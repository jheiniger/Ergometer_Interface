from tkinter import *
import serial.tools.list_ports
import threading
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.figure import Figure
from datetime import datetime
import pandas as pd
import time
import numpy as np


class Interface():

    def __init__(self):
        self.root = Tk()
        self.baud = 9600
        self.port = "COM"
        self.ser = None
        self.serialData = False
        self.force = 0
        self.data_str = "empty"
        self.log = False
        self.filename = ""
        self.datalist = []
        self.timelist = []
        self.timeZero = 0.0
        self.port_lable = Label(self.root, text = "Available Port(s): ", bg = "white")
        self.exit_btn = Button(self.root, text = "Exit", height = 2, width = 15, command = self.exit)
        self.refresh_btn = Button(self.root, text = "Refresh", height = 2, width = 15, command = self.update_COMS)
        self.connect_btn = Button(self.root, text = "Connect", height = 2, width = 15, state = "disabled", command=self.connexion)
        self.start_btn = Button(self.root, text = "Start", height = 2, width = 15, fg = "white", bg = "green", state = "disabled", command=self.start_logging)
        self.stop_btn = Button(self.root, text = "Stop", height = 2, width = 15, fg = "white", bg = "red", state = "disabled", command= self.stop_logging)
        self.reset_btn = Button(self.root, text = "Reset", height = 2, width = 15, state = "disabled", command= self.reset)
        self.clicked_com = StringVar()
        self.drop_COM = OptionMenu(self.root, self.clicked_com, ["-"])
        self.graph = Graphics()
        self.graph.canvas = Canvas(self.root, width = 400, height = 100, bg = "white")
        self.t1 = threading.Thread(target = self.readSerial)

       
        
        

    def connect_menu_init(self):
        self.root.title("Force Sensor Gui")
        self.root.geometry("700x500")
        self.root.config(bg = "white")

        self.port_lable.grid(column = 1, row = 2, pady = 20)
        self.refresh_btn.grid(column = 4, row = 2)
        self.connect_btn.grid(column = 4, row = 3)
        self.exit_btn.grid(column=4,row = 8, pady = 20)

        self.update_COMS()

        self.start_btn.grid(column = 2, row = 4, pady = 20)
        self.stop_btn.grid(column = 3, row = 4, pady = 20)
        self.reset_btn.grid(column= 4, row = 7, pady = 20)
        
        self.graph.canvas.grid(row = 6, columnspan = 5)
        self.graph.text = self.graph.canvas.create_text(200, 50, font=("Helvetica", "10"), text="HELLO", fill = "black")
        
        

    def run(self):
        self.root.mainloop()

    def update_COMS(self):
        
        ports = serial.tools.list_ports.comports()
        coms = [com[0] for com in ports]
        coms.insert(0, "-")
        try:
            self.drop_COM.destroy()
        except:
            pass

        self.drop_COM = OptionMenu(self.root, self.clicked_com, *coms, command=self.connect_check)
        self.clicked_com.set(coms[0])
        self.drop_COM.config(width = 20)
        self.drop_COM.grid(column=3,row=2, padx = 50)

        self.connect_check(0)
     
    def connect_check(self, args):
        if "-" in self.clicked_com.get():
            self.connect_btn["state"] = "disable"
        else:
            self.connect_btn["state"] = "active"

    def connexion(self):
        if self.connect_btn["text"] in "Disconnect":
            self.serialData = False
            self.connect_btn["text"] = "Connect"
            self.refresh_btn["state"] = "active"
            self.drop_COM["state"] = "active"
            self.reset_btn["state"] = "disable"
        else:
            self.serialData = True
            self.connect_btn["text"] = "Disconnect"
            self.refresh_btn["state"] = "disable"
            self.start_btn["state"] = "active"
            self.drop_COM["state"] = "disable"
            self.reset_btn["state"] = "active"
            self.port = self.clicked_com.get()
            try:
                self.ser = serial.Serial(self.port, self.baud)
            except:
                pass
            
            self.t1.start()
            

    def readSerial(self):
        while(self.serialData):
            data = self.ser.readline()
            if len(data) > 0:
                self.data_str = data.decode('utf8')
                self.graph_update()
                if self.log:
                    if "Force: " in self.data_str:
                        val = self.data_str.replace("Force: ","")
                        self.datalist.append(float(val))
                        self.timelist.append(time.time_ns()*10**-9 - self.timeZero)
                        print(val)
                else:
                    print(self.data_str)
                    
               


    def graph_update(self):
        self.graph.canvas.itemconfig(self.graph.text, text=self.data_str)

    def start_logging(self):
        self.log = True
        self.stop_btn["state"] = "active"
        self.start_btn["state"] = "disable"
        name = datetime.now()
        self.timeZero = time.time_ns()*10**-9
        self.filename = name.strftime("%Y%m%d_%H%M")
        

    def stop_logging(self):
        self.log = False
        self.start_btn["state"] = "active"
        self.stop_btn["state"] = "disable"
        #df = pd.DataFrame(self.datalist)
        df = pd.DataFrame(list(zip(self.timelist, self.datalist)), columns = ["Time [s]", "Force"])
        df.to_csv("logging/"+ self.filename + ".csv", sep=',',index=False)
        print_plot("logging/" + self.filename + ".csv")
        self.datalist = []
        self.timelist = []

    def reset(self):
        self.ser.write(b'RESET')

    def exit(self):
        serialData = False
        self.root.destroy()


class Graphics():
    pass


def print_plot(filename):
    df = pd.read_csv (filename)
    df.plot(x = "Time [s]", y = "Force")
    plt.show()



def main():
    """Main"""

    gui = Interface()
    gui.connect_menu_init()
    gui.run()


if __name__ == '__main__':
    main()