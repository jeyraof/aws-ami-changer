# -*- coding: utf-8 -*-

from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.blockdevicemapping import BlockDeviceMapping, BlockDeviceType
from datetime import datetime
import utils


class AutoScalingManager(object):
    def __init__(self, connection):
        self.connection = connection  # boto.ec2.autoscale.AutoScaleConnection

    def get_auto_scaling_group_by(self, name):
        group = self.connection.get_all_groups(names=[name])
        if group:
            return group[0]
        return None

    def get_launch_configuration_by(self, name):
        launch_configuration = self.connection.get_all_launch_configurations(names=[name])
        if launch_configuration:
            return launch_configuration[0]
        else:
            return None


class LaunchConfigurationManager(object):
    def __init__(self, lc, connection):
        if lc:
            self.lc = lc
            self.block_device_mappings = BlockDeviceManager(lc=self.lc).get_block_device_mapping()  # block device
            self.connection = connection

    def clone_by_template(self, image_id, template):
        # image id
        template[u'image_id'] = image_id

        # ami name
        today_string = datetime.now().replace(microsecond=0).strftime(u'%Y%m%d_%H%M%S')
        template[u'name'] = template.get(u'name_prefix', self.lc.name + u'-') + today_string
        del template[u'name_prefix']

        # Cannot deepcopy LaunchConfiguration Model
        renewal_lc = LaunchConfiguration(instance_type=self.lc.instance_type,
                                         block_device_mappings=self.block_device_mappings,
                                         key_name=self.lc.key_name,
                                         security_groups=self.lc.security_groups,
                                         image_id=image_id,
                                         ramdisk_id=self.lc.ramdisk_id,
                                         kernel_id=self.lc.kernel_id,
                                         user_data=self.lc.user_data,
                                         instance_monitoring=self.lc.instance_monitoring,
                                         spot_price=self.lc.spot_price,
                                         instance_profile_name=self.lc.instance_profile_name,
                                         ebs_optimized=self.lc.ebs_optimized,
                                         associate_public_ip_address=self.lc.associate_public_ip_address,
                                         volume_type=self.lc.volume_type,
                                         delete_on_termination=self.lc.delete_on_termination,
                                         iops=self.lc.iops,
                                         use_block_device_types=self.lc.use_block_device_types,
                                         )

        renewal_lc = utils.overwrite_launch_configuration(renewal_lc, template)

        return renewal_lc

    def create_renewal_launch_configuration(self, renewal_lc):
        try:
            self.connection.create_launch_configuration(renewal_lc)
            return True
        except Exception as inst:
            print inst
            return False


class AmazonMachineImagesManager(object):
    def __init__(self, lc_manager, connection):
        self.lc_manager = lc_manager
        self.lc = lc_manager.lc
        self.connection = connection
        self.reservation = None

    def launch_instance(self):
        self.reservation = self.connection.run_instances(image_id=self.lc.image_id,
                                                         key_name=self.lc.key_name,
                                                         instance_type=self.lc.instance_type,
                                                         security_groups=self.lc.security_groups,
                                                         user_data=self.lc.user_data,
                                                         block_device_map=self.lc_manager.block_device_mappings[0])


class BlockDeviceManager(object):
    def __init__(self, lc):
        self._block_device_mappings = lc.block_device_mappings
        self.block_device_mappings = []

        for block_device_mapping in self._block_device_mappings:
            new_block_device_mapping = BlockDeviceMapping()

            ebs = block_device_mapping.ebs
            new_ebs_block_device_type = BlockDeviceType(size=ebs.volume_size,
                                                        snapshot_id=ebs.snapshot_id,
                                                        )

            new_block_device_mapping[block_device_mapping.device_name] = new_ebs_block_device_type

            self.block_device_mappings.append(new_block_device_mapping)

    def get_block_device_mapping(self):
        return self.block_device_mappings