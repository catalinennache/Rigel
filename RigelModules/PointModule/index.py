import traceback


class PointModule:
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
                print(remainder)
            else:
                remainder = ""

        if len(input_args) == 0 and (remainder is None or remainder == ""):
            raise Exception("point to_some_abs_path || find x in y then point")
        if len(input_args) == 0:
            input_args = remainder

        path_to_point = input_args[0] if len(input_args) > 0 else remainder
        if path_to_point == "":
            self.env.output_pipe("Nowhere to point!")
            return []
        try:
            print("PointM executed", 'explorer /select, "' + path_to_point + '"')
            path_to_point = path_to_point.replace('"', '')
            self.run_lib.exec(['explorer /select, "' + path_to_point + '"'], [])
        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)

    @classmethod
    def getInstance(cls, *args):
        if cls.__module_instance is None:
            cls.__module_instance = PointModule(*args)

        return cls.__module_instance


def getModuleInstance(*argv):
    return PointModule.getInstance(*argv)
