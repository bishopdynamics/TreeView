#!/usr/bin/env python3

# TreeView

# Created 2022 by James Bishop (james@bishopdynamics.com)

import argparse
import pathlib
import traceback
import json
import select
import sys
import tkinter
import tkinter.filedialog

from sys import stdin

from Mod_TKUtil import show_object

# print some extra information if True
DEBUG_MODE = False



def check_stdin():
    """ check stdin for data, return it or None
    """
    data = None
    has_data = select.select([sys.stdin, ], [], [], 0.0)[0]  # check if any data in stdin
    if has_data:
        # we have data at stdin, lets see if its empty
        data = ''
        for line in stdin:
            data += line
        if data.strip() == '':
            data = None
    return data

def read_file(filepath):
    # read a file and return its data
    print(f'Reading data from file: {filepath}')
    filepath_absolute = pathlib.Path(filepath).resolve()
    file_data = None
    if filepath_absolute.is_file():
        # TODO detect json lines, and load as list of dicts
        with open(filepath_absolute, 'r', encoding='utf-8') as ifhan:
            file_data = json.load(ifhan)
    else:
        raise FileNotFoundError
    return file_data

if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser(description='TreeView - A simple utility for macOS to load json data from stdin or a file and render a nice interactive treeview to explore it')
    parser.add_argument('file', nargs='?', help='file-with-data.json')
    try:
        input_data = None
        input_file_str = None
        input_file = None
        args = vars(parser.parse_args())
        # if there is no file argument, first we check stdin
        if not args['file']:
            # no file argument, check stdin
            data_from_stdin = check_stdin()
            if data_from_stdin:
                input_data = json.loads(data_from_stdin)
                input_file_str = '(from stdin)'
                print('Loaded data from stdin')
        # if we still dont have input_data:
        if not args['file'] and not input_data:
            # no data in stdin and no file
            # if no argument given, and no stdin, then lets try a popup dialog to pick a file
            print('no stdin or filename, showing filedialog')
            input_file_str = tkinter.filedialog.askopenfilename(title='Select data-file.json', filetypes=(("JSON files", "*.json"),))
            if input_file_str:
                # user picked a file
                input_data = read_file(input_file_str)
            else:
                # user must have hit Cancel, because no file was selected, lets check if we have late stdin
                data_from_stdin = check_stdin()
                if data_from_stdin:
                    # we NOW have data at stdin, lets try to load it
                    input_data = json.loads(data_from_stdin)
                    input_file_str = '(from stdin)'
                    print('No data file selected, but found late data on stdin')
                else:
                    # no file selected (must have hit Cancel), and nothing from stdin
                    print('No data file selected!')
                    sys.exit(0)  # we are done here
        if args['file']:
            # have a file arg, so ignore stdin
            input_file_str = args['file']
            input_data = read_file(args['file'])
        # Finally - show a dialog with a treeview using "input_data" and "input_file_str"
        show_object(input_data, input_file_str)
    except Exception as ex:
        print('Error: %s' % ex)
        if DEBUG_MODE:
            traceback.print_exc()
        sys.exit(1)
