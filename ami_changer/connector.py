# -*- coding: utf-8 -*-

import os
import sys

from boto.ec2 import autoscale, connect_to_region
from ami_changer.autoscaling import AutoScalingManager


class Connection(object):
    def __init__(self):
        self._aws_access_key = os.environ.get('AWS_ACCESS_KEY', None)
        self._aws_secret_key = os.environ.get('AWS_SECRET_KEY', None)
        self._aws_region = os.environ.get('AWS_REGION', 'ap-northeast-1')

        if None in [self._aws_access_key, self._aws_secret_key]:
            raise NoEnvironmentSetExcept

    def auto_scaling(self):
        auto_scaling_connection = autoscale.connect_to_region(self._aws_region,
                                                              aws_access_key_id=self._aws_access_key,
                                                              aws_secret_access_key=self._aws_secret_key)
        return AutoScalingManager(connection=auto_scaling_connection)

    def ec2_connection(self):
        return connect_to_region(self._aws_region,
                                 aws_access_key_id=self._aws_access_key,
                                 aws_secret_access_key=self._aws_secret_key)


class NoEnvironmentSetExcept(Exception):
    def __init__(self):
        print
        print u'\033[95m Environment variable should be set. \033[0m'
        print u' : AWS_ACCESS_KEY \033[91m (* required) \033[0m'
        print u' : AWS_SECRET_KEY \033[91m (* required) \033[0m'
        print u' : AWS_REGION      (optional,\033[93m default: "ap-northeast-1"\033[0m)'
        print
        sys.exit(0)