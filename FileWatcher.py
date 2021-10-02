import os, shutil, time, argparse
import json

from pathlib import Path

class FileChangeWatcher():
    def __init__(self, watch_files, dest_path):
        self.watch_files = [{'file': f, 'cached_mod_time': 0} for f in watch_files]
        self.dest_path = dest_path

    def startWatch(self):
        print(f"Watching {[str(f['file']) for f in self.watch_files]}...")

        while True:
            for f in self.watch_files:
                self.checkForChanges(f)

            time.sleep(1)

    def checkForChanges(self, watch_file):
        modified_time = watch_file['file'].stat().st_mtime
        if modified_time != watch_file['cached_mod_time']:
            if watch_file['cached_mod_time'] != 0:
                self.copyFile(watch_file)

            for key, file in enumerate(self.watch_files):
                if file['file'] == watch_file['file']:
                    self.watch_files[key]['cached_mod_time'] = modified_time
                    break

    def copyFile(self, watch_file):
        destination_filename = self.dest_path / watch_file['file']

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
    def __init__(self, config_path=None) -> None:
        if config_path:
            self.config_path = config_path
        else:
            self.config_path = 'wac.config.json'

        if not os.path.exists(self.config_path):
            create_config_file = input('Could not find config file. Would you like to create one? (y/n):')
            if create_config_file.lower() == 'y' or create_config_file.lower() == 'yes':
                with open(self.config_path, 'w+') as f:
                    blank_config = {
                        'watch': [],
                        'ignore': []
                    }
                    json.dump(blank_config, f)
            else:
                raise Exception('Could not load config file: File does not exit.')

        with open(self.config_path, 'r') as config_file:
            self.config = json.load(config_file)

    def addWatchFile(self, filename, destination):
        if destination in self.config['watch']:
            if not filename in self.config['watch'][destination]:
                self.config['watch'][destination].append(filename)
        else:
            self.config['watch'][destination] = [filename]

    def removeWatchFile(self, filename):
        for dest in self.config['watch']:
            if filename in self.config['watch'][dest]:
                self.config['watch'][dest].remove(filename)

    def addIgnoreFile(self, filename):
        if not filename in self.config['ignore']:
            self.config['ignore'].append(filename)

    def removeIgnoreFile(self, filename):
        if filename in self.config['ignore']:
            self.config['ignore'].remove(filename)

    def writeConfigFile(self):
        with open(self.config_path, 'w') as config_file:
            json.dump(self.config, config_file)


def getFilePaths(source_dir, dest_dir, filenames, recursive=False):
    all_files = []
    for name in filenames:
        if recursive:
            all_files.extend(list(source_dir.glob(f"**/{name}")))
        else:
            all_files.extend(list(source_dir.glob(name)))
        
    files = [f for f in all_files if not '.git' in f.parts and dest_dir != f.parent and not f.is_dir()]
    return files

def main():
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
    parser.add_argument('-c', '--conf', help="Start file watcher using settings in wac.config.json file to determine source files to watch and destinations to copy to.", action='store_true')

    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument('-a', '--add', help="Add file(s) and destinations to config file watch-list/ignore-list", action='store_true')
    config_group.add_argument('-d', '--delete', help="Remove file(s) and destinations from config file watch-list/ignore-list", action='store_true')
    config_group.add_argument('-i', '--ignore', help="This flag will add/remove files to/from the ignore list. Files in the ignore list will never be watched for changes.", action='store_true')

    args = parser.parse_args()

    if args.find and not args.dest:
        raise Exception('A destination must be provided for watch files.')
    elif args.conf or (not args.find and not args.dest):
        pass

    source_dir = Path(args.find)
    dest_dir = Path(args.dest)

    files = getFilePaths(source_dir, dest_dir, args.name, args.recursive)

    if args.add:
        pass
    elif args.delete:
        pass
    elif args.ignore:
        pass

    watcher = FileChangeWatcher(files, dest_dir)
    watcher.startWatch()


if __name__ == "__main__":
    main()
