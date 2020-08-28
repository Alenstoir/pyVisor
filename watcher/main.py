import asyncio
import os
import signal
import subprocess
import sys
import time
from os import walk
from os.path import dirname, getmtime, join


class CustomPrint:
    def __init__(self):
        self.old_stdout = sys.stdout
        self.fileno = sys.stdout.fileno
        self.prefix = None
        self.flush = sys.stdout.flush

    def write(self, text):
        rtext = text.rstrip()
        if len(rtext) == 0:
            self.old_stdout.write(text)
            return
        self.old_stdout.write(self.prefix + rtext)


class Watcher:
    def __init__(self, path, exec_file, ignore):
        print(path, ignore)
        self.exec_file = exec_file
        self.file = path
        self.path = dirname(path)
        self.ignore = ignore
        self.f = {}
        self.printer = CustomPrint()
        sys.stdout = self.printer
        ioloop = asyncio.get_event_loop()
        ioloop.run_until_complete(self.loop_supervisor(self, ioloop))
        ioloop.close()

    @staticmethod
    async def loop_supervisor(self, ioloop):
        while True:
            try:
                await self.listen()
            except KeyboardInterrupt as e:
                ioloop.close()
                pass

    @staticmethod
    def check(item):
        timestamp = getmtime(item[0])
        if item[0] == "D:\gits\python_os\solar_enchanced\main.py":
            print("Stored:", item[1], "current:", timestamp)
        if timestamp != item[1]:
            return False
        return True

    async def cycle(self):

        changemark = None
        while True:
            for item in self.f.items():
                if not self.check(item):
                    changemark = True
            await asyncio.sleep(1)
            if changemark:
                print("State changed")
                break
        if changemark:
            return 'changed'
        return False

    async def listen(self):
        pending = None
        proc = None
        try:
            self.snapshot()
            self.printer.prefix = '[pyVisor]'

            proc = await asyncio.create_subprocess_shell('python ' + self.file,
                                                         stdout=self.printer,
                                                         stderr=subprocess.STDOUT,
                                                         shell=True)
            pid = proc.pid
            print("Starting project {} on {} |=====================================\n".format(proc, pid))
            tasks = [self.cycle()]
            proc.stdout = sys.stdout
            done, pending = await asyncio.wait(tasks)
            if done.pop().result():
                pass

        except KeyboardInterrupt as e:
            print("Killing executable |============================================\n")
            print()
            time.sleep(2)

        finally:
            if pending:
                for task in pending:
                    task.cancel()
            if proc:
                if proc.returncode is None:
                    os.kill(pid, signal.CTRL_C_EVENT)
                    proc.terminate()
                    proc.kill()

    def snapshot(self):
        for root, dirs, files in walk(self.path, topdown=True):
            dirs[:] = [d for d in dirs if d not in self.ignore]
            for file in files:
                self.f[str(join(root, file.title()))] = getmtime(join(root, file.title()))

