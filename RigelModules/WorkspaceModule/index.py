import os


class WorkspaceModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        self.workspaces = None
        env.callback_manager.registerCallback("envChange", self)

    def onEnvChange(self, new_env):
        self.env = new_env

    def loadFromMemory(self):

        if not os.path.isfile("RigelModules/workspace/workspaces.data"):
            f = open("RigelModules/workspace/workspaces.data", "w+")
            f.close()
        memory = open("RigelModules/workspace/workspaces.data", "r")
        data = memory.readlines()
        memory.close()
        self.workspaces = {}
        for line in data:
            #line.replace("\\", "\\\\")
            line = line.strip("\n")
            key = line.split("=")[0]
            value = line.split("=")[1]
            self.workspaces[key] = value

    def sync(self):
        memory = open("RigelModules/workspace/workspaces.data", "w")
        for k in self.workspaces:
            memory.write(k + "=" + self.workspaces[k] + "\n")
        memory.close()

    def exec(self, *args):
        if self.workspaces is None:
            self.loadFromMemory()
        returned_str = ""
        if len(args) > 1:
            returned_str = args[1]
            if len(returned_str) == 0:
                returned_str = ""

        if len(args) == 0 or (len(args[0]) == 0 and returned_str == ""):
            self.env.output_pipe("example: workspace C:\\project my_work")
            return

        input_args = args[0]
        input_args[0] = input_args[0].replace(":", ":\\")
        if os.path.isdir(input_args[0]) and len(input_args) > 1:
            self.workspaces[input_args[1]] = input_args[0]
            self.sync()
            return [input_args[0]]
        elif not os.path.isdir(input_args[0]) and input_args[0] in self.workspaces:
            return [self.workspaces[input_args[0]]]
        elif input_args[0] == '' and input_args[1] in self.workspaces:
            self.env.output_pipe("Invalidating ", input_args[1])
            del self.workspaces[input_args[1]]
            self.sync()
            return ['']
        else:
            raise Exception("No such workspace!")

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = WorkspaceModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return WorkspaceModule.getInstance(env)
