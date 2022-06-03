import threading
from threading import Thread
import time

import tkinter

stop = False
pause = False


def counting():
    cnt = 0
    while not stop:
        while not stop and pause:
            pass
        txt.config(text=cnt)

        cnt += 1
        time.sleep(0.5)

    print('stopped')


def abort():
    global pause
    global stop
    global a
    while True:
        c = input()
        pause = True
        c = input("1-resume, 2-abort")
        if c == '2':
            c = input("1-restart, 2-terminate")
            stop = True
            a.join()
            if c == '2':
                break
            else:
                stop = False
                ...
                a = threading.Thread(target=counting)
                a.start()

        pause = False


tk = tkinter.Tk()
txt = tkinter.Button(tk)
txt.pack()

a = Thread(target=counting)
a.start()
b = Thread(target=abort)
b.start()

tk.mainloop()
