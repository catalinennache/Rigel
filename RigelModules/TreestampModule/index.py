import os
import glob


class TreestampModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        env.callback_manager.registerCallback("envChange", self)

    def onEnvChange(self, new_env):
        self.env = new_env

    def exec(self, *args):
        input_args = args[0]
        remainders = args[1]

        if len(input_args) == 0 and len(remainders) == 0:
            self.env.output_pipe("Nothing to treestamp")
            return []
        elif len(input_args) == 0:
            input_args = remainders[0]

        if os.path.isabs(input_args[0]):
            files = [f for dirpath, dirnames, file in os.walk(input_args[0]) for f in
                     glob.iglob(os.path.join(next(glob.iglob(os.path.join(dirpath, "")),
                                                  '\\\\'), "*.{}".format("*")))]
            print(files)
            return files
        return []

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = TreestampModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return TreestampModule.getInstance(env)
