# -*- coding: utf-8 -*-

import sys
import time
import base64
import codecs


def get_group_name_list(config_dict):
    group_list = config_dict.get('auto_scaling_groups', [])
    return [group.get('name', '') for group in group_list]


def get_config_by_group_name(config_dict, group_name, key, default=None):
    group_list = config_dict.get('auto_scaling_groups', [])

    for group in group_list:
        if group.get('name', '') == group_name:
            return group.get(key, default)
    return default


def overwrite_launch_configuration(lc, template):
    for key, val in template.iteritems():
        setattr(lc, key, val)
    return lc


def get_arrow(uni=True):
    arrow = u' \033[91m=>\033[0m '
    if uni:
        return arrow
    else:
        return str(arrow)


def print_logo():
    print
    print u' \n \033[95m[AMI Changer]\033[0m'


def print_arrow(text):
    print get_arrow() + text


def merge_string_from_file(text, path):
    extracted_text = ""
    try:
        with codecs.open(path, "r", "utf-8") as fp:
            extracted_text = fp.read()
    except Exception as inst:
        print inst

    return "\n".join([text, extracted_text])


def user_data_encode(data):
    return base64.b64encode(data)


class Indicator(object):
    def __init__(self, message='Processing...', interval=0.5):
        self.message = message
        self.prefix = '\r' + str(get_arrow(uni=False)) + '%s ' % self.message
        self.interval = interval
        self.stage = ''
        self.range = 0

    def next(self):
        time.sleep(self.interval)
        sys.stdout.write(self.prefix + self.stage + self.get_mark())
        sys.stdout.flush()

        self.range = (self.range + 1) % 5
        if self.range == 0:
            self.stage += '*'

    def get_mark(self):
        return {
            0: ' ',
            1: '|',
            2: '/',
            3: '-',
            4: '\\',
        }.get(self.range, '*')