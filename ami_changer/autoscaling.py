# -*- coding: utf-8 -*-

from boto.ec2.autoscale import LaunchConfiguration
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
            self.connection = connection

    def clone_by_template(self, image_id, template):
        template[u'image_id'] = image_id

        lc_name = template.get(u'name_prefix', self.lc.name + u'-') + datetime.now().strftime(u'%Y%m%d%H%M%S')
        template[u'name'] = lc_name
        del template[u'name_prefix']

        cloned_lc = utils.initialize_launch_configuration(self.lc)

        renewal_lc = utils.overwrite_launch_configuration(cloned_lc, template)

        return renewal_lc

    def create_renewal_launch_configuration(self, renewal_lc):
        try:
            self.connection.create_launch_configuration(renewal_lc)
            return True
        except Exception as inst:
            print inst
            return False


class AmazonMachineImageManager(object):
    pass