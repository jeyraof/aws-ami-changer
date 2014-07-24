# -*- coding: utf-8 -*-
#!/usr/bin/env python

import click

from ami_changer.connector import Connection
from ami_changer.process import Processor
from ami_changer.utils import print_logo


@click.command()
@click.argument('config_file', type=click.File('r'))
def main(config_file):
    """
    AMI Change Process
    """
    processor = Processor(connection=Connection(),
                          config_file=config_file)

    print_logo()

    while click.confirm(processor.get_messages(), default=True):
        processor.next()

if __name__ == '__main__':
    main()