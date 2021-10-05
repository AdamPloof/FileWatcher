# WatchAndCopy (wac)
WatchAndCopy is a script that behaves a like a cross between the Unix `find` and `cp` utilities. It takes in a directory
to look for files in, a destination directory to copy files to, and a list of filenames and/or patterns to find matching files by.
The files that match the name or pattern are then watched for changes and when a change happens the modified file(s) are
copied to the destination directory provided.

The source and destination directories, filenames/patterns, and other options can either be passed in via command line args
or read from a wac.config.json file which can be used to remember watch and copy settings for a project. The wac.config.json file
can be created with the command line as well.

## Basic Examples
These are just a few examples to give an idea of how this tool can be used.

**Watch a specific file and copy to destination folder on change**\
`> python -m WatchAndCopy '.' 'myDestination/' --name 'myFile.txt'`

**Watch all files of a given type and copy to destination folder on change**\
`> python -m WatchAndCopy 'myProjectDir/' 'myDestination/someSubfolder/' --name '*.php'`

**Add files matching pattern to config file**\
`> python -m WatchAndCopy '.' 'myDestination/' --name 'myPattern*' --add`

**Add multiple files to config file and watch**\
`> python -m WatchAndCopy '.' 'myDestination/' --name 'myFile1.txt' 'myFile2.txt' 'myFile3.txt' --add --conf`

## Command Line Usage
usage: WatchAndCopy.py [-h] [-n NAME [NAME ...]] [-r] [--conf] [-i] [-a | -d] [find] [dest]

Provide a file or files to watch for changes. When a change is detected, copy the changed file to a target directory. For more
complex watching and copying, FileWatcher can be used set up a wac.config.json file to be used to define which files to watch
and where to copy them to.

positional arguments:\
&nbsp;&nbsp;find                  The source directory to look for watch files in.\
&nbsp;&nbsp;dest                  The target directory to copy the watched files to when changes are detected.

optional arguments:\
&nbsp;&nbsp;-h, --help            show this help message and exit\
&nbsp;&nbsp;-n NAME [NAME ...], --name NAME [NAME ...]\
                        The name(s) of the files or pattern to use for finding files to watch.\
&nbsp;&nbsp;-r, --recursive       Search in subdirectories for files matching the source argument. Watched files in child directories will\
                        be copied to directories of the same name within the destination in order to maintain the structure of\
                        the source directory.\
&nbsp;&nbsp;--conf                Start file watcher using settings in wac.config.json file to determine source files to watch and\
                        destinations to copy to.\
&nbsp;&nbsp;-i, --ignore          This flag will add/remove files to/from the ignore list. Files in the ignore list will never be watched\
                        for changes.\
&nbsp;&nbsp;-a, --add             Add file(s) and destinations to config file watch-list/ignore-list\
&nbsp;&nbsp;-d, --delete          Remove file(s) and destinations from config file watch-list/ignore-list\

## Running from a Config File
To run WatchAndCopy using a wac.config.json file run the program with either the `--conf` argument or with no arguments (positional or optional) 
at all. To add files to the config watch list use the `--add` flag. To remove them use the `--delete` flag. When using the `--ignore` flag, files will
added/deleted from the ignore list rather than the watch list.

While using the command line to create and add/remove files to the watch/ignore list is probably the easist way to set up the config file, 
feel free to manually create or modify the contents of it if you like.

The structure of the wac.config.json is:
```
{
    "watch": {
        "destination_dir1": [
            "file1",
            "file2",
            ...
        ],
        "destination_dir2": [
            ...
        ],
        ...
    },
    "ignore": [
        "file3",
        "file4",
        "dir3",
        ...
    ]
}
```