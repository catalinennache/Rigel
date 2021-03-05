import random
import sys
import os


class ShowModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        env.callback_manager.registerCallback("envChange", self)
        self.opened_files = []
        self.run_module = env.secure_load("RunModule")

    def onEnvChange(self, new_env):
        self.env = new_env

    def show(self, string):
        name = str(random.randint(0, sys.maxsize))
        tmp_path = os.getenv('APPDATA') + "\\..\\Local\\Temp\\" + name
        f = open(tmp_path, "w")
        f.write(string)
        self.opened_files.append(tmp_path)
        f.close()
        self.run_module.asyncRun(['notepad', '"' + tmp_path + '"'], lambda: self.onClose(tmp_path))

    def onClose(self, path_to_delete):
        os.remove(path_to_delete)
        self.opened_files.remove(path_to_delete)

    def exec(self, *args):
        to_show = args[0]
        print(args)
        remainders = args[1]
        if remainders is None or len(remainders) == 0:
            remainders = ['']
        print(to_show, remainders)
        result = "********THIS CONTENT WILL BE LOST UPON CLOSING THE DOCUMENT, PLEASE SAVE AS********\n\n"

        for remainder in remainders:
            if len(to_show) == 0 and len(remainders) == 0:
                self.env.output_pipe("Nothing to show\n")
            elif len(to_show) == 0:
                result += remainder+"\n"
            else:
                potential_lib = to_show[0]
                potential_lib = self.env.to_module_name(potential_lib)
                raw_result = " ".join(to_show)

                module = self.env.secure_load(potential_lib)
                if module is not None:
                    raw_result = module.exec(to_show[1:], "")
                    print(raw_result)
                    if len(raw_result) > 1 and type(raw_result) is list:
                        raw_result = " ".join([str(x)+"\n" for x in raw_result])
                        self.env.output_pipe("Multiple results detected.")
                    elif len(raw_result) == 1:
                        raw_result = raw_result[0]
                    elif type(raw_result) is list:
                        raw_result = ""
                        self.env.output_pipe("No results found!")
                
                result += raw_result
                if not result.endswith("\n"):
                    result += "\n"

        self.show(result)

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = ShowModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return ShowModule.getInstance(env)
