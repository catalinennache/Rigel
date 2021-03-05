class RubberduckModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        env.callback_manager.registerCallback("envChange", self)

    def onEnvChange(self, new_env):
        self.env = new_env

    def exec(self, *args):
        pass

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = RubberduckModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return RubberduckModule.getInstance(env)
