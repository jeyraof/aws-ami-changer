# -*- coding: utf-8 -*-

import json
from ami_changer import utils
from ami_changer.autoscaling import LaunchConfigurationManager


class Processor(object):
    def __init__(self, connection, config_file):
        self.connection = connection
        self._config = json.loads(config_file.read())
        self._as_manager = connection.auto_scaling()
        self._ec2_conn = connection.ec2_connection()
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
        # TODO: Launch temporary instance using current ami to fetching data.
        # self._ec2_conn.run_instances(image_id=lc.image_id,
        #                              key_name=lc.key_name,
        #                              instance_type=lc.instance_type,
        #                              security_groups=lc.security_groups,
        #                              user_data=lc.user_data,
        #                              block_device_map=lc_manager.block_device_mappings[0])
        self.result_box['image_id'] = u'ami-9d82d09c'

    def step_3(self):
        # TODO: Create Image and delete temporary instance.
        pass

    def step_4(self):
        lc_template = utils.get_lc_template_by_group_name(self._config, self.result_box['as_group_name'])
        utils.print_arrow(u'LC Template loaded from configure file.')

        self.result_box['new_lc_temp'] = self.result_box['lc_manager'].\
            clone_by_template(image_id=self.result_box['image_id'], template=lc_template)
        utils.print_arrow(u'Renewal LC was cloned to new using template.')

        lc_created_flag = self.result_box['lc_manager'].\
            create_renewal_launch_configuration(renewal_lc=self.result_box['new_lc_temp'])
        utils.print_arrow(u'Renewal LC was created!')

    def step_5(self):
        # TODO: Apply created LC to Group
        pass

    def step_6(self):
        # TODO: Tear down
        pass

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
