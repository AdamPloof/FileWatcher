import shutil, time, sys
from pathlib import Path

"""
FileChangeWatcher takes in a list of files and the destinations to copy those files to when changes are made to them.

It uses the modified time of the file and compares it to the cached modified time for that file to determine if it should
be copied to the destination directory. Files are polled for changes once every second.
"""
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
            try:
                self.scanWatchListForChanges()
                time.sleep(1)
            except KeyboardInterrupt as e:
                print("All done watching. Bye!")
                sys.exit(0)
    
    def scanWatchListForChanges(self):
        for dest, watch_files in self.watch_list.items():
            for f in watch_files:
                self.checkFileForChanges(f, dest)

    def checkFileForChanges(self, watch_file, dest):
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
