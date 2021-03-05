class LogModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        env.callback_manager.registerCallback("envChange", self)
        self.logStr = ""
        self.memory = None
        self.activated = True

    def onEnvChange(self, new_env):
        self.env = new_env

    def log(self, text):
        self.logStr += text+"\n"

    def exec(self, *args):
        to_log = " ".join(args[0])

        remainder = args[1]
        if to_log == "" and len(remainder) > 0:
            remainder = [str(x) for x in remainder]
            to_log = "\n".join(remainder)
            print("took reminders as log source ",to_log)
        else:
            print(to_log, remainder)

        if len(to_log) == 0 and len(remainder) == 0:
            return [self.logStr]

        if type(to_log) is list:
            to_log = [str(x) for x in to_log]
            to_log = " ".join(to_log)
        if to_log.lower() == "save":
            self.store()
            self.env.output_pipe("Log flushed to disk")
            return []

        if to_log == "clean":
            self.logStr = ""
            self.env.output_pipe("RAM Log cleaned")
            return []
        if to_log == "clean all":
            mem = open("./RigelModules/log/memory.data", "w+")
            mem.close()
            return []
        if to_log.lower() == "on":
            self.activated = True
            return []
        elif to_log.lower() == "off":
            self.activated = False
            return []

        if to_log.lower() == "all":
            mem = open("./RigelModules/log/memory.data", "r")
            to_return = mem.read()
            mem.close()
            return [to_return]
        if self.activated:
            self.log(to_log)

        return [self.logStr]

    def store(self):
        mem = open("./RigelModules/log/memory.data", "a")
        mem.write("------\n")
        mem.write(self.logStr)
        mem.close()

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = LogModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return LogModule.getInstance(env)
