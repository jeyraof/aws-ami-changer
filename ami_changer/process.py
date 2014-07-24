# -*- coding: utf-8 -*-

import json
from ami_changer import utils
from ami_changer.autoscaling import LaunchConfigurationManager


class Processor(object):
    def __init__(self, auto_scaling_manager, config_file):
        self._as_manager = auto_scaling_manager
        self._config = json.loads(config_file.read())

    def do(self):
        for as_group_name in utils.get_group_name_list(self._config):
            # 1. Get Auto-scaling group.
            as_group = self._as_manager.get_auto_scaling_group_by(name=as_group_name)

            # 2. Get current Launch configuration via auto-scaling group.
            lc = self._as_manager.get_launch_configuration_by(name=as_group.launch_config_name)
            lc_manager = LaunchConfigurationManager(lc=lc, connection=self._as_manager.connection)

            # TODO: 3. Launch temporary instance using current ami to fetching data.

            # TODO: 4. Create Image and delete temporary instance.
            image_id = u'ami-9d82d09c'

            # TODO: 5. After clone LC-object, overwrite arguments of imported data and Create using created AMI now.
            lc_template = utils.get_lc_template_by_group_name(self._config, as_group_name)
            renewal_lc = lc_manager.clone_by_template(image_id=image_id, template=lc_template)

            # print lc.block_device_mappings[0].__dict__.get('ebs').__dict__

            lc_created_flag = lc_manager.create_renewal_launch_configuration(renewal_lc=renewal_lc)
            print lc_created_flag

            # TODO: 6. Apply created LC to Group