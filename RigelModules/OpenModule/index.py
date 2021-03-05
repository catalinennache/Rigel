import os


class OpenModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        self.run_lib = env.secure_load("RunModule")
        env.callback_manager.registerCallback("envChange", self)

    def onEnvChange(self, new_env):
        self.env = new_env

    def exec(self, *args):
        input_args = args[0]
        remainder = args[1]
        if type(remainder) is list:
            if len(remainder) > 0:
                remainder = remainder[0]
            else:
                remainder = ""

        if len(input_args) == 0 and (remainder is None or remainder == ""):
            raise Exception("open some_abs_path || find x in y then point")
        if len(input_args) == 0:
            input_args = remainder

        try:
            print("OpenModule executed", args)
            if "." in input_args[0].split("\n")[-1]:
                if not input_args[0].endswith(".exe"):
                    os.startfile(input_args[0])
                else:
                    print("attempting to exec", input_args[0])
                    os.system('"' + input_args[0] + '"')
            else:
                self.run_lib.exec((['explorer "' + input_args[0] + '"']))
        except Exception as e:
            print(e)

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = OpenModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return OpenModule.getInstance(env)
