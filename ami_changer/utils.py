# -*- coding: utf-8 -*-

def get_group_name_list(config_dict):
    group_list = config_dict.get('auto_scaling_groups', [])
    return [group.get('name', '') for group in group_list]


def get_lc_template_by_group_name(config_dict, group_name):
    group_list = config_dict.get('auto_scaling_groups', [])

    for group in group_list:
        if group.get('name', '') == group_name:
            return group.get('launch_configuration_template', {})
    return {}


def overwrite_launch_configuration(lc, template):
    for key, val in template.iteritems():
        setattr(lc, key, val)
    return lc