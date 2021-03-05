import engine
import pynput


def on_press(key):
    if str(key) == "'\\x08'":
        program.show()


listener = pynput.keyboard.Listener(on_press=on_press)
listener.start()
BRAIN = engine.Brain.getBrain()
program = engine.GUI(BRAIN)
program.start()



# def change():
#     def go():
#         for i in range(150, 301, 2):
#             root.geometry("400x" + str(i) + "+" + str(root.winfo_x()) + "+" + str(root.winfo_y() - 2))
#             text_input.place(x=10, y=i - 30, width=300, height=20)
#
#     _thread.start_new_thread(go, ())


# while r != "exit":
#     result = BRAIN.accept(r)
#     print(result)
#     r = input(">>")
