import datetime
import os
import sys
import shlex
import subprocess
import threading

from time import *
from time import sleep
import time
from tkinter import *

import RPi.GPIO as GPIO
import serial
import matplotlib
matplotlib.use("TkAgg")
from PIL import ImageTk, Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from db import create_plot
import uuid
from systemcheck import *

# creating main window
root = Tk()
root.configure(bg='white', cursor=NONE)
root.attributes('-fullscreen', True)


# status ready if system check successfull, not ready if fail
if rmv_char == '':
    systm_rdy_lbl = Label(root, text="Status: Not ready", bg='white', font=("Helvetica", 18, 'bold'))
    systm_rdy_lbl.place(x=390, y=70)
elif rmv_char == rmv_char:
    systm_rdy_lbl = Label(root, text="Status: Ready", bg='white', font=("Helvetica", 18, 'bold'))
    systm_rdy_lbl.place(x=390, y=70)

 

# adding & changing test time seconds \ user defined \ default 15
global second
secnd = IntVar()
second = IntVar()
second.set(15)

if second.get() > 15:
    second.set(secnd.get())
elif second.get() < 15:
    second.set(secnd.get())
elif second.get() != secnd.get():
    secnd.set(second.get())


def graph():
    global x, y
    global canvas, add_fig
    
    x = []
    y = []
    
    fig = Figure(figsize=(6, 4), dpi=80)
    add_fig = fig.add_subplot(1, 1, 1)
    
    add_fig.set_xlabel('Time', fontsize=12)
    add_fig.set_ylabel('Sensor Value', fontsize=12)
    add_fig.scatter(x, y, label="Sensor Values", color='Blue')
    add_fig.plot(x, y, label="Plotting Values", color='orange')
    add_fig.legend(loc='lower right', shadow=True)
     
    add_fig.grid(True)
    add_fig.set_xlim(second.get(), 0)
    add_fig.set_ylim(0, 25)

    frame1 = Frame(root, bg='white')
    frame1.place(x=0, y=100)

    canvas = FigureCanvasTkAgg(fig, frame1)
    canvas.get_tk_widget().pack()
graph()


def refresh_graph():
    x.clear()
    y.clear()
    add_fig.cla()
    
    add_fig.set_xlabel('Time', fontsize=12)
    add_fig.set_ylabel('Sensor Value', fontsize=12)
    add_fig.scatter(x, y, label="Sensor Values", color='Blue')
    add_fig.plot(x, y, label="Plotting Values", color='orange')
    add_fig.legend(loc='lower right', shadow=True)
    
    add_fig.grid(True)
    add_fig.set_xlim(second.get(), 0)
    add_fig.set_ylim(0, 25)


def sensor_data():
    time.sleep(0.5)
    refresh_graph()
    
    second_get = second.get()
    guid = uuid.uuid4()
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    Relay_Ch1 = 26
    GPIO.setup(Relay_Ch1, GPIO.OUT)
    GPIO.output(Relay_Ch1, GPIO.LOW)
    
    with open("/home/pi/Documents/MAP/Log/oxygen_data.txt", 'a') as log:
        log.write("\n")

    for i in range(second_get):
        if second_get > 0:
            second_get -= 1
                
            ser_d = serial.Serial("/dev/ttyS0", 9600, timeout=0.4)
            ser_d.write(b'Z\r\n')
                                                                            
            decode_data = ser_d.readall().decode().replace("Z", '')
            float_oxygen = float(decode_data) / 1000
            oxygen_data.configure(text="{0:.2f}".format(float_oxygen) + "%")
            
            x.append(second.get())
            y.append(str(float_oxygen))
            
            add_fig.scatter(x, y, color='Blue')
            add_fig.plot(x, y, color='orange')
            canvas.draw()
            second.set(second_get)
            
        # temperature
        ser2 = serial.Serial("/dev/ttyS0", 9600, timeout=0.1)
        ser2.write(b'T\r\n')

        decode_temp = ser2.readall().decode().replace("T", '')
        float_temp = (float(decode_temp) - 1000) / 10
        print("\n", float_oxygen, float_temp)
                    
        # log data to txt file
        with open("/home/pi/Documents/MAP/Log/oxygen_data.txt", 'a') as log:
            data_writer = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S, "),
                            float_oxygen, ', ', float_temp]
            log.writelines("%s" % line for line in data_writer)
            log.write("\n")
        
        try:
            d = {'plot_guid': guid,
                 'plot_timestamp': datetime.datetime.now(),
                 'plot_oxygen': float_oxygen,
                 'plot_temp': float_temp}
            
            create_plot(d)
        except:
            pass

    GPIO.output(Relay_Ch1, GPIO.HIGH)
    GPIO.cleanup()
    time.sleep(1)
    

def refresh_sec():
    time.sleep(1)
    second.set(secnd.get())
    
def thread_sec():
    thread_s = threading.Thread(target=refresh_sec)
    thread_s.start()

def display_time_root():
    now = datetime.datetime.now()
    time_lbl['text'] = now.strftime('Time: %X')
    date_lbl['text'] = datetime.datetime.now().strftime('Date:  %x')
    root.after(1000, display_time_root)


# widgets
time_lbl = Label(root, bg='white', font=('Helvetica', 18, 'bold'))
time_lbl.place(x=390, y=5)

date_lbl = Label(root, bg='white', font=('Helvetica', 18, 'bold'))
date_lbl.place(x=390, y=35)
display_time_root()

second_lbl = Label(root, textvariable=second, bg='white', fg='medium blue',
                   font=('Helvetica', 28, 'bold'))
second_lbl.place(x=430, y=430)

oxygen_data = Label(root, fg='medium blue', bg='white', font=('Helvetica', 60, 'bold'))
oxygen_data.place(x=480, y=200)

oxygen_lbl = Label(root, text="Oxygen % |", bg='white', font=('Helvetica', 28, 'bold'))
oxygen_lbl.place(x=5, y=430)

test_time_lbl = Label(root, text="Time (Sec):", bg='white', font=('Helvetica', 28, 'bold'))
test_time_lbl.place(x=220, y=430)

test_logo = Image.open("/home/pi/Documents/MAP/Buttons/test.png")
test = ImageTk.PhotoImage(test_logo)
test_btn = Button(root, text="TEST", command=lambda:(sensor_data(),thread_sec()), compound=CENTER, image=test,
                  bd=0, highlightthickness=0, bg='white', activebackground='white',
                  fg='blue', activeforeground='blue', font=('Helvetica', 16, 'bold'))
test_btn.place(x=680, y=370)

bridge_logo = Image.open("/home/pi/Documents/MAP/Buttons/Bridge.png")
bridge = ImageTk.PhotoImage(bridge_logo)
bridge_img = Label(root, image=bridge, bd=0, bg='white')
bridge_img.place(x=5, y=0)


# SETTINGS WINDOW
def open_settings():
    setting = Toplevel()
    setting.configure(background='white', cursor=NONE)
    setting.attributes('-fullscreen', True)

    def display_date_time():
        now = datetime.datetime.now()
        time_lbl['text'] = now.strftime('Time: %X')
        setting.after(1000, display_date_time)

    time_lbl = Label(setting, bg='white', font=('Helvetica', 18, 'bold'))
    time_lbl.place(x=390, y=5)
    
    date_lbl = Label(setting, text=datetime.datetime.now().strftime('Date:  %x'),
                     bg='white', font=('Helvetica', 18, 'bold'))
    date_lbl.place(x=390, y=35)
    display_date_time()

    home_logo = Image.open("/home/pi/Documents/MAP/Buttons/home1.png")
    home = ImageTk.PhotoImage(home_logo)
    home_btn = Button(setting, text="Home", compound=TOP, image=home,
                      command=setting.destroy, bd=0, highlightthickness=0, bg='white',
                      activebackground='white', font=('Helvetica', 16, 'bold'))
    home_btn.image = home
    home_btn.place(x=430, y=310)

    bridge_logo = Image.open("/home/pi/Documents/MAP/Buttons/Bridge.png")
    bridge = ImageTk.PhotoImage(bridge_logo)
    bridge_img = Label(setting, image=bridge, bd=0, bg='white')
    bridge_img.image = bridge
    bridge_img.place(x=5, y=0)
    

    # AIR CHECK WINDOW
    def air_check():
        import time
        aircheck = Toplevel()
        aircheck.configure(background='white', cursor=NONE)
        aircheck.attributes('-fullscreen', True)
        
        
        def run_test():
            checking_lbl.configure(text="Checking for ambient air", fg='black')
            time.sleep(0.5)
            

            def read_air():
                Relay_Ch1 = 26
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                GPIO.setup(Relay_Ch1, GPIO.OUT)
                
                try:
                    GPIO.output(Relay_Ch1, GPIO.LOW)
                    for i in range(20):
                        open_serl = serial.Serial("/dev/ttyS0", 9600, timeout=0.4)
                        open_serl.write(b'Z\r\n')

                        serl_read = open_serl.readall().decode().replace("Z",'')
                        flt_d = float(serl_read) / 1000
                        received_air.configure(text="{0:.2f}".format(flt_d) + '%')
                            
                        # temp
                        ser1 = serial.Serial("/dev/ttyS0", 9600, timeout=0.1)
                        ser1.write(b'T\r\n')

                        data = ser1.readall().decode().strip()
                        temp = data.replace("T",'')
                        c = (float(temp) - 1000) / 10
                        print("\nAmbient Air : ", flt_d, c)
                        
                    GPIO.output(Relay_Ch1, GPIO.HIGH)
                    GPIO.cleanup()
                except:
                    GPIO.output(Relay_Ch1, GPIO.HIGH)
                    GPIO.cleanup()

                if flt_d >= 20.2:
                    checking_lbl.configure(text="Pass", fg='green2')
                elif flt_d < 20.0:
                    checking_lbl.configure(text="Failed", fg='red')
                elif flt_d > 22.0:
                    checking_lbl.configure(text="Failed", fg='red')
            read_air()
            
            
        def start_thread():
            global t_1
            t_1 = threading.Thread(target=run_test)
            t_1.start()
            aircheck.after(1000, refresh_thread)

        def refresh_thread():
            if t_1.is_alive():
                aircheck.after(1000, refresh_thread)

        def display_time():
            now = datetime.datetime.now()
            time_lbl['text'] = now.strftime('Time: %X')
            aircheck.after(1000, display_time)
        

        time_lbl = Label(aircheck, bg='white', font=('Helvetica', 18, 'bold'))
        time_lbl.place(x=390, y=5)
        display_time()

        date_lbl = Label(aircheck, text=datetime.datetime.now().strftime('Date:  %x'),
                         bg='white', font=('Helvetica', 18, 'bold'))
        date_lbl.place(x=390, y=35)
        
        received_air = Label(aircheck, fg='medium blue', bg='white',
                             font=('Helvetica', 130, 'bold'))
        received_air.place(x=5, y=200)
        
        aircheck_lbl = Label(aircheck, text="Air Check |", bg='white',
                             font=('helvetica', 28, 'bold'))
        aircheck_lbl.place(x=5, y=430)
        
        checking_lbl = Label(aircheck, text="Click 'Test' to begin", bg='white',
                             font=('Helvetica', 24, 'bold'))
        checking_lbl.place(x=210, y=435)
        
        info_lbl = Label(aircheck, bg='white', font=('Helvetica', 24, 'bold'), fg='red2',
                         text="Have sample inlet open to air,\nremove tubing if necessary.")
        info_lbl.place(x=5, y=100)

        test_logo = Image.open("/home/pi/Documents/MAP/Buttons/test.png")
        test = ImageTk.PhotoImage(test_logo)
        test_btn = Button(aircheck, text="TEST", command=start_thread, compound=CENTER,
                          image=test, bd=0, highlightthickness=0, fg='blue', bg='white',
                          activebackground='white', activeforeground='blue',
                          font=('Helvetica', 16, 'bold'))
        test_btn.image = test
        test_btn.place(x=680, y=370)

        back_logo = Image.open("/home/pi/Documents/MAP/Buttons/back.png")
        back = ImageTk.PhotoImage(back_logo)
        back_btn = Button(aircheck, image=back, command=aircheck.destroy, bd=0,
                          highlightthickness=0, bg='white', activebackground='white',
                          font=('Helvetica', 12, 'bold'))
        back_btn.image = back
        back_btn.place(relx=1, x=-10, y=5, anchor=NE)

        home_logo = Image.open("/home/pi/Documents/MAP/Buttons/home.png")
        home = ImageTk.PhotoImage(home_logo)
        home_btn = Button(aircheck, image=home, bd=0, highlightthickness=0, bg='white',
                          command=lambda: (aircheck.destroy(), setting.destroy()),
                          activebackground='white', font=('Helvetica', 12, 'bold'))
        home_btn.image = home
        home_btn.place(relx=1, x=-110, y=0, anchor=NE)

        bridge_logo = Image.open("/home/pi/Documents/MAP/Buttons/Bridge.png")
        bridge = ImageTk.PhotoImage(bridge_logo)
        bridge_img = Label(aircheck, image=bridge, bd=0, bg='white')
        bridge_img.image = bridge
        bridge_img.place(x=5, y=0)

    air_logo = Image.open("/home/pi/Documents/MAP/Buttons/air_check.png")
    air = ImageTk.PhotoImage(air_logo)
    air_btn = Button(setting, text="Air Check", compound=TOP, image=air,
                     command=air_check, bd=0, highlightthickness=0, background='white',
                     activebackground='white', fg='black', font=('Helvetica', 16, 'bold'))
    air_btn.image = air
    air_btn.place(x=5, y=110)
    

    # TEST TIME WINDOW
    def test_time():
        testTime = Toplevel()
        testTime.configure(background='white', cursor=NONE)
        testTime.attributes('-fullscreen', True)
        
        
        def increase_sec():
            (secnd.set(secnd.get() + 1))
            second.set(secnd.get())
            error_lbl.configure(text="")
            if secnd.get() > 15:
                add_fig.set_xlim(second.get())
                canvas.draw()

        def decrease_sec():
            secnd.set(secnd.get() - 1)
            second.set(secnd.get())
            if secnd.get() == 0:
                secnd.set(0)
                second.set(0)
                error_lbl.configure(text="needs to be > 0")
            if secnd.get() < 15:
                add_fig.set_xlim(second.get())
                canvas.draw()
                

        def display_time():
            now = datetime.datetime.now()
            time_lbl['text'] = now.strftime('Time: %X')
            testTime.after(1000, display_time)

        time_lbl = Label(testTime, bg='white', font=('Helvetica', 18, 'bold'))
        time_lbl.place(x=390, y=5)
        display_time()

        date_lbl = Label(testTime, text=datetime.datetime.now().strftime('Date:  %x'),
                         bg='white', font=('Helvetica', 18, 'bold'))
        date_lbl.place(x=390, y=35)
        
        sec = IntVar()
        sec_lbl = Label(testTime, textvariable=sec, fg='medium blue', bg='white',
                        font=('Helvetica', 180, 'bold'))
        sec_lbl.place(x=5, y=140)
        
        sec_lbl.configure(textvariable=secnd)
        
        error_lbl = Label(testTime, bg='white', fg='red', font=('Helvetica', 28, 'bold'))
        error_lbl.place(x=290, y=430)
        
        testtime_lbl = Label(testTime, text="Test Time (Sec)", bg='white',
                             font=('helvetica', 28, 'bold'))
        testtime_lbl.place(x=5, y=430)

        increase_logo = Image.open("/home/pi/Documents/MAP/Buttons/increase.png")
        increase = ImageTk.PhotoImage(increase_logo)
        increase_btn = Button(testTime, command=increase_sec, compound=CENTER,
                              image=increase, bd=0, highlightthickness=0, bg='white',
                              activebackground='white', foreground='white',
                              activeforeground='white')
        increase_btn.image = increase
        increase_btn.place(x=360, y=160)

        decrease_logo = Image.open("/home/pi/Documents/MAP/Buttons/decrease.png")
        decrease = ImageTk.PhotoImage(decrease_logo)
        decrease_btn = Button(testTime, command=decrease_sec, compound=CENTER,
                              image=decrease, bd=0, highlightthickness=0, bg='white',
                              activebackground='white', foreground='white',
                              activeforeground='white')
        decrease_btn.image = decrease
        decrease_btn.place(x=360, y=310)

        back_logo = Image.open("/home/pi/Documents/MAP/Buttons/back.png")
        back = ImageTk.PhotoImage(back_logo)
        back_btn = Button(testTime, image=back, command=testTime.destroy, bd=0,
                          highlightthickness=0, bg='white', activebackground='white',
                          font=('Helvetica', 12, 'bold'))
        back_btn.image = back
        back_btn.place(relx=1, x=-10, y=5, anchor=NE)

        home_logo = Image.open("/home/pi/Documents/MAP/Buttons/home.png")
        home = ImageTk.PhotoImage(home_logo)
        home_btn = Button(testTime, image=home, highlightthickness=0, bd=0, bg='white',
                          command=lambda: (testTime.destroy(), setting.destroy()),
                          activebackground='white', font=('Helvetica', 10, 'bold'))
        home_btn.image = home
        home_btn.place(relx=1, x=-110, y=0, anchor=NE)

        bridge_logo = Image.open("/home/pi/Documents/MAP/Buttons/Bridge.png")
        bridge = ImageTk.PhotoImage(bridge_logo)
        bridge_img = Label(testTime, image=bridge, bd=0, bg='white')
        bridge_img.image = bridge
        bridge_img.place(x=5, y=0)

    timer_logo = Image.open("/home/pi/Documents/MAP/Buttons/test_time.png")
    timer = ImageTk.PhotoImage(timer_logo)
    timer_btn = Button(setting, text="Test Time", command=test_time, compound=TOP,
                       image=timer, bd=0, highlightthickness=0, bg='white',
                       activebackground='white', font=('Helvetica', 16, 'bold'))
    timer_btn.image = timer
    timer_btn.place(x=5, y=310)


    # DATE & TIME WINDOW
    def date_time():
        dateTime_ = Toplevel()
        dateTime_.configure(bg='white', cursor=NONE)
        dateTime_.attributes('-fullscreen', True)
        
        
        now = datetime.datetime.now()
        year = IntVar()
        year.set(datetime.datetime.now().year)
        month = IntVar()
        month.set(datetime.datetime.now().month)
        day = IntVar()
        day.set(datetime.datetime.now().day)
        hour = IntVar()
        hour.set(datetime.datetime.now().hour)
        mins = IntVar()
        mins.set(datetime.datetime.now().minute)
        

        month_frame = LabelFrame(dateTime_, text="Month(s)", width=240, height=110, bg='white', font=('Helvetica', 14, 'bold'))
        month_frame.place(x=370, y=130)

        day_frame = LabelFrame(dateTime_, text="Day(s)", width=240, height=110, bg='white', font=('Helvetica', 14, 'bold'))
        day_frame.place(x=370, y=240)

        hour_frame = LabelFrame(dateTime_, text="Hour(s)", width=140, height=265, bg='white', font=('Helvetica', 14, 'bold'))
        hour_frame.place(x=10, y=130)

        min_frame = LabelFrame(dateTime_, text="Minute(s)", width=140, height=265,bg='white', font=('Helvetica', 14, 'bold'))
        min_frame.place(x=200, y=130)

        month_lbl = Label(month_frame, textvariable=month, bg='white', font=('Helvetica', 48, 'bold'))
        month_lbl.place(x=5, y=5)

        day_lbl = Label(day_frame, textvariable=day, bg='white', font=('Helvetica', 48, 'bold'))
        day_lbl.place(x=5, y=5)

        hour_lbl = Label(hour_frame, textvariable=hour, bg='white', font=('Helvetica', 80, 'bold'))
        hour_lbl.place(x=5, y=5)

        mins_lbl = Label(min_frame, textvariable=mins, bg='white', font=('Helvetica', 80, 'bold'))
        mins_lbl.place(x=5, y=5)

        colon_lbl = Label(dateTime_, text=":", bg='white', font=('Helvetica', 80, 'bold'))
        colon_lbl.place(x=155, y=160)
        

        def add_month():
            month.set(month.get() + 1)
            if month.get() == 13:
                month.set(1)

        month_btn = Button(month_frame, text="  +  ", command=add_month, bd=4,
                           fg='white', activeforeground='white', bg='DodgerBlue2',
                           activebackground='DodgerBlue2', font=('Helvetica', 38, 'bold'))
        month_btn.place(x=110, y=-3)
        

        def add_day():
            day.set(day.get() + 1)
            if day.get() == 32:
                day.set(1)

        day_btn = Button(day_frame, text="  +  ", command=add_day, bd=4, fg='white',
                         activeforeground='white', bg='DodgerBlue2',
                         activebackground='DodgerBlue2', font=('Helvetica', 38, 'bold'))
        day_btn.place(x=110, y=-3)
        

        def add_hour():
            hour.set(hour.get() + 1)
            if hour.get() == 24:
                hour.set(0)

        hour_btn = Button(hour_frame, text="   +   ", command=add_hour, bd=4,
                          fg='white', activeforeground='white', bg='DodgerBlue2',
                          activebackground='DodgerBlue2', font=('Helvetica', 30, 'bold'))
        hour_btn.place(x=5, y=170)
        

        def add_min():
            mins.set(mins.get() + 1)
            if mins.get() == 60:
                mins.set(0)

        mins_btn = Button(min_frame, text="   +   ", command=add_min, bd=4, fg='white',
                          activeforeground='white', bg='DodgerBlue2',
                          activebackground='DodgerBlue2', font=('Helvetica', 30, 'bold'))
        mins_btn.place(x=5, y=170)
        

        def linux_set_time(year, month, day, hour, mins):
            
            time_string = datetime.datetime(year.get(), month.get(), day.get(),
                                            hour.get(), mins.get())

            subprocess.call(shlex.split("sudo timedatectl set-ntp false"))
            subprocess.call(shlex.split("sudo date -s '%s'" % str(time_string)))
            subprocess.call(shlex.split("sudo hwclock -w"))
            

        def set_time():
            if sys.platform == 'linux2' or sys.platform == 'linux':
                linux_set_time(year, month, day, hour, mins)
                
                current_lbl['text'] = 'Set to:'
                dateTime_.after(1000, display_time)
                root.after(1000, display_time_root)
                

        def display_time():
            now = datetime.datetime.now()
            time_lbl['text'] = now.strftime('Time: %X')
            dsply_lbl['text'] = now.strftime('%c')
            dateTime_.after(1000, display_time)
            

        time_lbl = Label(dateTime_, bg='white', font=('Helvetica', 18, 'bold'))
        time_lbl.place(x=390, y=5)
        
        date_lbl = Label(dateTime_, text=datetime.datetime.now().strftime('Date:  %x'),
                         bg='white', font=('Helvetica', 18, 'bold'))
        date_lbl.place(x=390, y=35)
        
        dsply_lbl = Label(dateTime_, bg='white', fg='medium blue', font=('Helvetica', 22, 'bold'))
        dsply_lbl.place(x=410, y=438)
        display_time()

        set_dt = Button(dateTime_, text="Set date/time", command=set_time, bd=3,
                        fg='white', activeforeground='white', bg='red2', width=16,
                        activebackground='red2', font=('Helvetica', 18, 'bold'))
        set_dt.place(x=369, y=355)

        datetime_lbl = Label(dateTime_, text="Date & Time |", bg='white',
                             font=('Helvetica', 28, 'bold'))
        datetime_lbl.place(x=5, y=430)
        
        current_lbl = Label(dateTime_, text='Current:', bg='white',
                            font=('Helvetica', 28, 'bold'))
        current_lbl.place(x=250, y=430) 

        back_logo = Image.open("/home/pi/Documents/MAP/Buttons/back.png")
        back = ImageTk.PhotoImage(back_logo)
        back_btn = Button(dateTime_, image=back, command=dateTime_.destroy, bd=0,
                          highlightthickness=0, bg='white', activebackground='white',
                          font=('Helvetica', 12, 'bold'))
        back_btn.image = back
        back_btn.place(relx=1, x=-10, y=5, anchor=NE)

        home_logo = Image.open("/home/pi/Documents/MAP/Buttons/home.png")
        home = ImageTk.PhotoImage(home_logo)
        home_btn = Button(dateTime_, image=home, bd=0, highlightthickness=0, bg='white',
                          command=lambda: (dateTime_.destroy(), setting.destroy()),
                          activebackground='white', font=('Helvetica', 12, 'bold'))
        home_btn.image = home
        home_btn.place(relx=1, x=-110, y=0, anchor=NE)

        bridge_logo = Image.open("/home/pi/Documents/MAP/Buttons/Bridge.png")
        bridge = ImageTk.PhotoImage(bridge_logo)
        bridge_img = Label(dateTime_, image=bridge, bd=0, bg='white')
        bridge_img.image = bridge
        bridge_img.place(x=5, y=0)

    clock_logo = Image.open("/home/pi/Documents/MAP/Buttons/clock.png")
    clock = ImageTk.PhotoImage(clock_logo)
    clock_btn = Button(setting, text="Date & Time", compound=TOP, image=clock,
                       command=date_time, bd=0, highlightthickness=0, bg='white',
                       activebackground='white', font=('Helvetica', 16, 'bold'))
    clock_btn.image = clock
    clock_btn.place(x=220, y=110)


    # SYSTEM CHECK WINDOW
    def systemcheck():
        import time
        system_check = Toplevel()
        system_check.configure(bg='white', cursor=NONE)
        system_check.attributes('-fullscreen', True)
        

        def run():
            checking_lbl.configure(text="Testing system")
            rs485_check.configure(selectcolor='white')
            device_lbl.configure(selectcolor='white')
            oxygen_lbl.configure(selectcolor='white')
            system_lbl.configure(selectcolor='white')
            rs485_connected.configure(text='')
            selected_device.configure(text='')
            oxygen_output.configure(text='')
            system_ready.configure(text='')
            time.sleep(0.5)
            

            def rs485_hat():
                rs485_connected.configure(text="checking connection", fg='red')
                time.sleep(1)
                rs485 = os.system("dmesg | grep -i '\(can\|spi\)'")
                
                if rs485 == '':
                    print(rs485)
                    rs485_connected.configure(text="NOT CONNECTED", fg='red')
                    rs485_check.configure(selectcolor='red')
                    
                elif rs485 == rs485:
                    print(rs485)
                    rs485_connected.configure(text="CONNECTED", fg='medium blue')
                    rs485_check.configure(selectcolor='green2')
                time.sleep(1)
            rs485_hat()
            

            def select_device():
                selected_device.configure(text="selecting device", fg='red')
                time.sleep(1)

                ser = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
                ser.write(b'! \r\n')
                time.sleep(0.1)
                ser.write(b'! 5\r\n')

                dev_data = ser.readall().decode().strip().replace('! ','')
                rmv_str = dev_data.replace("0", '')
                
                if rmv_str == '':
                    print("\n[ Device : ]")
                    selected_device.configure(text=rmv_str, fg='red')
                    device_lbl.configure(selectcolor='red')
                    
                elif rmv_str == rmv_str:
                    print("\nDevice : ", rmv_str)
                    selected_device.configure(text=rmv_str, fg='medium blue')
                    device_lbl.configure(selectcolor='green2')
                time.sleep(1)
            select_device()
            

            def sensor_data():
                Relay_Ch1 = 26
                GPIO.setwarnings(False)
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(Relay_Ch1, GPIO.OUT)
                
                try:
                    GPIO.output(Relay_Ch1, GPIO.LOW)
                    for i in range(15):
                        ser1 = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
                        ser1.write(b'Z\r\n')
                        
                        s_data = ser1.readall().decode().strip().replace("Z",'')
                        flt_data = float(s_data) / 1000
                        oxygen_output.configure(text="{0:.2f}".format(flt_data) + "%", fg='medium blue')

                    GPIO.output(Relay_Ch1, GPIO.HIGH)
                    GPIO.cleanup()
                    print("\nOXygen : ", flt_data, "%")
                    print("\nSystem : Ready")
                    
                    oxygen_lbl.configure(selectcolor='green2')
                    system_ready.configure(text="READY", fg='medium blue')
                    system_lbl.configure(selectcolor='green2')
                    checking_lbl.configure(text="Test completed")
                except:
                    GPIO.output(Relay_Ch1, GPIO.HIGH)
                    GPIO.cleanup()
                    
                    oxygen_output.configure(text="CONFG ERROR", fg='red')
                    oxygen_lbl.configure(selectcolor='red')
                    system_ready.configure(text="NOT READY", fg='red')
                    system_lbl.configure(selectcolor='red')
                    checking_lbl.configure(text="Test completed")
                    print("\nOxygen :")
                    print("\nSystem : Not ready")
            sensor_data()


        def start_thread():
            global t1
            t1 = threading.Thread(target=run, daemon=True)
            t1.start()
            system_check.after(1000, refresh_thread)

        def refresh_thread():
            if t1.is_alive():
                system_check.after(1000, refresh_thread)

        def display_time():
            now = datetime.datetime.now()
            time_lbl['text'] = now.strftime('Time: %X')
            system_check.after(1000, display_time)
            

        time_lbl = Label(system_check, bg='white', font=('Helvetica', 18, 'bold'))
        time_lbl.place(x=390, y=5)
        
        date_lbl = Label(system_check, text=datetime.datetime.now().strftime('Date:  %x'),
                         bg='white', font=('Helvetica', 18, 'bold'))
        date_lbl.place(x=390, y=35)
        display_time()

        rs485_check = Checkbutton(system_check, text='RS485     :', bg='white', font=('Helvetica', 20, 'bold'))
        rs485_check.place(x=5, y=140)
        
        rs485_connected = Label(system_check, bg='white', font=('Helvetica', 20, 'bold'))
        rs485_connected.place(x=200, y=140)
        
        device_lbl = Checkbutton(system_check, text='DEVICE   :', bg='white',font=('Helvetica', 20, 'bold'))
        device_lbl.place(x=5, y=210)
        
        selected_device = Label(system_check, bg='white', font=('Helvetica', 20, 'bold'))
        selected_device.place(x=200, y=210)

        oxygen_lbl = Checkbutton(system_check, text='OXYGEN :', bg='white', font=('Helvetica', 20, 'bold'))
        oxygen_lbl.place(x=5, y=280)
        
        system_lbl = Checkbutton(system_check, text='STATUS  :', bg='white', font=('Helvetica', 20, 'bold'))
        system_lbl.place(x=5, y=350)
        
        system_ready = Label(system_check, bg='white', font=('Helvetica', 20, 'bold'))
        system_ready.place(x=200, y=350)
        
        oxygen_output = Label(system_check, bg='white', font=('Helvetica', 20, 'bold'))
        oxygen_output.place(x=200, y=280)

        checking_lbl = Label(system_check, text="Click 'Test' to begin", bg='white', font=('Helvetica', 24, 'bold'))
        checking_lbl.place(x=290, y=435)

        system_check_lbl = Label(system_check, text="System Check |", bg='white', font=('Helvetica', 28, 'bold'))
        system_check_lbl.place(x=5, y=430)
        

        test_logo = Image.open("/home/pi/Documents/MAP/Buttons/test.png")
        test = ImageTk.PhotoImage(test_logo)
        test_btn = Button(system_check, text="TEST", command=start_thread, compound=CENTER,
                          image=test, bd=0, highlightthickness=0, fg='blue', bg='white',
                          activebackground='white', activeforeground='blue',
                          font=('Helvetica', 16, 'bold'))
        test_btn.image = test
        test_btn.place(x=680, y=370)

        back_logo = Image.open("/home/pi/Documents/MAP/Buttons/back.png")
        back = ImageTk.PhotoImage(back_logo)
        back_btn = Button(system_check, image=back, command=system_check.destroy, bd=0,
                          highlightthickness=0, bg='white', activebackground='white',
                          font=('Helvetica', 12, 'bold'))
        back_btn.image = back
        back_btn.place(relx=1, x=-10, y=5, anchor=NE)

        home_logo = Image.open("/home/pi/Documents/MAP/Buttons/home.png")
        home = ImageTk.PhotoImage(home_logo)
        home_btn = Button(system_check, image=home, bd=0, highlightthickness=0, bg='white',
                          command=lambda: (system_check.destroy(), setting.destroy()),
                          activebackground='white', font=('Helvetica', 12, 'bold'))
        home_btn.image = home
        home_btn.place(relx=1, x=-110, y=0, anchor=NE)

        bridge_logo = Image.open("/home/pi/Documents/MAP/Buttons/Bridge.png")
        bridge = ImageTk.PhotoImage(bridge_logo)
        bridge_img = Label(system_check, image=bridge, bd=0, bg='white')
        bridge_img.image = bridge
        bridge_img.place(x=5, y=0)

    system_logo = Image.open("/home/pi/Documents/MAP/Buttons/system_check.png")
    system = ImageTk.PhotoImage(system_logo)
    system_btn = Button(setting, text="System Check", compound=TOP, image=system,
                        command=systemcheck, bd=0, highlightthickness=0, bg='white',
                        activebackground='white', font=('Helvetica', 16, 'bold'))
    system_btn.image = system
    system_btn.place(x=220, y=310)
    

    # CALIBRATION WINDOW
    def calibration():
        
        # LOGIN WINDOW
        login = Toplevel()
        login.configure(bg='white', cursor=NONE)
        login.attributes('-fullscreen', True)

        keybrd_frame = Frame(login, bg='white')
        keybrd_frame.place(x=10, y=270)
        

        def select(value):
            if value == "DEL":
                txt = name_entry.get()
                val = len(txt)
                name_entry.delete(0, END)
                name_entry.insert(0, txt[:val - 1])
                txts = pass_entry.get()
                vals = len(txts)
                pass_entry.delete(0, END)
                pass_entry.insert(0, txts[:vals - 1])
            elif value == "DWN":
                pass_entry.focus_set()
                pass_entry.config(state=NORMAL)
                name_entry.config(state=DISABLED)
            elif value == "UP":
                name_entry.focus_set()
                pass_entry.config(state=DISABLED)
                name_entry.config(state=NORMAL)
            else:
                name_entry.insert(END, value)
                pass_entry.insert(END, value)
                

        buttons = ['q', 'w', 'e', 'r', 't', 'y', 'u', '7', '8', '9', 'i', 'o', 'p', 'a', 's', 'd', 'f', '4', '5', '6', 'g', 'h', 
        'j', 'k', 'l', 'z', 'UP', '1', '2', '3', 'x', 'c', 'v', 'b', 'n', 'm', 'DWN', '0', '.', 'DEL']

        varrow = 2
        varcolumn = 0
    
        for button in buttons:
            command = lambda x=button: select(x)
            if button != 'Space':
                Button(keybrd_frame, text=button, width=5, bg='Blue', fg='white', activebackground="blue", activeforeground='white',
                relief='raised', padx=7, pady=8, bd=5, font=("Helvetica", 14, 'bold'), command=command).grid(row=varrow, column=varcolumn)

            varcolumn += 1
            if varcolumn > 9 and varrow == 2:
                varcolumn = 0
                varrow += 1
            if varcolumn > 9 and varrow == 3:
                varcolumn = 0
                varrow += 1
            if varcolumn > 9 and varrow == 4:
                varcolumn = 0
                varrow += 1
            if varcolumn > 9 and varrow == 5:
                varcolumn = 0
                varrow += 1

        
        def user_login():
            if name_entry.get() == 'admin' and pass_entry.get() == '12345':
                login.destroy()

                calibration = Toplevel()
                calibration.configure(bg='white', cursor=NONE)
                calibration.attributes('-fullscreen', True)
                

                def display_time():
                    now = datetime.datetime.now()
                    time_lbl['text'] = now.strftime('Time: %X')
                    calibration.after(1000, display_time)

                time_lbl = Label(calibration, bg='white', font=('Helvetica', 18, 'bold'))
                time_lbl.place(x=390, y=5)
                
                date_lbl = Label(calibration, text=datetime.datetime.now().strftime('Date:  %x'),
                                 bg='white', font=('Helvetica', 18, 'bold'))
                date_lbl.place(x=390, y=35)
                display_time()

                cal_lbl = Label(calibration, text="Calibration", bg='white',
                                font=('Helvetica', 28, 'bold'))
                cal_lbl.place(x=5, y=430)
                
                
                start_logo = Image.open("/home/pi/Documents/MAP/Buttons/test.png")
                start = ImageTk.PhotoImage(start_logo)
                start_btn = Button(calibration, text="TEST", compound=CENTER, image=start,
                                   bd=0, highlightthickness=0, fg='blue', bg='white',
                                   activebackground='white', activeforeground='blue',
                                   font=('Helvetica', 16, 'bold'))
                start_btn.image = start
                start_btn.place(x=680, y=370)

                logout = Image.open("/home/pi/Documents/MAP/Buttons/back.png")
                log_out = ImageTk.PhotoImage(logout)
                logout_btn = Button(calibration, compound=TOP, image=log_out,
                                  command=calibration.destroy, bd=0, bg='white',
                                  highlightthickness=0, activebackground='white',
                                  font=('Helvetica', 10, 'bold'))
                logout_btn.image = log_out
                logout_btn.place(relx=1, x=-10, y=5, anchor=NE)

                bridge_logo = Image.open("/home/pi/Documents/MAP/Buttons/Bridge.png")
                bridge = ImageTk.PhotoImage(bridge_logo)
                bridge_img = Label(calibration, image=bridge, bd=0, bg='white')
                bridge_img.image = bridge
                bridge_img.place(x=5, y=0)


            elif name_entry.get() == '' and pass_entry.get() == '':
                message1['text'] = "Username cannot be empty/\nPlease enter username"
                message2['text'] = "Password cannot be empty/\nPlease enter password"
            elif name_entry.get() == 'admin' and pass_entry.get() == '':
                message1.configure(text='')
                message2['text'] = "Password cannot be empty/\nPlease enter password"
            elif name_entry.get() != 'admin' and pass_entry.get() == '':
                message1['text'] = "Incorrect username, Try again!"
                message2['text'] = "Password cannot be empty/\nPlease enter password"
            elif name_entry.get() == '' and pass_entry.get() == 'bridge1':
                message2.configure(text='')
                message1['text'] = "Username cannot be empty/\nPlease enter username"
            elif name_entry.get() == '' and pass_entry.get() != 'bridge1':
                message1['text'] = "Username cannot be empty/\nPlease enter username"
                message2['text'] = "Incorrect password, Try again!"
            elif name_entry.get() != 'admin' and pass_entry.get() != 'bridge1':
                message1['text'] = "Incorrect username, Try again!"
                message2['text'] = "Incorrect password, Try again!"
            elif name_entry.get() == 'admin' and pass_entry.get() != 'bridge1':
                message1.configure(text='')
                message2['text'] = "Incorrect password, Try again!"
            elif name_entry.get() != 'admin' and pass_entry.get() == 'bridge1':
                message2.configure(text='')
                message1['text'] = "Incorrect username, Try again!"
            elif name_entry.get() == 'admin' and pass_entry.get() == '':
                message2['text'] = "Password cannot be empty/\nPlease enter password"
            elif name_entry.get() == '' and pass_entry.get() == 'bridge1':
                message1['text'] = "Username cannot be empty/\nPlease enter username"


        # Widgets
        name_entry = Entry(login, relief=SUNKEN, bg='light grey', bd=2, width=14, font=('Helvetica', 18, 'bold'))
        name_entry.place(x=380, y=110)
        name_entry.focus_set()
        
        usr_name = Label(login, text="Username:", relief=RIDGE, bg='light grey', bd=2, width=12, font=('Helvetica', 18, 'bold'))
        usr_name.place(x=200, y=110)

        pass_entry = Entry(login, state=DISABLED, relief=SUNKEN, show='*', bg='light grey', bd=2, width=14, font=('Helvetica', 18, 'bold'))
        pass_entry.place(x=380, y=160)

        usr_pass = Label(login, text="Password:", relief=RIDGE, bg='light grey', bd=2, width=12, font=('Helvetica', 18, 'bold'))
        usr_pass.place(x=200, y=160)

        message1 = Label(login, bg='white', fg="red", font=('Helvetica', 11, 'bold'))
        message1.place(x=575, y=110)

        message2 = Label(login, bg='white', fg='red', font=('Helvetica', 11, 'bold'))
        message2.place(x=575, y=160)

        login_btn = Button(login, text="Login", command=user_login, bd=5, width=11, bg='light grey', activebackground='light grey',
                           font=('Helvetica', 16, 'bold'))
        login_btn.place(x=200, y=205)

        cancel_btn = Button(login, text="Cancel", command=login.destroy, bd=5, width=13, bg='red', activebackground='red',
                            font=('Helvetica', 16, 'bold'))
        cancel_btn.place(x=380, y=205)
        

        bridge_logo = Image.open("/home/pi/Documents/MAP/Buttons/Bridge.png")
        bridge = ImageTk.PhotoImage(bridge_logo)
        bridge_img = Label(login, image=bridge, bd=0, bg='white')
        bridge_img.image = bridge
        bridge_img.place(x=200, y=0)

    cal_logo = Image.open("/home/pi/Documents/MAP/Buttons/calibration.png")
    cal = ImageTk.PhotoImage(cal_logo)
    cal_btn = Button(setting, text="Calibration", compound=TOP, image=cal,
                     command=calibration, bd=0, highlightthickness=0, bg='white',
                     activebackground='white', font=('Helvetica', 16, 'bold'))
    cal_btn.image = cal
    cal_btn.place(x=431, y=110)
    

# settings button
settings_logo = Image.open("/home/pi/Documents/MAP/Buttons/settings.png")
settings = ImageTk.PhotoImage(settings_logo)
settings_btn = Button(root, image=settings, command=open_settings, bd=0,
                      highlightthickness=0, bg='white', activebackground='white')
settings_btn.image = settings
settings_btn.place(x=710, y=10)


def exit_sys(event):
    root.destroy()
    return event

root.bind('<Escape>', exit_sys)

root.mainloop()
sys.exit()    