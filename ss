#!/usr/bin/env python

import click, src.main

@click.command()
@click.option('-fos', type=click.Choice(['general', 'bishop']), help="Calculates Factor of Saftey.")
@click.argument('config')
@click.argument('data')

def main(fos, config, data):
    """
    Usage:

    ss -fos=[general|bishop] [config_file] [data_file]
    """
    src.main.fos(fos, config, data)

if __name__ == '__main__':
    main()
