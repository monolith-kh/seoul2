# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.font

from PIL import Image, ImageTk
from itertools import count, cycle

import socket
from _thread import *
import threading

from datetime import datetime

from struct import unpack


SIZE = (1920, 1080)

HOST = '127.0.0.1'
PORT = 9999

GREEN_COLOR = '#4d6b53'

client_vmu = None
server_socket = None

vcu = 0
actioncam = 0
nfc = 0
imu = 0
battery = 0
brake = 0
gps = 0


def update_status():
    if vcu:
        status_vcu.config(foreground=GREEN_COLOR, relief='flat')
    else:
        status_vcu.config(foreground='red', relief='sunken')
    if actioncam:
        status_actioncam.config(foreground=GREEN_COLOR, relief='flat')
    else:
        status_actioncam.config(foreground='red', relief='sunken')
    if nfc:
        status_nfc.config(foreground=GREEN_COLOR, relief='flat')
    else:
        status_nfc.config(foreground='red', relief='sunken')
    if imu:
        status_imu.config(foreground=GREEN_COLOR, relief='flat')
    else:
        status_imu.config(foreground='red', relief='sunken')
    if battery:
        status_battery.config(foreground=GREEN_COLOR, relief='flat')
    else:
        status_battery.config(foreground='red', relief='sunken')
    if brake:
        status_brake.config(foreground=GREEN_COLOR, relief='flat')
    else:
        status_brake.config(foreground='red', relief='sunken')
    if gps:
        status_gps.config(foreground=GREEN_COLOR, relief='flat')
    else:
        status_gps.config(foreground='red', relief='sunken')


def threaded(client_socket, addr):
    global display_log
    global vcu
    global actioncam
    global nfc
    global imu
    global battery
    global brake
    global gps
    display_log['state'] = 'normal'
    display_log['text'] = '{}\tConnected by: {}:{}'.format(str(datetime.utcnow()), addr[0], addr[1])
    while True:
        try:
            data = client_socket.recv(1024)
            vcu, actioncam, nfc, imu, battery, brake, gps = unpack('hhhhhhh', data)
            display_log['text'] = '{}\tReceived from {}:{} :: {}'.format(str(datetime.utcnow()), addr[0], addr[1], str(data))
            update_status()
            if not data:
                client_vmu = None
                display_log['text'] = '{}\tDisconnected by: {}:{}'.format(str(datetime.utcnow()), addr[0], addr[1])
                display_log['state'] = 'disabled'
                break
        except (Exception, ConnectionResetError):
            client_vmu = None
            display_log['text'] = '{}\tDisconnected by: {}:{}'.format(str(datetime.utcnow()), addr[0], addr[1])
            display_log['state'] = 'disabled'
            break
        except:
            print('unknown error')
            break
    client_socket.close()


def server_open():
    start_new_thread(make_server, ())
    start_button['state'] = 'disabled'
    display_log['state'] = 'active'
    display_log['text'] = '{}\tstart display(server)'.format(str(datetime.utcnow()))


def make_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    while True:
        client_socket, addr = server_socket.accept()
        client_vmu = client_socket
        start_new_thread(threaded, (client_vmu, addr))


class ImageLabel(tk.Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    """
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        frames = []

        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)

        try:
            self.delay = 100
            #self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('seoul - GR display')
    root.geometry('{}x{}'.format(SIZE[0], SIZE[1]))
    root.resizable(False, False)
    root.attributes('-fullscreen', True)

    top_frame = tk.Frame(root)
    top_frame.pack(side=tk.TOP)

    host_label = tk.Label(top_frame, text='Server IP: {}:{}'.format(HOST, PORT))
    host_label.pack(side=tk.LEFT, expand=True,  fill=tk.BOTH, anchor=tk.N)
    start_button = tk.Button(top_frame, text='Start Display', command=server_open)
    start_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH,  anchor=tk.N)
    display_log = tk.Label(top_frame, text='log', state='disabled')
    display_log.pack(side=tk.RIGHT, expand=True,  fill=tk.BOTH,  anchor=tk.N)

    center_frame = tk.Frame(root, relief='solid', bd=2)
    center_frame.pack()

    lbl_1 = ImageLabel(center_frame)
    lbl_1.pack()
    lbl_1.load('./images/rabbit_car_480px.gif')

    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM)

    status_font = tkinter.font.Font(family='Arial', size=32)

    status_vcu = tk.Label(bottom_frame, text='VCU', background='gray', font=status_font, padx=10, pady=5)
    status_vcu.pack(side=tk.LEFT)
    status_actioncam = tk.Label(bottom_frame, text='ACTIONCAM', background='gray', font=status_font, padx=10, pady=5)
    status_actioncam.pack(side=tk.LEFT)

    status_nfc = tk.Label(bottom_frame, text='NFC', background='gray', font=status_font, padx=10, pady=5)
    status_nfc.pack(side=tk.RIGHT)
    status_imu = tk.Label(bottom_frame, text='IMU', background='gray', font=status_font, padx=10, pady=5)
    status_imu.pack(side=tk.RIGHT)
    status_battery = tk.Label(bottom_frame, text='BATTERY', background='gray', font=status_font, padx=10, pady=5)
    status_battery.pack(side=tk.RIGHT)
    status_brake  = tk.Label(bottom_frame, text='BRAKE', background='gray', font=status_font, padx=10, pady=5)
    status_brake.pack(side=tk.RIGHT)
    status_gps = tk.Label(bottom_frame, text='GPS', background='gray', font=status_font, padx=10, pady=5)
    status_gps.pack(side=tk.RIGHT)

    start_button.invoke()

    root.mainloop()

