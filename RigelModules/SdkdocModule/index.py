import os


class SdkdocModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        env.callback_manager.registerCallback("envChange", self)

    def onEnvChange(self, new_env):
        self.env = new_env

    def exec(self, *args):
        _input = args[0]
        _remainders = args[0]

        result = []
        if len(_input) > 0:
            for module in _input:
                result.append(self.getDoc(module))
        elif len(_remainders) > 0:
            for module in _remainders:
                result.append(self.getDoc(module))
        else:
            self.env.output_pipe("Incorrect use of 'sdkdoc'")

        return result

    def getDoc(self, module_name):
        if os.path.exists('./RigelModules/' + module_name + "/" + module_name + ".sdkdoc"):
            f = open('./RigelModules/' + module_name + "/" + module_name + ".sdkdoc", "r")
            contents = f.read()
            f.close()
            return contents
        return module_name + " is not documented\n"

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = SdkdocModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return SdkdocModule.getInstance(env)
