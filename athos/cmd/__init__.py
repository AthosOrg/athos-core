import argparse
import os

import athos
import yaml

def file_argument(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def main():
    # parse command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("config",
                        help="YAML config file",
                        type=lambda x: file_argument(parser, x))

    args = parser.parse_args()

    # parse the config file
    with open(args.config) as f:
        config = yaml.load(f)
        if config is None:
            config = {}

    # call the main function
    athos.main(config)
