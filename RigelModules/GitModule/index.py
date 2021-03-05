import os
import traceback
import shlex


class GitModule:
    __module_instance = None

    def __init__(self, env):
        self.env = env
        env.callback_manager.registerCallback("envChange", self)
        self.runModule = env.secure_load("RunModule")
        self.logger = env.secure_load("LogModule")
        self.working_directory = None
        self.working_directory_treestamp = None
        self.treestamp = env.secure_load("TreestampModule")
        self.powerShellModule = self.env.secure_load("PowershellModule")
        success = self.runModule.runAndWait(["git"])

        if not success:
            self.env.output_pipe("Git exe is not installed in your system!")
            self.logger.log("Failed in instantiating GitModule! Git exe is not installed or not added to PATH")
            raise Exception("No git executable found!")

    def onEnvChange(self, new_env):
        self.env = new_env

    def exec(self, *args):
        input_args = args[0]
        remainders = args[1]
        error = ""
        if len(input_args) == 0 and len(remainders) == 0:
            self.env.output_pipe("No command! Launching documentation")
            doc = self.env.secure_load("DocumentationModule").exec(["git"], [])
            self.env.secure_load("ShowModule").exec(doc, [])
            return []

        if len(input_args) != 0:
            if input_args[0] == "wd":
                return [self.working_directory if self.working_directory is not None else ""]
            if input_args[0] == "use" and len(input_args) > 1:
                path = ""
                if os.path.isabs(input_args[1]):
                    path = input_args[1]
                else:
                    try:
                        potential_lib = input_args[1]
                        potential_lib = self.env.to_module_name(potential_lib)
                        module = self.env.secure_load(potential_lib)
                        print("Module ", module)
                        if module is not None:
                            result = module.exec(input_args[2:], [])
                            print(result)
                            if len(result) > 0:
                                path = result[0]
                            else:
                                error = potential_lib + " didn't return anything."
                        else:
                            error = "Module " + potential_lib + " not found."
                    except:
                        error = "Error in loading " + input_args[1] + " module."

                if path != "" and os.path.isabs(path):
                    self.working_directory = path
                    self.env.output_pipe("Working directory set!")
                    self.logger.log("GIT >> Working directory set! " + path)
                    if self.isGitRepo(self.working_directory):
                        self.working_directory_treestamp = set(self.treestamp.exec([self.working_directory], []))
                        return [self.working_directory]
                    else:
                        self.env.output_pipe("Warning!\n Current WD is not a git repo.\nTreestamp not generated!")
                # do something with error
                return []

            if not self.isGitRepo(self.working_directory):
                self.env.output_pipe("Current WD is not a git repo, ignoring command!")
                return []

            if input_args[0] == "add":
                out, err = self.runGitCommand("git add -A -n")
                result = out.decode("utf-8")
                print(result)
                if len(result) > 0:
                    results = [shlex.split(x)[1] for x in result.strip("\n").split("\n")]
                else:
                    results = []
                if len(results) != 0:
                    tmp = ["Keep the files you want to add!"]
                else:
                    tmp = ["Nothing to add!"]

                tmp.extend(results)
                results = tmp
                editToastModule = self.env.secure_load("EditModule")
                results = editToastModule.exec([], results)[0].split("\n")
                added = 0
                for result in results:
                    if result == "" or result == "Nothing to add!" or result == "Keep the files you want to add!":
                        continue
                    self.runGitCommand("git add '" + result + "'")
                    added += 1
                if added > 0:
                    self.env.output_pipe(str(added) + " files were added, commit when you're ready!")
                else:
                    self.env.output_pipe("No files were added!")

    def isGitRepo(self, absolute_path=None):
        command = "git branch"
        absolute_path = absolute_path if absolute_path is not None else self.working_directory
        if absolute_path is None:
            self.env.output_pipe("WD is not set!\nIgnoring command!")
            return ""

        command = command.split(" ")
        raw_commands = ['cd', absolute_path, ' ; ']
        raw_commands.extend(command)
        out, err = self.powerShellModule.runAndWaitWithOutput(raw_commands, stdout=True, stderr=True)

        res = err.decode("utf-8")
        try:
            return "fatal: not a git repository (or any of the parent directories):" not in res
        except Exception as e:
            traceback.print_tb(e.__cause__)
            return True

    def runGitCommand(self, command):
        if self.working_directory is None:
            self.env.output_pipe("WD is not set!\nIgnoring command!")
            return ""
        if command == "":
            self.env.output_pipe("No command to run!")
            return ""

        command = command.split(" ")
        raw_commands = ['cd', self.working_directory, ' ; ']
        raw_commands.extend(command)
        return self.powerShellModule.runAndWaitWithOutput(raw_commands, stdout=True, stderr=True)

    @classmethod
    def getInstance(cls, env):
        if cls.__module_instance is None:
            cls.__module_instance = GitModule(env)
        return cls.__module_instance


def getModuleInstance(env):
    return GitModule.getInstance(env)


def listToDict(lst):
    dct = {}
    for cell in lst:
        dct[cell] = True
    return True
