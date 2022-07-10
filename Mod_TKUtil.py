#!/usr/bin/env python3

# Tk Utility Module
#   Tk utility classes - abstraction layer on top of Tk, to simplify usage

# Created 2022 by James Bishop (james@bishopdynamics.com)

# UI Abstraction Layer
#   these classes provide an abstraction layer on top of the primitives provided by Tk
#   in our system, grid layout is mandatory, and we use 1-indexed col/row numbers
#   Tk has a single object "Treeview" which handles duties for both hierarchical and columnar data
#       our abstractions "TkTableView" and "TkTreeView" simplify usage for each,
#       including helper methods to load a list or dictionary, respectively

import uuid
import random
import json
import tkinter
import tkinter.ttk
import tkinter.filedialog
import traceback
import webbrowser

from typing import Literal

# from Mod_Util import print_obj

# NOTE padding for x and y are linked, but for now everything is default

DEFAULT_FONT_NAME = 'Andale Mono'  # chosen because monospace
DEFAULT_PADDING = 5  # pixels, if you dont provide padding=, then this is the default
DEFAULT_FONT_SMALL = (DEFAULT_FONT_NAME, 10)
DEFAULT_FONT = (DEFAULT_FONT_NAME, 12)  # used for almost everything by default
DEFAULT_FONT_MEDIUM = (DEFAULT_FONT_NAME, 16)
DEFAULT_FONT_LARGE = (DEFAULT_FONT_NAME, 24)

# TODO font licensing?

# Debugging: show colored borders around things for debugging
#   choose one or more from DEBUG_ELEMENT_LIST
DEBUG_ELEMENTS = []
DEBUG_ELEMENT_LIST = ['frame', 'label', 'spacer', 'button',
                      'checkbox', 'table', 'tree', 'progressbar', 'combobox', 'textentry']
# colors will be randomly chosen from here
DEBUG_COLORS = ['red', 'yellow', 'blue', 'white', 'pink']

# TODO add method to all ui widgets that we can call to change debug state
#   so that we can trigger changes from within ui (menubar, checks for each)
#   should move frame_wrapper to TkWidget, and add a method to set debug


def sanitize_name(product_name, separator: str = '-'):
    # lowercase, remove ()[]{}/\+ and replace spaces with separator
    new_product_name = product_name.strip().lower().replace('(', '').replace(')', '')
    new_product_name = new_product_name.replace('[', '').replace(']', '')
    new_product_name = new_product_name.replace('{', '').replace('}', '')
    new_product_name = new_product_name.replace('/', '').replace('\\', '').replace('+', '')
    new_product_name = new_product_name.replace(' ', separator)
    return new_product_name


def list_to_dict(input_list: list):
    # turn a list into a dict, with index + 1 as keys
    newdict = {}
    for (index, value) in enumerate(input_list):
        newdict[index] = value
    return newdict

# print a traceback
def print_traceback():
    print(traceback.format_exc())


# open a new browser tab with the given url
def open_browser(url: str):
    webbrowser.open_new_tab(url)


class TkWindow(tkinter.Tk):
    # give the basic window object some helpers

    def __init__(self, title: str = '',
                 width: int = 300, height: int = 300,
                 resizable: bool = True,
                 minwidth: int = 20, minheight: int = 20,
                 maxwidth: int = 65536, maxheight: int = 65536,
                 offset_x: int = 0, offset_y: int = 0):
        super().__init__()
        self.on_close_function = None
        try:
            # calculate a starting point, middle of screen
            self.startpoint_x = (self.winfo_screenwidth() /
                                 2) - (width / 2) + offset_x
            self.startpoint_y = (self.winfo_screenheight() /
                                 2) - (height / 2) + offset_y
            # set the title
            self.title(title)
            # make the window resizable
            self.wm_resizable(resizable, resizable)
            # setup sizing of the main window
            self.geometry('%dx%d+%d+%d' %
                          (width, height, self.startpoint_x, self.startpoint_y))
            self.minsize(width=minwidth, height=minheight)
            self.maxsize(width=maxwidth, height=maxheight)
            # style
            self.mystyle = tkinter.ttk.Style()
            self.mystyle.configure('Treeview', font=DEFAULT_FONT)
            self.mystyle.configure('Treeview.Heading', font=DEFAULT_FONT)
            # window is a 1x1 grid
            self.rowconfigure(0, weight=1)
            self.columnconfigure(0, weight=1)
            self.protocol("WM_DELETE_WINDOW", self.close)
        except Exception as ex:
            print('Error while initializing Window: %s' % ex)
            print_traceback()

    def close(self):
        # close this window
        self.destroy()


class TkWidget(tkinter.BaseWidget, tkinter.Grid):
    # this is the base class of our fancy little tk wrapper library
    #   adds explicit 1-indexed placement in parent grid, and unified default padding
    # pylint: disable=super-init-not-called
    def __init__(self, parent, parent_col: int, parent_row: int,
                 sticky='', padding: int = DEFAULT_PADDING,
                 ):
        tkinter.Grid.__init__(parent)
        if parent_col == 0:
            return  # skip setting up grid if no cols
        if parent_row == 0:
            return  # skip setting up grid if no rows
        self.grid(column=(parent_col - 1), row=(parent_row - 1),
                  sticky=sticky, padx=padding, pady=padding)


class TkFrame(tkinter.Frame, TkWidget):
    # a frame with extra controls
    #   cols/rows - configure the grid inside this frame
    #   spacecol/spacerow - set a col/row as a spacer which will expand and push away other elements in the col/row.
    #       in this case all other cols/rows will get weight 0, and this spacecol/spacerow will get weight 1
    #       otherwise all cols/rows get weight 1
    #   for auto-resizing to work as expected, you actually need more than one col/row, so in cases where a frame only has 1 of each, we add an extra
    def __init__(self, parent, parent_col: int, parent_row: int,
                 cols: int, rows: int,
                 spacecol: int = 0, spacerow: int = 0,
                 sticky='', padding: int = DEFAULT_PADDING,
                 width: int = None, height: int = None,):
        tkinter.Frame.__init__(self, parent)
        TkWidget.__init__(self, parent, parent_col=parent_col,
                          parent_row=parent_row, sticky=sticky, padding=padding)
        if 'frame' in DEBUG_ELEMENTS:
            border_color = random.choice(DEBUG_COLORS)
            self.config(highlightthickness=1, highlightcolor=border_color,
                        highlightbackground=border_color)
        # configure columns
        if cols > 0:
            if cols == 1:
                # minimum two columns for proper autoresize, so we just toss in an extra with zero weight
                self.columnconfigure(0, weight=1)
                self.columnconfigure(1, weight=0)
            else:
                for c in range(0, (cols - 1)):
                    if spacecol > 0:
                        if c == (spacecol - 1):
                            self.columnconfigure(c, weight=1)
                        else:
                            self.columnconfigure(c, weight=0)
                    else:
                        self.columnconfigure(c, weight=1)
        # configure rows
        if rows > 0:
            if rows == 1:
                # minimum two rows for proper autoresize, so we just toss in an extra with zero weight
                self.rowconfigure(0, weight=1)
                self.rowconfigure(1, weight=0)
            else:
                for r in range(0, (rows - 1)):
                    if spacerow > 0:
                        if r == (spacerow - 1):
                            self.rowconfigure(r, weight=1)
                        else:
                            self.rowconfigure(r, weight=0)
                    else:
                        self.rowconfigure(r, weight=1)
        # setup width/height
        if width:
            self.config(width=width)
        if height:
            self.config(height=height)


class TkLabel(tkinter.Label, TkWidget):
    # basic label, enhanced with word wrapping technology!
    def __init__(self, parent, parent_col: int, parent_row: int,
                 text: str, wraplength: int = None,
                 font: tuple = DEFAULT_FONT,
                 anchor: Literal['nw', 'n', 'ne', 'w',
                                 'center', 'e', 'sw', 's', 'se'] = 'center',
                 justify: Literal['left', 'center', 'right'] = 'center',
                 sticky='', padding: int = DEFAULT_PADDING,
                 width: int = None, height: int = None):
        if wraplength:
            tkinter.Label.__init__(self, parent, text=text, anchor=anchor,
                                   wraplength=wraplength, font=font, justify=justify)
        else:
            tkinter.Label.__init__(
                self, parent, text=text, anchor=anchor, font=font, justify=justify)
        TkWidget.__init__(self, parent, parent_col=parent_col,
                          parent_row=parent_row, sticky=sticky, padding=padding)
        if 'label' in DEBUG_ELEMENTS:
            border_color = random.choice(DEBUG_COLORS)
            self.config(highlightthickness=1, highlightcolor=border_color,
                        highlightbackground=border_color)
        # TODO this might be a way to do dynamic word wrap on labels
        # self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))
        # setup width/height
        if width:
            self.config(width=width)
        if height:
            self.config(height=height)


class TkButton(tkinter.Button, TkWidget):
    # a basic button, supplemented to make assigning callbacks easier
    def __init__(self, parent, parent_col: int, parent_row: int,
                 text: str,
                 state: Literal['normal', 'disabled', 'readonly'] = 'normal',
                 font: tuple = DEFAULT_FONT,
                 anchor: Literal['nw', 'n', 'ne', 'w',
                                 'center', 'e', 'sw', 's', 'se'] = 'center',
                 justify: Literal['left', 'center', 'right'] = 'center',
                 sticky='', padding: int = DEFAULT_PADDING,
                 ):
        tkinter.Button.__init__(
            self, parent, text=text, state=state, justify=justify, anchor=anchor, font=font)
        TkWidget.__init__(self, parent, parent_col=parent_col,
                          parent_row=parent_row, sticky=sticky, padding=padding)
        self.grid(column=(parent_col - 1), row=(parent_row - 1),
                  sticky=sticky, padx=padding, pady=padding)
        if 'button' in DEBUG_ELEMENTS:
            border_color = random.choice(DEBUG_COLORS)
            self.config(highlightthickness=1, highlightcolor=border_color,
                        highlightbackground=border_color)

    def on_click(self, callback: callable):
        # convenience method to assign callback
        self.config(command=callback)


class TkTreeView(tkinter.ttk.Treeview, TkWidget):
    # Supplement Tk Treeview with methods for loading data, expand all, collapse all
    #   display an arbitrary dictionary (of values that can convert to str)
    def __init__(self, parent, parent_col: int, parent_row: int, value: dict = None, sticky='', padding: int = DEFAULT_PADDING, show_units: bool = False, sort_keys: bool = True):
        self.frame_wrapper = TkFrame(
            parent, parent_col=parent_col, parent_row=parent_row, cols=1, rows=1, sticky=sticky, padding=padding)
        tkinter.ttk.Treeview.__init__(self, self.frame_wrapper)
        TkWidget.__init__(self, self.frame_wrapper, parent_col=1,
                          parent_row=1, sticky='nsew', padding=0)
        if 'treeview' in DEBUG_ELEMENTS:
            border_color = random.choice(DEBUG_COLORS)
            self.frame_wrapper.config(
                highlightthickness=1, highlightcolor=border_color, highlightbackground=border_color)
        self.tree_nodes = []  # track all nodes of the tree in a flat list, for iterating
        # copy of current data loaded into tree will be stored here for convenvient retrieval
        self.tree_data = {}
        # show units in nodes with children, such a: [2 keys]
        self.show_units = show_units
        self.sort_keys = sort_keys  # wether to sort dict keys
        column_widths = [100, 300, 0]
        column_headings = ['Key', 'Value', '']
        column_ids = ['#0', 'key', 'value']
        self.config(columns=['key', 'value'])  # column ids (other than '#0')
        for (index, col_id) in enumerate(column_ids):
            self.heading(col_id, anchor='w', text=column_headings[index])
            self.column(col_id, width=column_widths[index])
        if value is not None:
            self.load_dict(value)

    def insert_tree_node(self, node_data, parent: str = ''):
        # insert a node to the tree, as a child of the given parent
        #   this method is used recursively
        #   if data is a dict, we recursively process its keys and add nodes for them
        #   if data is a set, we turn it into a list
        #   if data is a list, we recursively process its entries and add nodes for them
        #   if data is a multiline string, we recursively process each line as if they were entries in a list
        #   NOTE: this method was lass blessed as "perfect" on July 10, 2022, 1:35pm PST. do not touch it
        if isinstance(node_data, type(set())):
            # turn set into list
            node_data = sorted(node_data)
        if isinstance(node_data, dict) and self.sort_keys:
            # sort dictionary keys
            node_data = dict(sorted(node_data.items()))
        # print(f'node data type: {type(node_data)}')
        # print_obj(node_data)
        index = 0  # index counter incase node_data is a list
        for key in node_data:
            # print(f'traversing key: {key}')
            # this way we can process node_data as a dict or a list
            try:
                # is a dict?
                value = node_data[key]
            except TypeError:
                # must be a list
                value = key
                key = str(index)
            uid = str(uuid.uuid4())
            self.tree_nodes.append(uid)
            if isinstance(value, type(set())):
                # turn any values of type set into list
                value = sorted(value)
            if isinstance(value, dict):
                if self.show_units:
                    key_name = f'{key} [dict] ({len(value.keys())} keys)'
                else:
                    key_name = f'{key} ({len(value.keys())})'
                self.insert(parent, 'end', uid, text=key_name)
                self.insert_tree_node(value, uid)
            elif isinstance(value, list):
                if len(value) == 0:
                    # turn empty lists into (empty)
                    if self.show_units:
                        self.insert(parent, 'end', uid, text=f'{key} [list] (0 items):', values=['(empty)'])
                    else:
                        self.insert(parent, 'end', uid, text=f'{key} (0):', values=['(empty)'])
                else:
                    list_as_dict = list_to_dict(value)
                    if self.show_units:
                        self.insert(parent, 'end', uid, text=f'{key} [list] ({len(list_as_dict)} items):')
                    else:
                        self.insert(parent, 'end', uid, text=f'{key} ({len(list_as_dict)}):')
                    self.insert_tree_node(list_as_dict, uid)
            else:
                # print(f'value of unknown type: {type(value)}')
                try:
                    if value is None:
                        # if value is empty, replace it with string 'None' to give something in the UI
                        value = 'None'
                    else:
                        if isinstance(value, str):
                            if len(value.splitlines()) > 1:
                                # this multiline string will look ugly in the treeview
                                #   lets turn it into an array of lines
                                value_as_lines = value.splitlines()
                                # we ended up with a list of lines, lets treat it like a list
                                if self.show_units:
                                    self.insert(parent, 'end', uid, text=f'{key} [text] ({len(value_as_lines)} lines): ')
                                else:
                                    self.insert(parent, 'end', uid, text=f'{key} ({len(value_as_lines)}): ')
                                self.insert_tree_node(list_to_dict(value_as_lines), uid)
                                continue  # otherwise tree.insert below will create a duplicate entry
                        else:
                            value = str(value)
                    # hopefully now we have a string, lets add it
                    # below, remember values needs to be an array in this context
                    self.insert(parent, 'end', uid, text=f'{key}', values=[value])
                except Exception as ex:
                    print(f'failed to insert value for key: {key}, error: {ex}')
                    continue
            index += 1  # increment our index counter
    def load_dict(self, input_dict: dict):
        # load a dictionary into the treeview
        try:
            self.clear_data()  # first clear out existing data
            # now populate it
            if input_dict is None:
                input_dict = {
                    'data': 'no data'
                }
            self.insert_tree_node(input_dict)
            self.tree_data = input_dict.copy()
        except Exception as ex:
            print('Error loading dict into TreeView: %s' % ex)
            print_traceback()

    def get_data(self):
        # helper method to get currently loaded data
        return self.tree_data

    def clear_data(self):
        # clear data from treeview
        self.tree_nodes = []  # clear our nodes list
        self.tree_data = {}  # clear stored copy of loaded data
        for item in self.get_children():  # delete all items in the treeview
            self.delete(item)

    def expand(self):
        # expand all items of treeview
        for item in self.tree_nodes:
            self.item(item, open=True)

    def collapse(self):
        # collapse all items of treeview
        for item in self.tree_nodes:
            self.item(item, open=False)


def show_object(this_object, object_name, show_units=True, sort_keys=False):
    # show a dialog with treeview populated by this object, used for debugging
    #   TODO this is blocking, so causes execution to stop wherever this was called
    new_obj = {
        'data': 'Failed to decode object'
    }
    try:
        # transform any list into dict because thats what growing trees need!
        if isinstance(this_object, list):
            this_object = list_to_dict(this_object)
        # if it can be json-encoded then we can turn it into a tree
        _string_object = json.dumps(this_object)
        new_obj = this_object
    except Exception:
        # not json encodable, lets try other options
        try:
            # maybe we can use __dict__ to get a better representation of this object
            _string_object = json.dumps(this_object.__dict__)
            new_obj = this_object.__dict__
        except Exception:
            # last-ditch effort, likely wont ever get here
            _string_object = json.dumps(str(this_object).splitlines())
            new_obj = str(this_object).splitlines()
    finally:
        # ok, now lets throw up a dialog with the object
        DialogTreeview('TreeView', summary='File: %s' % object_name, width=800,
                       height=500, resizable=True, focus_force=True, data=new_obj, show_units=show_units, sort_keys=sort_keys)


class DialogTreeview(object):
    # Generic Treeview Dialog
    #   if you provide data, it will be loaded into the treeview immediately
    def __init__(self, name: str, data: dict = None, summary: str = None, description: str = None,
                 height: int = 400, width: int = 300, resizable=False, focus_force=False, show_units: bool = False, sort_keys: bool = False):
        super().__init__()
        self.name = name
        self.data = data
        self.focus_force = focus_force
        self.button_expand = None
        self.button_collapse = None
        self.treeview_result = None
        self.progressbar = None
        self.label_status = None
        # print("Setting up the Generic Treeview Dialog")
        try:
            self.window = TkWindow(
                name, width=width, height=height, minwidth=200, minheight=300, resizable=resizable)
            # this is the overall window, the container of all containers
            frame_root = TkFrame(
                self.window, parent_col=1, parent_row=1, cols=1, rows=4, spacerow=2, sticky='nsew')
            frame_root.rowconfigure(0, weight=0)
            frame_root.rowconfigure(1, weight=1)
            frame_top_section = TkFrame(
                frame_root, parent_col=1, parent_row=1, cols=1, rows=3, sticky='ewn')
            if summary:
                TkLabel(frame_top_section, parent_col=1, parent_row=1,
                        text=summary, font=DEFAULT_FONT_LARGE, sticky='ew')
            if description:
                TkLabel(frame_top_section, parent_col=1, parent_row=2, text=description,
                        font=DEFAULT_FONT_MEDIUM, sticky='ew', wraplength=(width - 10))
            frame_buttons = TkFrame(
                frame_top_section, parent_col=1, parent_row=3, cols=2, rows=1, sticky='ew')
            frame_buttons.columnconfigure(0, weight=1)
            frame_buttons.columnconfigure(1, weight=1)
            self.button_collapse = TkButton(
                frame_buttons, parent_col=1, parent_row=1, text='Collapse All', sticky='ew')
            self.button_expand = TkButton(
                frame_buttons, parent_col=2, parent_row=1, text='Expand All', sticky='ew')
            self.treeview_result = TkTreeView(
                frame_root, parent_col=1, parent_row=2, sticky='nsew', show_units=show_units, sort_keys=sort_keys)
        except Exception as ex:
            print('exception while building ui: %s' % ex)
            print_traceback()
        # schedule setup_backend to run within the loop
        self.window.after(100, self.setup_backend)
        self.window.mainloop()

    @staticmethod
    def log_msg(message):
        # what to do with messages?
        print('TreeView: %s' % message)

    def setup_backend(self):
        # setup any backend stuffs
        self.button_expand.on_click(self.expand_tree)
        self.button_collapse.on_click(self.collapse_tree)
        if self.focus_force:
            self.window.focus_force()
        if self.data is not None:
            self.log_msg('Rendering tree...')
            self.treeview_result.load_dict(self.data)
            self.log_msg('Done rendering tree.')

    def cleanup(self):
        # cleanup any connections
        self.window.destroy()

    def expand_tree(self):
        # expand all items of treeview
        self.treeview_result.expand()

    def collapse_tree(self):
        # collapse all items of treeview
        self.treeview_result.collapse()
