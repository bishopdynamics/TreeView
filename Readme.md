# TreeView

A simple utility for macOS to load json data from stdin or a file and render a nice interactive treeview to explore it.

[MIT license](License.txt)

![screenshot](screenshot.png)

## Build & Install

build it with: `./build-app.sh`, then find the app in `./dist/` 

Drag `TreeView.app` into your Applications folder.

## Usage

Open the app, and it will prompt you to select a file ending in `.json`

There are three ways to use it from terminal:
* pipe data to stdin: `cat sampledata.json | /Applications/TreeView.app/Contents/MacOS/TreeView`
* read data from a file: `/Applications/TreeView.app/Contents/MacOS/TreeView sampledata.json`
* use a file selection dialog: `/Applications/TreeView.app/Contents/MacOS/TreeView`



I like to throw a symlink my `~/bin/`
```bash
ln -s /Applications/TreeView.app/Contents/MacOS/TreeView ~/bin/treeview

# direct
treeview sampledata.json

# stdin
cat sampledata.json |treeview
```

## STDIN Race Condition
What if I have a race condition with my stdin? 

Let's say you run a script which takes a second before it spits out json to stdout, and you pipe that into `treeview`.

No problem! The filedialog will appear (because stdin wasnt there on time), 
just wait a few seconds to let your script finish, then hit "Cancel" button.

After you hit "Cancel" the app will check stdin again, and if it finds data it will re-exec itself with that data to stdin.

## Testing

For testing, you can build & run it all at once with `./run.sh sampledata.json`

## Linux and other Unix-like systems

I only tested this on macOS, but this is all really basic python3 with tkinter, built into a macOS app using pyinstaller. It should be trivial to tweak it to work on any other system, and might already work out of the box.
