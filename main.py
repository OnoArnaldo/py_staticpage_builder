from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileDeletedEvent, FileModifiedEvent
import time
import sys

from page_builder import Builder, loads_config
from page_builder.config import build_config


class PageBuilderEventHandler(FileSystemEventHandler):
    def __init__(self, builder, build_pages=True, build_static=True):
        self.builder = builder
        self.build_pages = build_pages
        self.build_static = build_static

    def on_created(self, event):
        if isinstance(event, FileCreatedEvent):
            self.builder.run(clear=False, build_pages=self.build_pages, build_static=self.build_static)

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            self.builder.run(clear=False, build_pages=self.build_pages, build_static=self.build_static)

    def on_deleted(self, event):
        if isinstance(event, FileDeletedEvent):
            self.builder.run(clear=False, build_pages=self.build_pages, build_static=self.build_static)


def build():
    print('Building')
    config = loads_config('./config.yaml')
    builder = Builder(config)
    builder.run()


def watch():
    print('Start watching')
    config = loads_config('./config.yaml')
    builder = Builder(config)
    builder.run()

    page_event = PageBuilderEventHandler(builder, build_static=False)
    static_event = PageBuilderEventHandler(builder, build_pages=False)

    dog = Observer()
    dog.schedule(page_event, config.dirs.pages, recursive=True)
    dog.schedule(page_event, config.dirs.templates, recursive=True)
    dog.schedule(page_event, config.dirs.data, recursive=True)
    dog.schedule(static_event, config.dirs.static, recursive=True)
    dog.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        dog.stop()
    dog.join()


def help():
    print('main.py [options]')
    print('')
    print('options:')
    print('  -create-config <config-file>')
    print('  -watch')
    print('  -build')
    print('  -help')


def main(args):
    if len(args) == 0 or args[0] == '-build':
        build()

    elif args[0] == '-help':
        help()

    elif args[0] == '-create-config':
        build_config(args[1])

    elif args[0] == '-watch':
        watch()


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
