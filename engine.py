import _thread
import importlib
import shlex
import traceback
import subprocess
import os
import json
from tkinter import *


class CallbackManager:
    def __init__(self):
        self.registry = {}

    def emit(self, event, input_str=""):
        if event not in self.registry:
            return

        for listener in self.registry[event]:
            try:
                method_to_call = getattr(listener, event)
                method_to_call(input_str)
            except Exception as e:
                print(e)
                pass

    def registerCallback(self, event, instance):
        if event not in self.registry:
            self.registry[event] = []
        if instance not in self.registry[event]:
            self.registry[event].append(instance)

    def unregisterCallback(self, event, instance):
        if event not in self.registry:
            self.registry[event] = []
        if instance in self.registry[event]:
            self.registry[event].remove(instance)


class VirtualEnvironment:

    def __init__(self, lib_finder, callback_manager, className):
        self.secure_load = lambda name: lib_finder.getLibSecure(name, className)
        self.to_module_name = lambda name: name.lower().capitalize()+"Module"
        self.callback_manager = callback_manager
        self.output_pipe = lambda *args: Brain.output(*args)


class Environment:
    __env_instance = None

    def __init__(self, lib_finder, callback_manager):
        self.lib_finder = lib_finder
        self.callback_manager = callback_manager
        self.output_pipe = lambda *args: Brain.output(*args)

    @classmethod
    def getInstance(cls, lib_finder=None, callback_manager=None):
        if cls.__env_instance is None:
            cls.__env_instance = Environment(lib_finder, callback_manager)
        return cls.__env_instance

    def getVirtualEnvFor(self, className):
        return VirtualEnvironment(lib_finder=self.lib_finder, callback_manager=self.callback_manager,
                                  className=className)


class LibFinder:
    __loaded_libs = {}

    def loadManifest(self, className):
        manifest_content = None

        name = className
        if os.path.isfile("./RigelModules/" + name + "/index.py") and os.path.isfile(
                "./RigelModules/" + name + "/manifest.json"):
            with open("./RigelModules/" + name + "/manifest.json") as manifest:
                manifest_content = json.loads(manifest.read())
        else:
            raise Exception("Manifest or module not found for "+className)
        return manifest_content

    def getLibSecure(self, name, className):
        def __loadLib(name, className):
            manifest = self.loadManifest(className)
            print("Testing manifest of",className," for ", name, manifest)
            if (manifest is None) or (manifest['imports'] is None) or (
                    name not in manifest['imports'] and "*" not in manifest["imports"]):
                raise Exception("Manifest Rejected!")

            print("Manifest accepted", className)
            if os.path.isfile("./RigelModules/" + name + "/index.py"):
                module = importlib.import_module("RigelModules." + name + ".index")
                virtual_env = Environment.getInstance().getVirtualEnvFor(name)
                module = module.getModuleInstance(virtual_env)
            else:
                module = importlib.import_module(name)
            return module

        if name in LibFinder.__loaded_libs and className in LibFinder.__loaded_libs[name]:
            return LibFinder.__loaded_libs[name][className]
        else:
            lib = __loadLib(name, className)
            if lib is not None:
                if name not in LibFinder.__loaded_libs:
                    LibFinder.__loaded_libs[name] = {}
                LibFinder.__loaded_libs[name][className] = lib
                return lib
            return



    def clearCache(self):
        LibFinder.__loaded_libs.clear()

    def installLib(self, code=None, path=None):
        if code is not None:
            # attempt to load via repo
            return
        elif path is not None:
            # attempt to install via file
            return
        else:
            print("Nothing to install")
            return -1


class ContextScanner:
    def __init__(self):
        print("init")

    def getContext(self, sequence):
        return "question"


class ResearchResults:
    def __init__(self):
        pass


class Brain:
    BRAIN_INSTANCE = None

    def __init__(self):
        f = open("head.data", "r")  # fix
        self.raw_cmds = [shlex.split(x) for x in f.read().split("\n")]
        self.cmds = [x[0] for x in self.raw_cmds]
        f.close()
        self.nlp_model = ContextScanner()
        self.process_controller = subprocess
        self.lib_finder = LibFinder()
        self.callback_manager = CallbackManager()
        self.env = Environment.getInstance(lib_finder=self.lib_finder, callback_manager=self.callback_manager)
        self.stream = None
        self.callback_manager.registerCallback("oninput", self)
        self.callback_manager.registerCallback("onexit", self)
        self.callback_manager.registerCallback("onminimize", self)

    def acknowledge(self, event, input_str=""):
        _thread.start_new_thread(self.callback_manager.emit, (event, input_str))

    def onminimize(self, *args):
        print("minimized")
        return

    def onexit(self, *args):
        _thread.interrupt_main()

    def oninput(self, sequence):
        sequence = sequence.replace("\\", '\\\\')
        result = self.analyze(sequence)
        if result < 0:
            print("executing", sequence)
            result = self.execute(sequence)
        elif result > 0:
            result = self.research(sequence)

        # Brain.output(result)
        return result

    def analyze(self, sequence):
        if shlex.split(sequence)[0] in self.cmds:
            return -1
        else:
            return 1

    def execute(self, sequence):
        sequence_sep = " then "
        sequences = sequence.split(sequence_sep)
        _returned = []
        for each_seq in sequences:
            each_seq = each_seq.strip()
            lib_name = shlex.split(each_seq)[0]
            lib_name = lib_name.lower().capitalize()+"Module"
            lib = self.lib_finder.getLibSecure(lib_name, Brain.__name__+"Module")
            if lib is not None:
                try:
                    args = shlex.split(each_seq)[1:]
                    print("exec on lib " + lib_name, args, _returned)
                    _returned = _returned if _returned is not None else []
                    _returned = lib.exec(args, _returned)
                except Exception as e:
                    print(e)
                    Brain.output("Exception occurred at execution, check the logs")
                    traceback.print_tb(e.__traceback__)
        return _returned

    def research(self, sequence):
        return []

    def output(*args):
        print(*args)
        if Brain.getBrain().stream is None:
            print(*args)
        else:
            try:
                output_string = ">>"
                for arg in args:
                    if arg is not None:
                        output_string += str(arg)
                output_string += "\n"
                if output_string != ">>\n":
                    Brain.getBrain().stream(output_string)
            except Exception as e:
                Brain.getBrain().stream(">> There was an error in execution")

    def set_output_stream(self, stream):
        self.stream = stream

    @staticmethod
    def getBrain():
        if Brain.BRAIN_INSTANCE is None:
            Brain.BRAIN_INSTANCE = Brain()
        return Brain.BRAIN_INSTANCE


class GUI:
    def __init__(self, brain):
        self.isHidden = False
        self.brain = brain
        self.root = Tk()
        self.root.geometry("350x190+1175+10")
        self.root.resizable(0, 0)
        self.root.overrideredirect(1)

        self.root.attributes("-alpha", 0.7)
        back = Frame(self.root, bg="#3c3c3c")
        back.pack_propagate(0)
        back.pack(fill=BOTH, expand=1)
        back.bind("<Enter>", lambda x: self.root.attributes("-alpha", 1))
        back.bind("<Leave>", lambda x: self.root.attributes("-alpha", 0.7))
        self.back = back
        self.text_input = Text(back, bg="#232323", fg="white", borderwidth=2, relief="groove")
        self.text_input.place(x=10, y=145, width=280, height=30)
        self.text_input.config(padx=5, pady=5)
        self.text_input.config(insertbackground="white", font="Arial 10")
        self.text_input.bind('<Return>',
                             lambda x="": (
                                 self.brain.acknowledge("oninput", self.text_input.get("1.0", END)), self.clearEntry()))

        self.go = Button(back, text="GO", bg="#3c3c3c", fg="white",
                         command=lambda x="": (
                             self.brain.acknowledge("oninput", self.text_input.get("1.0", END)), self.clearEntry()),
                         borderwidth=0,
                         relief="groove")
        self.go.place(x=300, y=150, width=35, height=23)

        self.brain.set_output_stream(lambda x: self.output_method(x))
        self.monitor = Text(self.back, borderwidth=0, bg="#3c3c3c", fg="white", relief="solid")
        self.monitor.place(x=10, y=30, width=280, height=100)
        self.monitor.config(insertbackground="white")
        self.monitor.insert(END, ">>")
        # self.monitor.delete('1.0', END)
        self.monitor.configure(state="disabled")

        top_Frame = Frame(back, bg="#3c3c3c")
        top_Frame.place(x=0, y=0, anchor="nw", width=350, height=20)
        #
        grip = Grip(top_Frame)
        Ext_but = Button(top_Frame, text="_", bg="red", fg="white",
                         command=lambda: (self.hide(), self.brain.acknowledge("onminimize")),
                         borderwidth=0)
        Ext_but.place(x=320, y=0, anchor="nw", width=30, height=20)

        self.root.lift()
        self.root.attributes('-topmost', True)
        # self.root.after_idle(self.root.attributes, '-topmost', False)

    def start(self):
        self.root.mainloop()

    def output_method(self, input_string):
        if type(input_string) == "str" or True:  # fix string check
            self.monitor.configure(state="normal")
            self.monitor.insert("end", input_string)
            self.monitor.configure(state="disabled")

    def hide(self):
        self.isHidden = True
        self.root.withdraw()

    def show(self):
        self.isHidden = False
        self.root.deiconify()
        self.root.lift()

    def clearEntry(self):
        self.text_input.delete('1.0', END)


class Grip:
    ''' Makes a window dragable. '''

    def __init__(self, parent, disable=None, releasecmd=None):
        self.parent = parent
        self.root = parent.winfo_toplevel()

        self.disable = disable
        if type(disable) == 'str':
            self.disable = disable.lower()

        self.releaseCMD = releasecmd

        self.parent.bind('<Button-1>', self.relative_position)
        self.parent.bind('<ButtonRelease-1>', self.drag_unbind)

    def relative_position(self, event):
        cx, cy = self.parent.winfo_pointerxy()
        geo = self.root.geometry().split("+")
        self.oriX, self.oriY = int(geo[1]), int(geo[2])
        self.relX = cx - self.oriX
        self.relY = cy - self.oriY

        self.parent.bind('<Motion>', self.drag_wid)

    def drag_wid(self, event):
        cx, cy = self.parent.winfo_pointerxy()
        d = self.disable
        x = cx - self.relX
        y = cy - self.relY
        if d == 'x':
            x = self.oriX
        elif d == 'y':
            y = self.oriY
        self.root.geometry('+%i+%i' % (x, y))

    def drag_unbind(self, event):
        self.parent.unbind('<Motion>')
        if self.releaseCMD != None:
            self.releaseCMD()
