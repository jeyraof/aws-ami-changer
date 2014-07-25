# -*- coding: utf-8 -*-

import json
import click
from ami_changer import utils
from ami_changer.autoscaling import (LaunchConfigurationManager, AmazonMachineImagesManager, )


class Processor(object):
    def __init__(self, connection, config_file, dry_run=False):
        self.connection = connection
        self._config = json.loads(config_file.read())
        self._as_manager = connection.auto_scaling()
        self._ec2_conn = connection.ec2_connection()
        self.dry_run = dry_run
        self.groups = utils.get_group_name_list(self._config)  # list for loop
        self.step = 0
        self.result_box = {}

    def next(self):
        return getattr(self, 'step_%s' % self.step, self.last_check).__call__()

    def step_1(self):
        # Get Auto-scaling Group
        self.result_box['as_group_name'] = self.groups.pop()
        utils.print_arrow(u'Get Auto-scaling group:: "%s"' % self.result_box['as_group_name'])

        self.result_box['as_group'] = self._as_manager.get_auto_scaling_group_by(name=self.result_box['as_group_name'])
        utils.print_arrow(u'Auto-scaling group "%s" was loaded.' % self.result_box['as_group_name'])

        # Get current launch configuration (lc) from auto-scaling group.
        self.result_box['lc'] = self._as_manager.get_launch_configuration_by(
            name=self.result_box['as_group'].launch_config_name)
        utils.print_arrow(u'Launch Configuration "%s" was loaded.' % self.result_box['lc'].name)

        # Make launch_configuration Manager
        self.result_box['lc_manager'] = LaunchConfigurationManager(lc=self.result_box['lc'],
                                                                   connection=self._as_manager.connection)
        utils.print_arrow(u'Launch Configuration Manager generated.')

    def step_2(self):
        self.result_box['ami_manager'] = AmazonMachineImagesManager(lc_manager=self.result_box['lc_manager'],
                                                                    connection=self._ec2_conn)
        utils.print_arrow(u'AMI manager was generated.')

        start_script_path = utils.get_config_by_group_name(config_dict=self._config,
                                                           group_name=self.result_box['as_group_name'],
                                                           key='start_script_path',
                                                           default=None)
        utils.print_arrow(u'Start script file loaded. Path: %s' % start_script_path)
        self.result_box['ami_manager'].launch_instance(start_script_path=start_script_path,
                                                       dry_run=self.dry_run,
                                                       )
        utils.print_arrow(u'Temporary instance launch command sent. Image_id: %s' % self.result_box['lc'].image_id)

        self.result_box['launched_instance'] = self.result_box['ami_manager'].get_launched_instance()
        utils.print_arrow(u'Reservation\'s information were loaded.')

        # Waiting for running status of launched instance
        indicator = utils.Indicator(message='Running instance...')
        while not self.result_box['launched_instance'].state_code is 16:
            indicator.next()
            self.result_box['launched_instance'] = self.result_box['ami_manager'].get_launched_instance()
        print
        utils.print_arrow(u'Instance is in running state! Instance_id: %s' % self.result_box['launched_instance'].id)

    def step_3(self):
        image_prefix = utils.get_config_by_group_name(config_dict=self._config,
                                                      group_name=self.result_box['as_group_name'],
                                                      key='ami_name_prefix',
                                                      default='ami_changer_')
        self.result_box['image_id'] = self.result_box['ami_manager'].create_image(prefix=image_prefix)
        utils.print_arrow(u'AMI generating command was sent.')

        self.result_box['new_image'] = self.result_box['ami_manager'].get_image_by(self.result_box['image_id'])
        utils.print_arrow(u'AMI generating is on pending.')

        indicator = utils.Indicator(message='Creating AMI...')
        while not self.result_box['new_image'].state == 'available':
            indicator.next()
            self.result_box['new_image'] = self.result_box['ami_manager'].get_image_by(self.result_box['image_id'])
        utils.print_arrow(u'AMI was available! New_AMI_id: %s' % self.result_box['image_id'])

    def step_4(self):
        lc_template = utils.get_config_by_group_name(config_dict=self._config,
                                                     group_name=self.result_box['as_group_name'],
                                                     key='launch_configuration_template',
                                                     default={})
        utils.print_arrow(u'LC Template loaded from configure file.')

        self.result_box['new_lc_temp'] = self.result_box['lc_manager'].\
            clone_by_template(image_id=self.result_box['image_id'], template=lc_template)
        utils.print_arrow(u'Renewal LC was cloned to new using template.')

        lc_created_flag = self.result_box['lc_manager'].\
            create_renewal_launch_configuration(renewal_lc=self.result_box['new_lc_temp'])
        if not lc_created_flag:
            self.roll_back(message='Can\'t generate launch configuration. Are you want to roll back?')
        utils.print_arrow(u'Renewal LC was created.')

    def step_5(self):
        self.result_box['as_group'].launch_config = self.result_box['new_lc_temp'].name
        utils.print_arrow(u'Renewal LC was applied to Auto-scaling group.')

        self.result_box['as_group'].update()
        utils.print_arrow(u'Save Auto-scaling group.')

    def step_6(self):
        self.result_box['launched_instance'].terminate()
        utils.print_arrow(u'Temporary launched instance was terminated.')

    def initialize(self):
        self.step = 0
        self.result_box = {}

    def last_check(self):
        if self.groups:
            self.initialize()
        else:
            self.terminate()

    @staticmethod
    def terminate():
        exit(0)

    def roll_back(self, message='[Error!] Are you want to roll back process?'):
        if click.confirm(message, default=False):
            # If Step3 finished completely.
            if 'launched_instance' in self.result_box and click.confirm('message'):
                self.result_box['launched_instance'].terminate()
                utils.print_arrow(u'Launched instance was terminated.')

            if 'new_image' in self.result_box:
                self.result_box['ami_manager'].delete_image_by(self.result_box['image_id'])
                utils.print_arrow(u'New AMI was deleted.')

            utils.print_arrow(u'Rollback Complete!')
        self.terminate()

    def get_messages(self):
        self.step += 1
        return u'\n ' + {
            1: u'1. Load Auto-scaling group and information about it from AWS.',
            2: u'2. Launch temporary machine to create new image.',
            3: u'3. Create AMI and delete temporary instance.',
            4: u'4. Create new Launch Configuration via template.',
            5: u'5. Apply new LC to current Auto-scaling group.',
            6: u'6. Tear down process (delete existing and etc.)'
        }.get(self.step, u' No more process to do in this context.\nCheck if more group is on config?')
