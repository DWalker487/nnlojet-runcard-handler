import json
import os
import sys

def do_split(args):
    for comp in get_split_components(args):
        args.logger.debug("{0}".format(comp.info))
        fname = comp.write_split_file(args.configdata,args.logger, args.skip_checks)
        args.logger.info("Writing file: {0}".format(fname))
        if args.git:
            os.system("git add {0}".format(fname))
    if args.git and args.commit:
        name = args.configdata["General"]["NAME"]
        directory = args.configdata["General"]["OUTPUT_DIRECTORY"]
        os.system("git commit -m \"Added {0} runcards to {1} dir in repo\"".format(name, 
                                                                               directory))


def undo_split(args):
    for comp in get_split_components(args):
        fname = comp.get_filename(args.configdata)
        args.logger.info("Removing file: {0}".format(fname))
        os.remove(fname)
        if args.git:
            os.system("git reset HEAD {0}".format(fname))

def write_dict(args):
    return ["dictCard = {\n"] +["   \"{0}\":\"{1}\",\n".format(
            os.path.basename(comp.get_filename(args.configdata)),
            args.configdata["General"]["NAME"])
                                for comp in get_split_components(args)]+["}\n"]


def gen_grid_runcard(args):
    out_lines = write_dict(args)

    for attr in args.configdata["Grid Runcard"]:
        if "RUNCARD_FILE" and "TEMPLATE_RUNCARD_FILE" not in attr:
            out_lines.append("{0} = \"{1}\"\n".format(attr,args.configdata["Grid Runcard"][attr]))

    with open(args.configdata["Grid Runcard"]["TEMPLATE_RUNCARD_FILE"]) as tmp:
        for line in tmp.readlines():
            if line.startswith("#"):
                out_lines.append(line)

    outfile = args.configdata["Grid Runcard"]["RUNCARD_FILE"]
    args.logger.debug("".join(out_lines))
    args.logger.info("Writing grid file to {0}".format(outfile))
    with open(outfile,"w") as rcfile:
        rcfile.writelines(out_lines)


def get_override(args, channel):
    override = args.configdata[channel]
    for key, value in override.items():
        override[key.lower()]=value
        override[key.upper()]=value
    try:
        override["channel"]=override["CHANNEL"]
    except Exception as e:
        pass
    try:
        override["chan"]=override["CHAN"]
    except Exception as e:
        pass
    return override


def get_perm(indict,list_of_dicts,idx=0, keys= None):
    """ Recursive function to generate all permutations of runcard dictionaries
    and save them to list_of_dicts"""
    if keys is None:
        keys = list(indict.keys())
    no_lists = True
    for idx, key in enumerate(keys[idx:]):
        val = indict[key]
        origval = val
        try:
            val = get_config_list(val)
        except (TypeError,ValueError) as e:
            pass
        if type(val)==list:
            no_lists = False
            for a in val:
                indict[key]=a
                get_perm(indict,list_of_dicts, idx=idx, keys = keys)
            indict[key] = origval
            return 
    if no_lists:
        list_of_dicts.append(indict.copy())


def get_split_components(args):
    channels = get_config_list(args.configdata.get("Splitting","CHANNELS"))
    templatefile = args.configdata.get("General","TEMPLATE_FILE")
    split_components = []
    for channel in channels:
        indict = {}
        indict.update(args.configdata["Default Split Info"])
        if args.configdata.has_section(channel):
            indict.update(get_override(args, channel))
        list_of_subcomponents = []
        get_perm(indict,list_of_subcomponents)
        for subcomp in list_of_subcomponents:
            split_components.append(SplitComponent(channel, templatefile,
                                                   subcomp))
    return split_components


def get_split_files(args):
    split_components = get_split_components(args)
    return [i.get_filename(args.configdata) for i in split_components]


def get_config_list(cfdata):
    return json.loads(cfdata)


class SplitComponent():
    def __init__(self,channel,template,info):
        self.info = {}
        self.templatefile = template
        self.info["channel"]=channel
        self.info["chan"]=channel
        self.info.update(info)
        if "RUNID_FMT" in info.keys() and "RUNID" not in info.keys():
            self.info["RUNID"] = self.info["RUNID_FMT"].format(**self.info)

        
    def get_filename(self,configdata):
        basedir = configdata.get("General", "OUTPUT_DIRECTORY")
        fname = configdata.get("General", "NAME_FMT").format(**self.info)
        return os.path.join(basedir,fname)


    def __format_tag(self,tag):
        out_tags = []
        for start,end in [["&","&"],["<",">"]]:
            out_tags.append("{0}{1}{2}".format(start,tag.upper(),end))
            out_tags.append("{0}{1}{2}".format(start,tag.lower(),end))
            out_tags.append("{0}{1}{2}".format(start,tag,end))
        return list(set(out_tags))


    def __update_line(self,string, replacement, line):
        return line.replace(string, str(replacement))


    def write_split_file(self, configdata, logger, skip_checks):
        with open(self.templatefile) as infile:
            template_lines = infile.readlines()
        newlines = []
        for line in template_lines:
            nline = line
            for tag in self.info:
                wrapped_tags = self.__format_tag(tag)
                for w_tag in wrapped_tags:
                    nline = self.__update_line(w_tag, self.info[tag], nline)
            newlines.append(nline)

        outfilename = self.get_filename(configdata)
        if os.path.isfile(outfilename) and not skip_checks:
            ok = input("File {0} already exists. Overwrite [y/n]?    ".format(outfilename))# Do check with user
            if not ok[0].upper() =="Y":                
                logger.info("Skipping {0}".format(outfilename))
                return outfilename
        with open(outfilename,"w") as outfile:
            outfile.writelines(newlines)
        return outfilename
