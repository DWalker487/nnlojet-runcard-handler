import os
import shutil
import split_utils


def do_deploy(args):
    files = split_utils.get_split_files(args)
    copy_files(split_utils.get_split_files(args), 
               args.configdata["Deployment"]["DEPLOY_LOCATION"],args)


def undo_deploy(args):
    files = split_utils.get_split_files(args)
    rm_files(split_utils.get_split_files(args), 
               args.configdata["Deployment"]["DEPLOY_LOCATION"],args)


def get_deployed_name(griddir, infile):
    return os.path.join(griddir, os.path.basename(infile))


def rm_files(infiles, griddir,args):
    for infile in infiles:
        outfile = get_deployed_name(griddir, infile)
        args.logger.info("Removing {1}".format(infile, os.path.relpath(outfile)))
        os.remove(outfile)


def copy_files(infiles, griddir,args):
    for infile in infiles:
        outfile = get_deployed_name(griddir, infile)
        args.logger.info("Deploying {0} to {1}".format(infile, os.path.relpath(outfile)))
        shutil.copyfile(infile, outfile)
