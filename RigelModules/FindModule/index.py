import os.path as path
from pathlib import Path


class FindModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        self.lib_loader = env.secure_load
        self.callback_manager = env.callback_manager
        env.callback_manager.registerCallback("envChange", self)
        self.log = env.secure_load("LogModule")

    def onEnvChange(self, new_env):
        self.env = new_env

    def searchInDir(self, to_search, target_path):
        ret = [str(result.absolute()) for result in Path(target_path).rglob(to_search)]
        self.env.output_pipe("Found ", len(ret), " results for ", to_search, " in ", target_path)
        return ret

    def exec(self, *args):
        input_args = args[0]
        buildup_str = args[1]
        if type(buildup_str) is list:
            if len(buildup_str) > 0:
                buildup_str = buildup_str[0]
            else:
                buildup_str = ""

        if len(input_args) < 2 or (len(input_args) < 3 and (buildup_str == "" or buildup_str is None)) \
                or (len(input_args) == 2 and input_args[0] != "in"):
            raise Exception(
                "example: find somefile in some_path || get_clipboard then find in workspace root then point")

        if input_args[0] == "in" and buildup_str == "":
            raise Exception("wrong chaining method, buildul_str is empty")
        elif input_args[0] == "in" and not (path.isdir(input_args[1]) or self.lib_loader(input_args[1]) is not None):
            raise Exception("must be chained with a folder path returning module or receive a literal absolute path ")
        elif input_args[0] == "in" and path.isdir(input_args[1]):
            return self.searchInDir(buildup_str, input_args[1])
        elif input_args[0] == "in":
            path_returning_module = self.lib_loader(input_args[1])
            if len(input_args) > 2:
                returned_path = path_returning_module.exec(input_args[2:])
            else:
                returned_path = path_returning_module.exec()
            return self.searchInDir(buildup_str, returned_path)
        elif input_args[1] == "in" and not (path.isdir(input_args[2]) or self.lib_loader(input_args[2]) is not None):
            raise Exception("must be chained with a folder path returning module or receive a literal absolute path ")
        elif input_args[1] == "in" and path.isdir(input_args[2]):
            return self.searchInDir(input_args[0], input_args[2])
        elif input_args[1] == "in":
            path_returning_module = self.lib_loader(input_args[2])
            if len(input_args) > 3:
                returned_path = path_returning_module.exec(input_args[3:], [])
                if len(returned_path) > 0:
                    returned_path = returned_path[0]
                else:
                    self.env.output_pipe("The module "+input_args[2]+" didn't return anything")
                    return []
                print(returned_path)
            else:
                returned_path = path_returning_module.exec()
            return self.searchInDir(input_args[0], returned_path)
        else:
            raise Exception("Something went wrong :(")

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = FindModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return FindModule.getInstance(env)
