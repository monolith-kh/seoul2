# -*- coding: utf-8 -*-

import socket
from _thread import *
import threading
from tkinter import *
from time import sleep
from struct import pack

def send(socket):
    global go_send
    while True:
        if go_send:
            socket.send(pack('hhhhhhh', check_vcu.get(), check_actioncam.get(), check_nfc.get(), check_imu.get(), check_battery.get(), check_brake.get(), check_gps.get()))
            go_send = False
        else:
            if go_out:
                socket.close()
                exit()
            sleep(0.1)

def receive(socket):
    first = True
    while True:
        try:
            data = socket.recv(1024)
            chat_log['state'] = 'normal'
            if first: # 이걸 처음 체크 이후 의미없이 매번 체크하므로 이렇게 하는 건 효율적이지 않음.
                chat_log.insert("end",str(data.decode( )))
                first = False
            else:
                chat_log.insert("end",'\n' + str(data.decode()))
                chat_log.see('end')
            chat_log['state'] = 'disabled'
        except (OSError, ConnectionAbortedError):
            chat_log['state'] = 'normal'
            chat_log.insert("end", '\n[System] Teminate display connection.\n')
            chat_log.see('end')
            chat_log['state'] = 'disabled'
            exit()

def login():
    # 서버의 ip주소 및 포트
    HOST = ip_entry.get(); PORT = int(port_entry.get())
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    threading.Thread(target=send, args= (client_socket,)).start()
    threading.Thread(target=receive, args= (client_socket,)).start()
    exit()

def try_login():
    global go_out
    start_new_thread(login,())
    login_button['state'] = 'disabled'
    logout_button['state'] = 'active'
    ip_entry['state'] = 'readonly'
    port_entry['state'] = 'readonly'
    go_out = False

def try_logout():
    global go_out
    login_button['state'] = 'active'
    logout_button['state'] = 'disabled'
    ip_entry['state'] = 'normal'
    port_entry['state'] = 'normal'
    go_out = True

def set_go_send(event):
    global go_send
    go_send = True

go_out, go_send = False, False
c_root = Tk()
c_root.geometry('500x500+50+50')
c_root.title('seoul - GR VMU mockup')
c_root.resizable(True, True)

''' Top Menu '''
Label(c_root, text = 'Server IP : ').place(x=20, y=20)
Label(c_root, text = 'Port : ').place(x=250, y=20)
ip_entry = Entry(c_root, width=14); ip_entry.place(x=83, y=21)
ip_entry.insert(0,'127.0.0.1')
port_entry = Entry(c_root, width=5); port_entry.place(x = 290, y=21)
port_entry.insert(0,'9999')
login_button = Button(c_root,text='Log In', command=try_login); login_button.place(x=350, y=18)
logout_button = Button(c_root,text='Log Out',state = 'disabled', command = try_logout); logout_button.place(x=420, y=18)

''' Middle Menu '''
chat_frame = Frame(c_root)
scrollbar = Scrollbar(chat_frame) ; scrollbar.pack(side='right',fill='y')
chat_log = Text(chat_frame, width = 62, height = 24, state = 'disabled', yscrollcommand = scrollbar.set) ; chat_log.pack(side='left')#place(x=20, y=60)
scrollbar['command'] = chat_log.yview
chat_frame.place(x=20, y=60)

''' test vmu button '''
check_vcu = IntVar()
vcu_button = Checkbutton(c_root, text='VCU', variable=check_vcu, command=lambda: set_go_send(None))
vcu_button.place(x=0, y=405)

check_actioncam = IntVar()
actioncam_button = Checkbutton(c_root, text='ACTIONCAM', variable=check_actioncam, command=lambda: set_go_send(None))
actioncam_button.place(x=60, y=405)

check_nfc = IntVar()
nfc_button = Checkbutton(c_root, text='NFC', variable=check_nfc, command=lambda: set_go_send(None))
nfc_button.place(x=160, y=405)

check_imu = IntVar()
imu_button = Checkbutton(c_root, text='IMU', variable=check_imu, command=lambda: set_go_send(None))
imu_button.place(x=220, y=405)

check_battery = IntVar()
battery_button = Checkbutton(c_root, text='BATTERY', variable=check_battery, command=lambda: set_go_send(None))
battery_button.place(x=280, y=405)

check_brake = IntVar()
brake_button = Checkbutton(c_root, text='BRAKE', variable=check_brake, command=lambda: set_go_send(None))
brake_button.place(x=370, y=405)

check_gps = IntVar()
gps_button = Checkbutton(c_root, text='GPS', variable=check_gps, command=lambda: set_go_send(None))
gps_button.place(x=440, y=405)

''' Bottom Menu '''
close_button = Button(c_root,text='Close',command=exit); close_button.place(x=200, y = 460)

c_root.mainloop()

