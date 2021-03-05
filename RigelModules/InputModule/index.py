import os
import random
import sys

class InputModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        env.callback_manager.registerCallback("envChange", self)
        self.opened_files = []
        self.run_module = env.secure_load("RunModule")
        self.logger = env.secure_load("LogModule")

    def onEnvChange(self, new_env):
        self.env = new_env

    def presentInputWindow(self):
        name = str(random.randint(0, sys.maxsize))
        tmp_path = os.getenv('APPDATA') + "\\..\\Local\\Temp\\" + name
        f = open(tmp_path, "w")
        f.write("Write here your input (delete this line before saving)")
        self.opened_files.append(tmp_path)
        f.close()
        self.run_module.runAndWait(['notepad', '"' + tmp_path + '"'], lambda: self.logger.log("Input Window closed"))
        f = open(tmp_path, "r")
        content = f.read()
        f.close()

        if content.startswith("Write here your input (delete this line before saving)"):
            content = content.replace("Write here your input (delete this line before saving)", "")
        content = content.strip("\n")
        self.env.output_pipe("You inputed ", content)
        return [content]

    def onClose(self, path_to_delete):
        os.remove(path_to_delete)
        self.opened_files.remove(path_to_delete)

    def exec(self, *args):
        self.logger.log("executing input")

        return self.presentInputWindow()
    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = InputModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return InputModule.getInstance(env)
