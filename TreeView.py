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
import subprocess

from sys import stdin

from Mod_TKUtil import show_object

input_data = {}
input_file_str = ''
input_file = None

if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('file', nargs='?', help='file-with-data.json')
    args = vars(parser.parse_args())

    # First - figure out what file we are loading data from, and populate "input_data"
    try:
        b_has_stdin = select.select([sys.stdin, ], [], [], 0.0)[0]  # check if any data in stdin
        if not args['file']:
            if b_has_stdin:
                # we have data at stdin, lets try to load it
                str_stdin = ''
                for line in stdin:
                    str_stdin += line
                input_data = json.loads(str_stdin)
                input_file_str = '(from stdin)'
                print('TreeView: loaded data from stdin')
            else:
                # no data in stdin
                # if no --file or -f argument given, and no stdin, then lets try a popup dialog, then re-execute ourselves WITH the --file argument!
                print('no stdin or filename, showing filedialog')
                input_file_str = tkinter.filedialog.askopenfilename(
                    title='Select data-file.json', filetypes=(("JSON files", "*.json"),))
                # note: sys.executable only works when it is compiled, because it resolves to the binary
                if input_file_str:
                    print('TreeView: re-execing with file: %s', input_file_str)
                    new_process = subprocess.Popen(
                        [sys.executable, input_file_str])
                    new_process.wait()
                else:
                    print('TreeView: no input file selected!')
                sys.exit(0)  # we are done here

        else:
            input_file_str = args['file']
            # normalize to absolute path
            input_file = pathlib.Path(input_file_str).resolve()
            input_file_str = str(input_file)
            print(f'reading data from file: {input_file_str}')
            if not input_file.is_file():
                raise Exception('File not found!')
            # Next - read the file data into a dictionary
            if input_file.is_file():
                with open(input_file_str, 'r', encoding='utf-8') as ifhan:
                    input_data = json.load(ifhan)
            else:
                print(f'error: file [{input_file_str}] not found!')
                sys.exit()
    except Exception as ex:
        print('something went wrong: %s', ex)
        traceback.print_exc()
        sys.exit()

    # Finally - show a dialog with a treeview and the data
    try:
        show_object(input_data, input_file_str)
    except Exception as ex:
        print('exception: %s', ex)

    print('TreeView: Exited.')
