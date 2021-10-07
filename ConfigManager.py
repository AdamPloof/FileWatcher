import os
import json
from pathlib import Path

from FileChangeWatcher import FileChangeWatcher

"""
ConfigManager handles reading and writing to and from a wac.config.json file.
The config file stores a files to watch grouped by the destination that those files should be moved
to when changes are detected. The config file also stores a list of files that should be ignored. Files in the 
ignore list will not be watched even if they are also in the watch list. This allows users to use broad patterns
for adding files to the watch list (for example: "*") and then selectively omit certain files without having to edit the config file.

The ConfigManager can also be used to instantiate new FileWatchers and provide it with file lists and their copy destinations. 

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
        self.config['watch'] = {Path(dest): self.stringListToPath(paths) for (dest, paths) in config['watch'].items()}
        self.config['ignore'] = self.stringListToPath(config['ignore'])

    def addWatchFiles(self, filenames, dest):        
        if dest in self.config['watch']:
            for filename in filenames:
                if not filename in self.config['watch'][dest]:
                    self.config['watch'][dest].append(filename)
        else:
            self.config['watch'][dest] = filenames

    def removeWatchFiles(self, filenames, dest):
        for filename in self.config['watch'][dest]:
            if filename in filenames:
                self.config['watch'][dest].remove(filename)

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

    def isIgnoreFile(self, filename):
        isIgnoreFile = False

        if filename in self.config['ignore']:
            isIgnoreFile = True
        
        return isIgnoreFile

    def writeConfigFile(self):
        # Convert POSIX paths to strings so that they can be serialized
        normalized_config = {}
        normalized_config['watch'] = {str(dest): self.pathListToString(paths) for (dest, paths) in self.config['watch'].items()}
        normalized_config['ignore'] = self.pathListToString(self.config['ignore'])

        with open(self.config_path, 'w') as config_file:
            json.dump(normalized_config, config_file, indent='\t')
    
    def watch(self):
        for dest, files in self.config['watch'].items():
            filtered_files = [file for file in files if not self.isIgnoreFile(file)]
            self.watcher.addWatchFiles(filtered_files, dest)
            self.watcher.startWatch()
