import argparse

from watcher import Watcher

parser = argparse.ArgumentParser(description="Process valid .py file")
parser.add_argument('pyfile', metavar='FILE', type=str, help="Path to valid .py file")
parser.add_argument("-e", "--exec", type=str, help="Executable", metavar='EXEC')
parser.add_argument("-i", "--ignore", nargs='*', type=str, help="Ignored folders and files", metavar='')

if __name__ == '__main__':
    args = parser.parse_args()
    if args:
        try:
            watcher = Watcher(args.pyfile, args.exec, args.ignore)
        except KeyboardInterrupt:
            print("Exiting on interrupt")
    pass
