import subprocess
import _thread
import traceback

"""
add remainder support
"""


class PowershellModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        env.callback_manager.registerCallback("envChange", self)

    def onEnvChange(self, new_env):
        self.env = new_env

    def exec(self, *args):
        remainder = args[1]
        args = args[0]

        to_run = []
        if len(args) == 0 and len(remainder) == 0:
            self.output_pipe("Nothing to run!")
        elif len(args) == 0:
            to_run = remainder[0]
        elif args[0] == "all" and len(remainder) > 0:
            to_run = remainder
        else:
            to_run = [" ".join(args)]

        for each_command in to_run:
            try:
                print("running", each_command.strip())
                p = subprocess.Popen(["powershell.exe", each_command], stdout=subprocess.PIPE)
                for line in p.stdout:
                    self.env.output_pipe(line)
            except Exception as e:
                print(e)

    def asyncRun(self, args, callback=None):
        _thread.start_new_thread(self.runAndWait, (args, callback))

    def runAndWait(self, args, callback=None):
        try:
            p = subprocess.Popen(["powershell.exe", " ".join(args)], stdout=subprocess.PIPE)
            p.wait()
            if callback is not None:
                callback()
            return True
        except Exception as e:
            print(e)
            return False

    def runAndWaitWithOutput(self, args, callback=None, stdout=True, stderr=False):
        output = ""
        try:
            print("executing ", " ".join(args))
            p = subprocess.Popen(["powershell.exe"," ".join(args)], stdout=subprocess.PIPE if stdout else None, stderr=subprocess.PIPE if stderr else None)
            out, err = p.communicate()

            p.wait()

            if callback is not None:
                callback()
            return out, err
        except Exception as e:
            print(e)
            print(e.__cause__)
            traceback.print_tb(e.__traceback__)
            return False


    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = PowershellModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return PowershellModule.getInstance(env)
