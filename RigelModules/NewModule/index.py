
class ModuleGenerator:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        self.point_lib = env.secure_load("PointModule")
        env.callback_manager.registerCallback("envChange", self)
        self.pathlib = env.secure_load("pathlib")
        self.os = env.secure_load("os")
        self.shutil = env.secure_load("shutil")


    def onEnvChange(self, new_env):
        self.env = new_env

    def exec(self, *args):

        name = args[0][0]
        name = name.lower()
        cpath = str(self.pathlib.Path().absolute())

        template = open("./RigelModules/NewModule/module.sample", "r")
        template_text = template.read()
        template.close()

        index_content = template_text.replace("%%module_name%%", name.capitalize())
        if self.os.path.exists("./RigelModules/" + name):
            resp = input("warning! module " + name + " already exists, overwrite? y/n\n")
            if (resp.lower() != "y"):
                raise Exception("User refused to overwrite!")
            self.shutil.rmtree(cpath + "\\RigelModules\\" + name)
        self.os.mkdir(cpath + "\\RigelModules\\" + name.capitalize() +"Module" + "\\")
        index_path = cpath + "\\RigelModules\\" + name.capitalize() + "Module" + "\\index.py"
        index = open(index_path, "w")
        index.write(index_content)
        index.close()

        head = open("head.data", "r")
        hcontents = head.readlines()
        module_exists = len([module for module in hcontents if module.startswith(name + " ")]) > 0
        if not module_exists:
            head.close()
            head = open("head.data", "a")
            head.write("\n")
            head.write(" ".join(args[0]))
        head.close()

        self.point_lib.exec([index_path], "")
        self.env.output_pipe(name+" Module Created")

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = ModuleGenerator(env)
        return cls.__module_instance


def getModuleInstance(env):
    return ModuleGenerator.getInstance(env)
