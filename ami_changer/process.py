# -*- coding: utf-8 -*-

import json
from ami_changer import utils


class Processor(object):
    def __init__(self, auto_scaling_manager, config_file):
        self._auto_scaling_manager = auto_scaling_manager
        self._config = json.loads(config_file.read())

    def do(self):
        for auto_scaling_group_name in utils.get_group_name_list(self._config):
            auto_scaling_group = self._auto_scaling_manager.get_auto_scaling_group_by(name=auto_scaling_group_name)

