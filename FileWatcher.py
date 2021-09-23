import os, shutil, time

class FileChangeWatcher():
    def __init__(self, watch_file):
        self._cached_modified_time = 0
        self.watch_file = watch_file

    def startWatch(self):
        print(f"Watching {self.watch_file}...")

        while True:
            self.checkForChange()
            time.sleep(1)

    def checkForChange(self):
        modified_time = os.stat(self.watch_file).st_mtime
        if modified_time != self._cached_modified_time:
            if self._cached_modified_time != 0:
                self.copyFile()

            self._cached_modified_time = modified_time

    def getCleanFilename(self):
        return self.watch_file.replace("./", "")

    def copyFile(self):
        destination_path = 'z:\\Apache24\\htdocs-dev\\Dev2\\civicrmscripts\\MemberWorkUploader\\'
        destination_filename = destination_path + self.getCleanFilename()
        try:
            shutil.copy2(self.watch_file, destination_filename)
            print(f"File updated! Copying... {self.watch_file} {destination_filename}")
        except IOError as e:
            print(e)

def main():
    filename = "./MemberWorkUploader.php"
    watcher = FileChangeWatcher(filename)
    watcher.startWatch()


if __name__ == "__main__":
    main()
