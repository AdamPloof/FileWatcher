import os, shutil, time, argparse
import json

from pathlib import Path

class FileChangeWatcher():
    def __init__(self):
        self.watch_list = {}

    def addWatchFiles(self, files, dest):
        watch_files = [{'file': f, 'cached_mod_time': 0} for f in files]

        # Safe to assume that we won't be attempting to add additional watch files for a desination that already exists
        self.watch_list[dest] = watch_files

    def startWatch(self):
        print(f"Watching files...")

        while True:
            for dest, watch_files in self.watch_list.items():
                for f in watch_files:
                    self.checkForChanges(f, dest)

            time.sleep(1)           

    def checkForChanges(self, watch_file, dest):
        modified_time = watch_file['file'].stat().st_mtime
        if modified_time != watch_file['cached_mod_time']:
            if watch_file['cached_mod_time'] != 0:
                self.copyFile(watch_file, dest)

            for key, file in enumerate(self.watch_list[dest]):
                if file['file'] == watch_file['file']:
                    self.watch_list[dest][key]['cached_mod_time'] = modified_time
                    break

    def copyFile(self, watch_file, dest):
        destination_filename = dest / watch_file['file']

        # Make any subdirectories within the destination directory to mirror the source structure
        if not destination_filename.parent.exists():
            Path.mkdir(destination_filename.parent, parents=True)

        try:
            shutil.copy2(watch_file['file'], destination_filename)
            print(f"File updated! Copying... {watch_file['file']} to {destination_filename}")
        except IOError as e:
            print('An error occured: ')
            print(e)


"""
Structure of config file is:
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
"""
class ConfigManager():
    def __init__(self) -> None:
        self.config_path = 'wac.config.json'
        self.watcher = FileChangeWatcher()

        if not os.path.exists(self.config_path):
            create_config_file = input('Could not find config file. Would you like to create one? (y/n):')
            if create_config_file.lower() == 'y' or create_config_file.lower() == 'yes':
                with open(self.config_path, 'w+') as f:
                    blank_config = {
                        'watch': {},
                        'ignore': {}
                    }
                    json.dump(blank_config, f)
            else:
                raise Exception('Could not load config file: File does not exit.')

        with open(self.config_path, 'r') as config_file:
            config = json.load(config_file)
        
        # Convert string to POSIX path
        self.config = {}
        self.config['watch'] = {str(dest): self.stringListToPath(paths) for (dest, paths) in config['watch'].items()}
        self.config['ignore'] = self.stringListToPath(config['ignore'])

    def addWatchFiles(self, filenames, dest):
        dest_str = str(dest)
        
        if dest_str in self.config['watch']:
            for filename in filenames:
                if not filename in self.config['watch'][dest_str]:
                    self.config['watch'][dest_str].append(filename)
        else:
            self.config['watch'][dest_str] = filenames

    def removeWatchFiles(self, filenames, dest):
        dest_str = str(dest)

        for filename in self.config['watch'][dest_str]:
            if filename in filenames:
                self.config['watch'][dest_str].remove(filename)

    def addIgnoreFiles(self, filenames):
        for filename in filenames:
            if not filename in self.config['ignore']:
                self.config['ignore'].append(filename)

    def removeIgnoreFiles(self, filenames):
        for filename in filenames:
            if filename in self.config['ignore']:
                self.config['ignore'].remove(filename)

    def stringListToPath(self, str_paths):
        return [Path(str_path) for str_path in str_paths]

    def pathListToString(self, paths):
        return [str(path) for path in paths]

    def writeConfigFile(self):
        # Convert POSIX paths to strings so that they can be serialized
        normalized_config = {}
        normalized_config['watch'] = {str(dest): self.pathListToString(paths) for (dest, paths) in self.config['watch'].items()}
        normalized_config['ignore'] = self.pathListToString(self.config['ignore'])

        with open(self.config_path, 'w') as config_file:
            json.dump(normalized_config, config_file, indent='\t')
    
    def watch(self):
        for dest, files in self.config['watch'].items():
            filtered_files = [file for file in files if not file in self.config['ignore']]
            self.watcher.addWatchFiles(filtered_files, dest)
            self.watcher.startWatch()

# Destination directory is needed here so that we an make sure to exclude watching
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
        FileWatcher can be used set up a watch.config.json file to be used to define which
        files to watch and where to copy them to.
    """)

    parser.add_argument('find', help="The source directory to look for watch files in.", nargs='?', default=0)
    parser.add_argument('dest', help='The target directory to copy the watched files to when changes are detected.', nargs='?', default=0)
    parser.add_argument('-n', '--name', help='The name(s) of the files or pattern to use for finding files to watch.', nargs='+')
    parser.add_argument('-r', '--recursive', 
        help="""
            Search in subdirectories for files matching the source argument.
            Watched files in child directories will be copied to directories of the same name within the destination in order to
            maintain the structure of the source directory. This behavior can be overridden by specifying target destinations
            on per file basis in a configuration file.
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
    
    if args.add:
        if args.ignore:
            config_manager.addIgnoreFiles(files)
        else:
            config_manager.addWatchFiles(files, args.dest)
        
        config_manager.writeConfigFile()
    elif args.delete:
        if args.ignore:
            config_manager.removeIgnoreFiles(files)
        else:
            config_manager.removeWatchFiles(files, args.dest)
        
        config_manager.writeConfigFile()

    return config_manager

def main():
    args = getCommandLineArgs()

    if args.find and not args.dest:
        raise Exception('A destination must be provided for watch files.')
    elif not args.find and not args.dest:
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
