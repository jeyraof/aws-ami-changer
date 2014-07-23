# -*- coding: utf-8 -*-
#!/usr/bin/env python

import click

from ami_changer.connector import Connection
from ami_changer.process import Processor


@click.command()
@click.argument('config_file', type=click.File('r'))
def main(config_file):
    """
    AMI Change Process
    """
    conn = Connection()
    auto_scaling_manager = conn.auto_scaling()
    processor = Processor(auto_scaling_manager=auto_scaling_manager,
                          config_file=config_file)

    processor.do()  # profit!


if __name__ == '__main__':
    main()