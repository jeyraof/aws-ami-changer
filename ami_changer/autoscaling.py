# -*- coding: utf-8 -*-


class AutoScalingManager(object):
    def __init__(self, connection):
        self.connection = connection  # boto.ec2.autoscale.AutoScaleConnection

    def get_auto_scaling_group_by(self, name):
        group = self.connection.get_all_groups(names=[name])
        if group:
            return group[0]
        return None