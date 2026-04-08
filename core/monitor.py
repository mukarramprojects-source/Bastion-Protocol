from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver as Observer

class BastionHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.is_healing = False

    def on_modified(self, event):
        if not event.is_directory and not self.is_healing:
            self.callback("Modification", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory and not self.is_healing:
            self.callback("Deletion", event.src_path)
    def on_moved(self, event):
        if not event.is_directory and not self.is_healing:
            self.callback("Move/Rename", event.src_path)

class BastionWatcher:
    def __init__(self, path, callback):
        self.path = path
        self.handler = BastionHandler(callback)
        self.observer = Observer()

    @property
    def is_healing(self):
        return self.handler.is_healing

    @is_healing.setter
    def is_healing(self, value):
        self.handler.is_healing = value

    def start(self):
        self.observer.schedule(self.handler, self.path, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
