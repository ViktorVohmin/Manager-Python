import os
import sys
import time
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from subprocess import Popen

class MyHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.last_md5 = self.calculate_md5()

    def calculate_md5(self):
        md5 = hashlib.md5()
        with open(self.file_path, "rb") as f:
            while chunk := f.read(8192):
                md5.update(chunk)
        return md5.hexdigest()

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path == self.file_path:
            new_md5 = self.calculate_md5()
            if new_md5 != self.last_md5:
                print(f"Detected change in {event.src_path}")
                self.last_md5 = new_md5
                try:
                    print("Restarting main.py...")
                    Popen([sys.executable, self.file_path])
                except Exception as e:
                    print(f"Error while restarting: {e}")

if __name__ == "__main__":
    file_path = "C:\\Server\\API\\main.py"
    working_directory = "C:\\Server\\API"  # Укажите вашу рабочую папку здесь
    
    event_handler = MyHandler(file_path)
    observer = Observer()
    observer.schedule(event_handler, working_directory, recursive=False)
    
    try:
        # Сначала запустить main.py
        print("Starting main.py...")
        Popen([sys.executable, file_path])

        # Затем начать отслеживание изменений
        print("Starting the watcher...")
        observer.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
