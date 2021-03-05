"""
from win32com.client import Dispatch
from win32gui import GetClassName

ShellWindowsCLSID = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
ShellWindows = Dispatch ( ShellWindowsCLSID )


"""
from win32com.client import Dispatch
from win32gui import GetClassName
ShellWindowsCLSID = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'

import os
class ExplorerTracker:
    __module_instance = None



    def __init__(self, env):

        self.env = env
        env.callback_manager.registerCallback("envChange",self)
        print("ExplorerTracker loaded")
        self.run_lib = env.secure_load("run")


    def onEnvChange(self,new_env):
        self.env = new_env
        pass


    def exec(self, *args):
        ShellWindows = Dispatch(ShellWindowsCLSID)
        for x in ShellWindows:
            print(GetClassName(x.HWND),x)


    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = ExplorerTracker(env)
        return cls.__module_instance


def getModuleInstance(env):

    return ExplorerTracker.getInstance(env)
