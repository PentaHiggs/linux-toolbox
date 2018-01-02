#!/usr/bin/env python3

import argparse
import json
import os.path
import os
import sys
import imp

from typing import List, Any

PATH_TO_i3config = "~/.config/i3/config"
PATH_TO_THIS = "/usr/local/bin/i3wm_timer.py"


def set_i3config() -> None:
    """ Makes i3wm use this script. """

    with open(PATH_TO_i3config, 'r+') as f:
        lines = f.readlines()

        # Start writing from the beginning
        f.seek(0)
        f.truncate()

        at_bar = False
        for line in lines:
            if at_bar:
                line = line.append(" | " + PATH_TO_THIS + " --i3wm")
                at_bar = False
            elif line == "bar {":
                at_bar = True
            f.write(line)


def read_line() -> None:
    try:
        line = sys.stdin.readline().strip()
        if not line:
            sys.exit(3)
        return line

    except KeyboardInterrupt:
        sys.exit()


def bufferfree_print(line) -> None:
    sys.stdout.write(line + '\n')
    sys.stdout.flush()


def init_modules(pathname: str) -> List[Any]:
    """ Loads python classes from scripts from given directory """
    if not os.path.isabs(pathname):
        pathname = os.path.join(os.environ['HOME'], pathname)

        if not os.path.exists(pathname) or not os.path.isdir(pathname):
            return []

        else:
            filename_list = []
            for (dirpath, dirnames, filenames) in os.walk(pathname):
                filename_list.extend(filenames)

            modules = []
            for filename in filename_list:
                try:
                    with open(filename) as f:
                        # TODO: change this to use importlib instead.
                        modules.append(imp.load_module(
                            os.path.splittext(filename)[0],  # module name
                            f,  # file
                            pathname,  # pathname
                            "dummy_description",  # description
                        ))
                except ImportError:
                    pass

            # TODO: this should be in a try, except block.
            return [module.runner() for module in modules]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set a timer.")
    parser.add_argument('-d', '--directory', help='set scripts directory',
                        default='/usr/local/bin/i3wm_scripts/')
    parser.add_argument('-i', '--i3wm', help='not for use by end-user', action="store_true")
    args = parser.parse_args()

    if args.i3wm:
        # Start up the scripts, run their runner.__init__()'s
        runners = init_modules(args.directory)

        # Simply echo version number.
        bufferfree_print(read_line())

        # Also pass-through array
        bufferfree_print(read_line())

        while True:
            # TODO: Should check if scripts have been changed since start
            line, prefix = read_line(), ''

            if line.startswith(','):
                    line, prefix = line[1:], ','

            j = json.loads(line)
            for i, runner in enumerate(runners):
                j.insert(i, runner.produce_json())

            bufferfree_print(prefix + json.dumps(j))
