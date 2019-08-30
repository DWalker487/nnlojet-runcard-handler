#!/usr/bin/env python3
import configparser
import logging
import argparse as ap
from deploy_utils import do_deploy, undo_deploy
from split_utils import do_split, undo_split, gen_grid_runcard, get_config_list
from collections import defaultdict
import os


def do_splitdeploy(*args):
    do_split(*args)
    do_deploy(*args)


modes = {
    "deploy":do_deploy,
    "split":do_split,
    "undeploy":undo_deploy,
    "unsplit":undo_split,
    "grid":gen_grid_runcard,
    "splitdeploy":do_splitdeploy

         }

def setup_logger(level):
    formatter = logging.Formatter(fmt='%(asctime)s %(message)s',
                                  datefmt="[%Y-%m-%d %H:%M:%S]")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger("root")
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def parse_args():
    parser = ap.ArgumentParser(
        description="A handler for splitting and deploying NNLOJET runcards.")
    parser.add_argument("mode",type=str, help="modes=[{0}]".format("/".join(modes.keys())))
    parser.add_argument("--config","-c","-C",type=str, 
                        help = "Config file", required=True)
    parser.add_argument("--loglevel","-l", help="logging info level", 
                        default="INFO",type=str)
    parser.add_argument("--git","-g", help="(remove) add file to git [(un)split mode only]", 
                        default=False,action="store_true")
    parser.add_argument("--skip_checks","-s", help="skip sanity checks/confirmations with user", 
                        default=False,action="store_true")
    parser.add_argument("--commit", 
                        help="commits file to repo if --git also enabled [split mode only]", 
                        default=False,action="store_true")
    args = parser.parse_args()
    args.logger = setup_logger(args.loglevel.upper())
    return args


def parse_config(args):
    cf = args.config
    parser = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation())
    parser.optionxform = str 
    args.logger.info("Config file: {0}".format(cf))
    parser.read(cf)
    for section in parser.sections():
        for (key, val) in parser.items(section):
            parser[section][key] = os.path.expanduser(parser[section][key])
    os.makedirs(parser["General"]["OUTPUT_DIRECTORY"], exist_ok=True)
    return parser

if __name__ == "__main__":
    args = parse_args()
    args.configdata = parse_config(args)
    args.logger.info("Mode: {0}".format(args.mode))
    modes[args.mode](args)
