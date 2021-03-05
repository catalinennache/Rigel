

class EditModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        env.callback_manager.registerCallback("envChange", self)
        self.opened_files = []
        self.run_module = env.secure_load("RunModule")
        self.logger = env.secure_load("LogModule")
        global os, sys, random
        os = env.secure_load("os")
        sys = env.secure_load("sys")
        random = env.secure_load("random")


    def onEnvChange(self, new_env):
        self.env = new_env

    def presentEditWindow(self, to_edit):
        name = str(random.randint(0, sys.maxsize))
        tmp_path = os.getenv('APPDATA') + "\\..\\Local\\Temp\\" + name
        f = open(tmp_path, "w")
        f.write(to_edit)
        self.opened_files.append(tmp_path)
        f.close()
        self.run_module.runAndWait(['notepad', '"' + tmp_path + '"'], lambda: self.logger.log("Input Window closed"))
        f = open(tmp_path, "r")
        content = f.read()
        f.close()

        content = content.strip("\n")
        return [content]

    def onClose(self, path_to_delete):
        os.remove(path_to_delete)
        self.opened_files.remove(path_to_delete)

    def exec(self, *args):
        self.logger.log("executing edit")
        to_edit = ""
        if len(args[0]) > 0:
            module = self.env.secure_load(self.env.to_module_name(args[0][0]))
            if module is not None:
                results = module.exec(args[0][1:], [])
                edited_results = []
                for result in results:
                    edited_results.extend(self.presentEditWindow(result))
                return edited_results

        remainders = args[1]
        print(remainders)

        if type(remainders) is list and len(remainders) == 0:
            self.env.output_pipe("Nothing to edit :(")
            return [""]
        elif type(remainders) is list:
            to_edit = "\n".join(remainders)
        elif type(remainders) is str:
            to_edit = remainders
        else:
            self.env.output_pipe("Nothing to edit :(")
            return [""]

        return self.presentEditWindow(to_edit)

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = EditModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return EditModule.getInstance(env)
