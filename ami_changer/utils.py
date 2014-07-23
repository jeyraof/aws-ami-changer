# -*- coding: utf-8 -*-


def get_group_name_list(config_dict):
    group_list = config_dict.get('auto-scaling-groups', [])
    return [group.get('name', '') for group in group_list]