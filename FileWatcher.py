import os, shutil, time, argparse

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

    parser.add_argument('find', help="The source directory to look for watch files in.")
    parser.add_argument('dest', help='The target directory to copy the watched files to when changes are detected.')
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
    parser.add_argument('-a', '--add', help="Add file(s) and destinations to config file watch-list/ignore-list")
    parser.add_argument('-d', '--delete', help="Remove file(s) and destinations from config file watch-list/ignore-list")
    parser.add_argument('-i', '--ignore', help="This flag will add/remove files to/from the ignore list. Files in the ignore list will never be watched for changes.")
    parser.add_argument('-c', '--conf', help="Start file watcher using settings in watch.config.json file to determine source files to watch and destinations to copy to.")

    args = parser.parse_args()

    source_dir = Path(args.find)
    dest_dir = Path(args.dest)

    files = getFilePaths(source_dir, dest_dir, args.name, args.recursive)

    watcher = FileChangeWatcher(files, dest_dir)
    watcher.startWatch()


if __name__ == "__main__":
    main()
