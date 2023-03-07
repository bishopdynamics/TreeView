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
import sqlite3

from sys import stdin

import yaml
import pandas
import xmltodict

from Mod_TKUtil import show_object

# print some extra information if True
DEBUG_MODE = True



def check_stdin():
    """ check stdin for data, return it or None
    """
    data = None
    try:
        has_data = select.select([sys.stdin, ], [], [], 0.0)[0]  # check if any data in stdin
        if has_data:
            # we have data at stdin, lets see if its empty
            data = ''
            for line in stdin:
                data += line
            if data.strip() == '':
                data = None
    except OSError:
        # on Windows, lack of stdin data results in an OSError
        data = None
    return data

def read_file(filepath):
    # read a file and return its data
    #   checks file extension to assign a decoder
    print(f'Reading data from file: {filepath}')
    filepath_absolute = pathlib.Path(filepath).resolve()
    file_data = None
    if filepath_absolute.is_file():
        if filepath_absolute.suffix == '.json':
            # tryloading it as json
            # TODO detect json lines, and load as list of dicts
            if DEBUG_MODE:
                print('loading json file')
            with open(filepath_absolute, 'r', encoding='utf-8') as ifhan:
                file_data = json.load(ifhan)
        elif filepath_absolute.suffix in ['.yml', '.yaml']:
            # try loading it as yaml
            if DEBUG_MODE:
                print('loading yaml file')
            with open(filepath_absolute, 'r', encoding='utf-8') as ifhan:
                # NOTE yaml.load is deprecated. always use safe_load
                file_data = yaml.safe_load(ifhan)
        elif filepath_absolute.suffix == '.xml' :
            # try loading it as xml
            if DEBUG_MODE:
                print('loading xml file')
            with open(filepath_absolute, 'r', encoding='utf-8') as ifhan:
                file_content = ifhan.read()
            file_data = xmltodict.parse(file_content)
        elif filepath_absolute.suffix in ['.csv', '.tsv', '.xlsx', '.xls', '.ods', '.db', '.sqlite', '.sqlite3']:
            # lets try decoding this with pandas
            # first try to read into dataframe
            dataframes = []  # store dataframes
            dataframe_names = []  # store dataframe names
            if filepath_absolute.suffix == '.csv':
                attempt_data = None
                try:
                    attempt_data = pandas.read_csv(filepath_absolute, encoding='utf-8')
                except UnicodeDecodeError:
                    print('re-trying with latin/cp1252/ISO-8859-1 encoding')
                    attempt_data = pandas.read_csv(filepath_absolute, encoding='latin')
                dataframes.append(attempt_data)
                dataframe_names.append('default')
            elif filepath_absolute.suffix == '.tsv':
                attempt_data = None
                try:
                    attempt_data = pandas.read_csv(filepath_absolute, sep='\t', encoding='utf-8')
                except UnicodeDecodeError:
                    print('re-trying with latin/cp1252/ISO-8859-1 encoding')
                    attempt_data = pandas.read_csv(filepath_absolute, sep='\t', encoding='latin')
                dataframes.append(attempt_data)
                dataframe_names.append('default')
            elif filepath_absolute.suffix in ['.xlsx', '.xls', '.ods']:
                # old xls, new xlsx, and openoffice ods formats
                xlfile = pandas.ExcelFile(filepath_absolute)
                # load all sheets
                if DEBUG_MODE:
                    print(f'Reading data from {len(xlfile.sheet_names)} sheets')
                for this_sheet in xlfile.sheet_names:
                    dataframes.append(pandas.read_excel(filepath_absolute, sheet_name=this_sheet))
                    dataframe_names.append(this_sheet)
            elif filepath_absolute.suffix in ['.db', '.sqlite', '.sqlite3']:
                # try to read sqlite db
                if DEBUG_MODE:
                    print(f'Treating as sqlite3 database: {filepath_absolute.suffix}')
                db_conn = sqlite3.connect(filepath_absolute)
                cursor = db_conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables_raw = cursor.fetchall()
                tables_list = []
                for entry in tables_raw:
                    tables_list.append(entry[0])
                # load all tables
                if DEBUG_MODE:
                    print(f'Reading data from {len(tables_list)} tables')
                for this_table in tables_list:
                    dataframes.append(pandas.read_sql_query(f"SELECT * FROM {this_table};", db_conn))
                    dataframe_names.append(this_table)
                db_conn.close()
            # now convert dataframe into a vanilla dictionary
            file_data = {}
            for (index, df_name) in enumerate(dataframe_names):
                # turn into json first, which takes care of any serialization issues
                frame_json = dataframes[index].to_json(orient='records')
                file_data[df_name] = json.loads(frame_json)
            # print(json.dumps(file_data, indent=4))
        else:
            raise Exception(f'Unsupported file extension: {filepath_absolute.suffix}')
    else:
        raise FileNotFoundError
    return file_data

def read_data(data):
    # read the given data and return a tuple: (object, description)
    #   Tries to parse as json, then yaml
    try:
        data_obj = json.loads(data)
        data_str = '(from stdin, json)'
        if DEBUG_MODE:
            print('successfully parsed data as json')
    except ValueError:
        if DEBUG_MODE:
            print('failed to parse data as json, trying yaml')
        try:
            data_obj = yaml.safe_load(data)
            data_str = '(from stdin, yaml)'
            if DEBUG_MODE:
                print('successfully parsed data as yaml')
        except ValueError:
            data_obj = None
            data_str = None
    return (data_obj, data_str)

if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser(description='TreeView - A simple utility for macOS to load json data from stdin or a file and render a nice interactive treeview to explore it')
    parser.add_argument('file', nargs='?', help='file-with-data.{json|yml|yaml}')
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
                (input_data, input_file_str) = read_data(data_from_stdin)
                print('Loaded data from stdin')
        # if we still dont have input_data:
        if not args['file'] and not input_data:
            # no data in stdin and no file
            # if no argument given, and no stdin, then lets try a popup dialog to pick a file
            print('no stdin or filename, showing filedialog')
            input_file_str = tkinter.filedialog.askopenfilename(title='Select a datafile (json/yaml)', filetypes=(("JSON files", "*.json"),("YAML files", "*.yaml"),("YML files", "*.yml")))
            if input_file_str:
                # user picked a file
                input_data = read_file(input_file_str)
            else:
                # user must have hit Cancel, because no file was selected, lets check if we have late stdin
                data_from_stdin = check_stdin()
                if data_from_stdin:
                    # we NOW have data at stdin, lets try to load it
                    (input_data, input_file_str) = read_data(data_from_stdin)
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
