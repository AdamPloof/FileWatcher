import argparse
from pathlib import Path

from FileChangeWatcher import FileChangeWatcher
from ConfigManager import ConfigManager

"""
This script handles executing the WatchAndCopy (wac) script. It parses command line args, instantiates the FileWatcher or the ConfigManager
depending on the mode that the script is executed in (regular or configuration mode).

One particularly important function in this file is getFilePaths which is used to find the files matching the pattern provided through the
--name command line arg. The file list returned from this function is passed to both the ConfigManager.addWatchFiles() method as well as the
FileWatcher.addWatchFiles() method.
"""

# Destination directory is needed here so that we can make sure to exclude watching
# files in the destination directory when in recursive mode
def getFilePaths(source_dir, dest_dir, filenames, recursive=False):
    all_files = []
    for name in filenames:
        if recursive:
            all_files.extend(list(source_dir.glob(f"**/{name}")))
        else:
            all_files.extend(list(source_dir.glob(name)))
        
    files = [f for f in all_files if not isDefaultIgnore(f, dest_dir)]
    return files

def isDefaultIgnore(filepath, dest_dir):
    is_default_ignore = False

    if '.git' in filepath.parts:
        is_default_ignore = True
    elif dest_dir == filepath.parent:
        is_default_ignore = True
    elif filepath.is_dir():
        is_default_ignore = True
    elif 'wac.config.json' == filepath:
        is_default_ignore = True

    return is_default_ignore
        

def getCommandLineArgs():
    parser = argparse.ArgumentParser(description="""
        Provide a file or files to watch for changes. When a change is detected, copy
        the changed file to a target directory. For more complex watching and copying,
        FileWatcher can be used set up a wac.config.json file to be used to define which
        files to watch and where to copy them to.
    """)

    parser.add_argument('find', help="The source directory to look for watch files in.", nargs='?', default=0)
    parser.add_argument('dest', help='The target directory to copy the watched files to when changes are detected.', nargs='?', default=0)
    parser.add_argument('-n', '--name', help='The name(s) of the files or pattern to use for finding files to watch.', nargs='+')
    parser.add_argument('-r', '--recursive', 
        help="""
            Search in subdirectories for files matching the source argument.
            Watched files in child directories will be copied to directories of the same name within the destination in order to
            maintain the structure of the source directory.
        """, 
        action='store_true'
    )

    # Config file arguments
    parser.add_argument('--conf', help="Start file watcher using settings in wac.config.json file to determine source files to watch and destinations to copy to.", action='store_true')
    parser.add_argument('-i', '--ignore', help="This flag will add/remove files to/from the ignore list. Files in the ignore list will never be watched for changes.", action='store_true')

    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument('-a', '--add', help="Add file(s) and destinations to config file watch-list/ignore-list", action='store_true')
    config_group.add_argument('-d', '--delete', help="Remove file(s) and destinations from config file watch-list/ignore-list", action='store_true')

    return parser.parse_args()

def useConfigFile(args):
    useConfigFile = False

    if args.conf:
        useConfigFile = True
    elif args.add:
        useConfigFile = True
    elif args.delete:
        useConfigFile = True

    return useConfigFile

def getConfigManager(args, files):
    config_manager = ConfigManager()

    if not files:
        return config_manager
    
    # Safe to assume there will be a valid destination at this point because otherwise files would be None or empty
    dest = Path(args.dest)

    if args.add:
        if args.ignore:
            config_manager.addIgnoreFiles(files)
        else:
            config_manager.addWatchFiles(files, dest)
        
        config_manager.writeConfigFile()
    elif args.delete:
        if args.ignore:
            config_manager.removeIgnoreFiles(files)
        else:
            config_manager.removeWatchFiles(files, dest)
        
        config_manager.writeConfigFile()

    return config_manager

def main():
    args = getCommandLineArgs()

    if args.find and not args.dest:
        raise Exception('A destination must be provided for watch files.')
    elif not args.find and not args.dest:
        # Calling the program with no positional args defaults to config mode
        args.conf = True
        files = []
    else:
        source_dir = Path(args.find)
        dest_dir = Path(args.dest)

        try:
            files = getFilePaths(source_dir, dest_dir, args.name, args.recursive)
        except TypeError as err:
            raise Exception('A filename or pattern must be provided by using the --name argument')

    if useConfigFile(args):
        config_manager = getConfigManager(args, files)

        if args.conf:
            config_manager.watch()
    else:
        watcher = FileChangeWatcher()
        watcher.addWatchFiles(files, dest_dir)
        watcher.startWatch()


if __name__ == "__main__":
    main()
