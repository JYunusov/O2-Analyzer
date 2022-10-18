import os
import threading
import RPi.GPIO as GPIO
import serial

from time import *
from time import sleep
from time import strftime
import time
from tkinter import *
from PIL import ImageTk, Image




sys_check = Tk()
sys_check.configure(bg='white', cursor=NONE)
sys_check.attributes('-fullscreen', True)


def run_systemcheck():
    time.sleep(0.5)
    sys_ready.config(text="running...", fg='red')
    
    
    def rs485_hat():
        rs485 = os.system("dmesg | grep -i '\(can\|spi\)'")
        
        if rs485 == rs485:
            print(rs485)
            print('\nconnected')
            rs485_data.config(text="connected", fg='green')
        elif rs485!= rs485:
            print(rs485)
            print('\nconfg err')
            rs485_data.config(text="confg err")
        time.sleep(0.5)
    rs485_hat()
    
         
    def sys_select_device():
        global rmv_char
        ser = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
        ser.write(b'! \r\n')
        time.sleep(0.1)
        ser.write(b'! 5\r\n')
        
        data = ser.readall().decode().strip().replace('! ', '')
        rmv_char = data.replace("0", '')
        device_data.config(text=rmv_char, fg='green')

        print('\ndevice', rmv_char)
        time.sleep(0.5)
    sys_select_device()
    

    def sys_oxygen_data():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        Relay_Ch1 = 26
        GPIO.setup(Relay_Ch1, GPIO.OUT)

        try:
            GPIO.output(Relay_Ch1, GPIO.LOW)
            for i in range(15):
                ser2 = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
                ser2.write(b'Z\r\n')
                data = ser2.readall().decode().strip().replace('Z ', '')
                
                flt = float(data) / 1000
                print("\noxygen :", flt, "%")
                oxy_data.config(text=flt, fg='green')

            GPIO.output(Relay_Ch1, GPIO.HIGH)
            GPIO.cleanup()
            time.sleep(0.5)

            print("\n[status: ready]")
            sys_ready.config(text="READY", fg='medium blue')
            start_btn.config(state=ACTIVE)
        except:
            print("\nnot ready")
            device_data.config(text="none", fg='red')
            oxy_data.config(text="none", fg='red')
            sys_ready.config(text="NOT READY", fg='red')
    sys_oxygen_data()


def date_time():
    dt_lbl.config(text=strftime('%a ' ' %b ' ' %d\n' ' %X ' '%p'))
    dt_lbl.after(1000, date_time)
    
dt_lbl = Label(sys_check, bg='snow', fg='gray14', font=("Helvetica", 50, 'bold'))
dt_lbl.place(x=380, y=150)
date_time()


def sys_thread():
    global sys_t1
    sys_t1 = threading.Thread(target=run_systemcheck)
    sys_t1.start()
    sys_check.after(1000, refresh_sys)

def refresh_sys():
    if sys_t1.is_alive():
        sys_check.after(1000, refresh_sys)
                    
def start_sys():
    sys_thread()
start_sys()

def close():
    sys_check.destroy()


# Widgets/Labels
unit_lbl = Label(sys_check, text="TS Oxygen Analyzer (Model 1).", bg='white', font=("Helvetica", 14, 'bold'))
unit_lbl.place(x=90, y=5)

bridge_lbl = Label(sys_check, text="(c) 2021 Bridge Analyzers, All Rights Reserved.", bg='white', font=("Helvetica", 14, 'bold'))
bridge_lbl.place(x=90, y=40)

f = Label(sys_check, text='System Check', bg='snow', font=("Helvetica", 15, 'bold'))
f.place(x=5, y=120)

s_frm = LabelFrame(sys_check, text='System', bg='snow', bd=1, width=150, height=70, font=("Helvetica", 15, 'bold'))
s_frm.place(x=5, y=400)

dev_lbl = Label(sys_check, text="[ devices ]", fg='medium blue', bg='snow', font=("Helvetica", 15))
dev_lbl.place(x=10, y=150)

status_lbl = Label(sys_check, text="[ status ]", fg='medium blue', bg='snow', font=("Helvetica", 15))
status_lbl.place(x=180, y=150)

rs485_lbl = Label(sys_check, text="rs485:", bg='snow', font=("Helvetica", 15))
rs485_lbl.place(x=10, y=200)

rs485_data = Label(sys_check, bg='snow', font=("Helvetica", 15))
rs485_data.place(x=180, y=200)

device_lbl1 = Label(sys_check, text="device:", bg='snow', font=("Helvetica", 15))
device_lbl1.place(x=10, y=250)

device_data = Label(sys_check, bg='snow', font=("Helvetica", 15))
device_data.place(x=180, y=250)

oxygen_lbl1 = Label(sys_check, text="oxygen:", bg='snow', font=("Helvetica", 15))
oxygen_lbl1.place(x=10, y=300)

oxy_data = Label(sys_check, bg='snow', font=("Helvetica", 15))
oxy_data.place(x=180, y=300)

sys_ready = Label(s_frm, bg='snow', font=("Helvetica", 16))
sys_ready.place(x=10, y=0)

canvas1 = Canvas(sys_check, width=300, height=2)
canvas1.place(x=5, y=110)

canvas = Canvas(sys_check, width=300, height=2)
canvas.place(x=5, y=340)

start_btn = Image.open("/home/pi/Documents/MAP/Buttons/power-80.png")
start = ImageTk.PhotoImage(start_btn)
start_btn = Button(sys_check, text="Start System", compound=TOP, image=start, state=DISABLED,
                    command=close, bd=0, highlightthickness=0, bg='white',
                    activebackground='white', font=('Helvetica', 12, 'bold'))
start_btn.place(x=200, y=360)

bridge_logo = Image.open("/home/pi/Documents/MAP/Buttons/bridge2.png")
bridge = ImageTk.PhotoImage(bridge_logo)
bridge_img = Label(sys_check, image=bridge, bd=0, bg='white')
bridge_img.place(x=5, y=5)

sys_check.mainloop()
