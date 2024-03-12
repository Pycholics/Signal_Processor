###SignalProcessor###
##Created by Pycholics##

#Tkinter packages
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog as fd
#Wave code
from tools import *
#Export packages
import wave
import struct
#Matplotlib plot waves
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.axis import Axis
import numpy as np

#Variables
grid_lines = {}
selected_wave = None
use_waves = {}
waves = {}
line_no = 2
view_graph = None

#Superclass of lines of waves
class GridLine:
    c = {}
    selected_line = None
    def __init__(self,grid,no):  
        GridLine.c[no] = IntVar()
        self.grid = grid
        self.no = no
        
        self.line = LabelFrame(grid, bg = 'blue', bd = 2)
        data = lambda: Buttons.use_wave(self.no,GridLine.c[self.no].get())   

        self.used = Checkbutton(self.line, font = 'Arial 9',text='Use',variable=GridLine.c[self.no], onvalue=1, offvalue=0, command=data)
   
    def checkbtn_state(self):
        GridLine.c[self.no].set(0)
        self.used.deselect()
    #Method that changes selected line(blue line)
    def selected(self,event):
        global selected_wave
        global view_graph
        if self != GridLine.selected_line:
            if GridLine.selected_line == None:
                GridLine.selected_line = self
                self.line.configure(bg = "blue")
            else:
                self.line.configure(bg = "blue")
                if type(GridLine.selected_line) is BasicGridLine:
                    descolor = '#07EFF7'
                else:
                    descolor = '#FF0096'
                GridLine.selected_line.line.configure(bg = descolor)
                GridLine.selected_line = self
                
            if (GridLine.selected_line.no in waves.keys()) or (type(GridLine.selected_line) is ComposedGridLine):
                selected_wave  = waves[GridLine.selected_line.no]
                print(selected_wave)
                view_graph.preview()
            else:
                messagebox.showerror(title='Exist Error', message='This is not a configured signal!') 
    #Delete line of wave               
    def del_line(self):
        self.line.destroy()
        
#The class of the lines of sine, square and triangular waves        
class BasicGridLine(GridLine):
    def __init__(self,grid,no):
        super().__init__(grid,no)
        if GridLine.selected_line != None:
            if type(GridLine.selected_line) is ComposedGridLine:  
                GridLine.selected_line.line.configure(bg = '#FF0096')
            else:
                GridLine.selected_line.line.configure(bg = '#07EFF7')
        GridLine.selected_line = self
        self.line.grid_columnconfigure(7, weight=1)
        self.line.grid_rowconfigure(0, weight=1)
        self.line.grid(row = no,column=0,sticky=N)
               
        self.noL = Label(self.line, text = no, font = 'Arial 9')
        self.noL.grid(row = 0,column=0, padx=10)
        

        self.type = StringVar(value=None)
        self.freq = StringVar(value=None)
        self.ampl = StringVar(value=None)
        self.phase = StringVar(value=None)
        self.dur = StringVar(value=None)
        
        self.combitems = ['Sine','Square','Triangular']
        self.typeC = ttk.Combobox(self.line, values=self.combitems,state="readonly",textvariable=self.type,width=8)
        self.typeC.set("Choose")
        self.typeC.grid(row = 0,column=1, padx=10)
        
        self.freqE = Entry(self.line, font = 'Arial 9',width=8,textvariable = self.freq)
        self.freqE.grid(row = 0,column=2, padx=10)
        
        self.amplE = Entry(self.line, font = 'Arial 9',width=8,textvariable = self.ampl)
        self.amplE.grid(row = 0,column=3, padx=10)

        self.phaseE = Entry(self.line, font = 'Arial 9',width=8,textvariable = self.phase)
        self.phaseE.grid(row = 0,column=4, padx=10)

        self.durE = Entry(self.line, font = 'Arial 9',width=8,textvariable = self.dur)
        self.durE.grid(row = 0,column=5, padx=10)

        self.used.grid(row = 0,column=6, padx=10)

        self.save = Button(self.line, text="Save",font='Arial 7',width = 6,bg='#66FF00',command=lambda: self.saveline())
        self.save.grid(row=0,column=7,padx = 10)

        self.line.bind('<Button-1>', self.selected)
    #Get data from the lines
    def get_data(self):
        data = []

        data.append(self.type.get())
        data.append(self.freq.get()) 
        
        if self.ampl.get() == '':
            data.append(32000)
            self.ampl.set(data[2])
        else:
            data.append(self.ampl.get())
            
        if self.phase.get() == '':
            data.append(0)
            self.phase.set(data[3])
        else:
            data.append(self.phase.get())
            
        data.append(self.dur.get())  
             
        return data 
                    
    #Save line as wave
    def saveline(self):
        global line_no
        global waves
        global selected_wave
        global grid_lines
        wave = self.get_data()
        dur_analogy = 5
        try:
            float(wave[1])
            float(wave[2])
            float(wave[3])
            #Duration of the wave for best plot quality
            if wave[4] == '':
                wave[4] = dur_analogy/float(wave[1])
                self.dur.set(wave[4])
            float(wave[4])
            if wave[0] =='Choose':
                grid_lines[self.no].checkbtn_state()
                messagebox.showerror(title='Parameters Error', message='Select a type of signal!')
                check = False
            else:
                check = True
        except ValueError:
            check = False
            grid_lines[self.no].checkbtn_state()
            messagebox.showerror(title='Parameters Error', message='Type valid values in the entries!')
            return False
            
        if check:              
            if wave[0] =='Sine':
                waves[self.no] = Sinewave(float(wave[1]),float(wave[2]),float(wave[3]),float(wave[4]))
            elif wave[0] =='Square':
                waves[self.no] = Square_wave(float(wave[1]),float(wave[2]),float(wave[3]),float(wave[4]))
            elif wave[0] =='Triangular':
                 waves[self.no] = Trianglewave(float(wave[1]),float(wave[2]),float(wave[3]),float(wave[4]))

            try:
                if GridLine.selected_line.no == self.no:     
                    selected_wave  = waves[GridLine.selected_line.no]
                    view_graph.preview()
            except:
                pass

            self.typeC.config(state='disabled')
            self.freqE.config(state='disabled')
            self.amplE.config(state='disabled')
            self.phaseE.config(state='disabled')
            self.durE.config(state='disabled')
            self.save.destroy()
            export = lambda: export_wave(waves[self.no])
            self.export = Button(self.line, text="Export",font='Arial 7',width = 7,bg='#fdbf00',command=export)
            self.export.grid(row=0,column=7,padx = 3)
            
            return True
        
#The class of the lines of composed waves by superposition or convolution
class ComposedGridLine(GridLine):
    def __init__(self,grid,identity,calc,wave,no):
        global waves
        global selected_wave
        super().__init__(grid,no)
        if GridLine.selected_line != None:
            if type(GridLine.selected_line) is ComposedGridLine:  
                GridLine.selected_line.line.configure(bg = '#FF0096')
            else:
                GridLine.selected_line.line.configure(bg = '#07EFF7')
        GridLine.selected_line = self
        self.line.grid_columnconfigure(4, weight=1)
        self.line.grid_rowconfigure(0, weight=1)
        self.line.grid(row = no,column=0,sticky=N)
               
        self.noL = Label(self.line, text = no, font = 'Arial 9')
        self.noL.grid(row = 0,column=0, padx=10)

        self.calc = Label(self.line, text = calc, font = 'Arial 9')
        self.calc.grid(row = 0,column=1, padx=10)
        
        idTxt = "Made by: "
        for i in identity:
            idTxt += f"{i},"
        idTxt = idTxt[:-1]         
        self.id = Label(self.line, text = idTxt, font = 'Arial 7')
        self.id.grid(row = 0,column=2, padx=10)
        
        self.used.grid(row = 0,column=3, padx=110-len(identity)*4)
        export = lambda: export_wave(waves[self.no])
        self.export = Button(self.line, text="Export",font='Arial 7',width = 7,bg='#fdbf00',command=export)
        self.export.grid(row=0,column=4,padx = 3)

        self.line.bind('<Button-1>', self.selected)

        waves[self.no] = wave   
        selected_wave  = waves[GridLine.selected_line.no]
        view_graph.preview()
    
#Controller of the buttons of ControlPanel
class Buttons:
    #Add wave line  
    def addline(root):
        global grid_lines
        global line_no
        grid_lines[line_no] = BasicGridLine(root,line_no)
        line_no += 1
    #Use wave line on calculations
    def use_wave(no,state):
        global selected_wave
        if state:
            global grid_lines
            check = False
            if type(grid_lines[no]) is BasicGridLine:
                ok = grid_lines[no].saveline()
                if ok:
                    use_waves[no] = waves[no]
            else:
                use_waves[no] = waves[no]
        else:
            print("deleted")
            use_waves.pop(no)
    #Delete Line Method       
    def delline(root):
        global line_no
        global selected_wave
        global grid_lines
        global waves
        if len(grid_lines) > 0 and GridLine.selected_line != None:
             
            try:
                waves.pop(GridLine.selected_line.no)
                use_waves.pop(GridLine.selected_line.no)
            except:
                pass
            grid_lines.pop(GridLine.selected_line.no)
            GridLine.selected_line.del_line()
            GridLine.selected_line = None
            selected_wave = None
        
        
        
#Function that draws the basic start-up graphics
def drawGraphics():
    global view_graph
    m_form = Tk()
    m_form.grid_rowconfigure(1, weight=1)
    m_form.grid_columnconfigure(1, weight=1)
    m_form.title("Signal Processor------- © 2023 Featured by Pycholics")
    m_form.geometry('1500x700+0+0')
    
    tabControl = ttk.Notebook(m_form)
    view_tab = Frame(tabControl)
    fft_tab = Frame(tabControl)
    tabControl.add(view_tab, text ='View Signal')
    tabControl.add(fft_tab, text ='Fourier Transform')
    tabControl.grid(row=0,column=0,sticky=NW)

    fft_graph = Plotter(fft_tab)
    view_graph = Plotter(view_tab)
    
    controlPanel = LabelFrame(m_form,bg = '#6C2DC7',bd = 3,text="Control Panel",font='Arial 12')
    controlPanel.grid_rowconfigure(1, weight=1)
    controlPanel.grid_columnconfigure(2, weight=1)
    controlPanel.grid(row=1,column=0,sticky=(E,W,S))

    wave_list = LabelFrame(m_form, bg = '#C2BEBC', bd = 3,width= 700,height = 1000,text="Signals", font = 'Arial 14')
    wave_list.grid_rowconfigure(1, weight=1)
    wave_list.grid_columnconfigure(0, weight=1)
    wave_list.grid(row=0,column=1,rowspan=2,sticky=NE)
 
    wave_s_grid = LabelFrame(wave_list, bg = '#C2BEBC', bd = 3,width= 700,height = 1000,text="Basic", font = 'Arial 12')
    wave_s_grid.grid_rowconfigure(0, weight=1)
    wave_s_grid.grid_columnconfigure(1, weight=1)
    wave_s_grid.grid(row=0,column=0,sticky=NE)

    wave_c_grid = LabelFrame(wave_list, bg = '#C2BEBC', bd = 3,width= 700,height = 1000,text="Composed", font = 'Arial 12')
    wave_c_grid.grid_rowconfigure(0, weight=1)
    wave_c_grid.grid_columnconfigure(1, weight=1)
    wave_c_grid.grid(row=1,column=0,sticky=NE)

    del_btn = Button(controlPanel, text="Delete Wave",font=40,width = 10,bg='red',command=lambda: Buttons.delline(wave_s_grid))
    del_btn.grid(row=1,column=2,sticky=SE,padx = 10,pady = 20)
    
    add_btn = Button(controlPanel, text="Add Wave",font=40,width = 10,bg='#66FF00',command=lambda: Buttons.addline(wave_s_grid))
    add_btn.grid(row=0,column=2,sticky=SE,padx = 10,pady = 10)

    spos_btn = Button(controlPanel, text="SuperPosition",font=('Roman', 17, 'bold'),width = 14,bg='#4CC417',command=lambda: view_graph.spos(use_waves,wave_c_grid))
    spos_btn.grid(row=0,column=0,sticky=SE,padx = 10,pady = 10)
    
    conv_btn = Button(controlPanel, text="Convolution",font=('Roman', 17, 'bold'),width = 14,bg='#307D7E',command=lambda: view_graph.conv(use_waves,wave_c_grid))
    conv_btn.grid(row=1,column=0,sticky=SE,padx = 10,pady = 10)

    fft_btn = Button(controlPanel, text="Fourier Transform",font=('Roman', 17, 'bold'),width = 17,bg='#307D7E',command=lambda: fft_graph.fft(selected_wave))
    fft_btn.grid(row=1,column=1,sticky=SE,padx = 10,pady = 10)

    
    

    t_line = Frame(wave_s_grid, bg = '#C2BEBC')
    t_line.grid_columnconfigure(6, weight=1)
    t_line.grid_rowconfigure(0, weight=1)
    t_line.grid(row = 0,column=0,sticky=NW)

    l_0 = Label(t_line, text="No",font="Arial 9")
    l_0.grid(row=0,column=0,padx = 7,sticky=W)

    l_1 = Label(t_line, text="Type of Wave",font="Arial 9")
    l_1.grid(row=0,column=1,padx = 5,sticky=W)

    l_2 = Label(t_line, text="Frequency",font="Arial 9")
    l_2.grid(row=0,column=2,padx = 9,sticky=W)

    l_3 = Label(t_line, text="Amplitude",font="Arial 9")
    l_3.grid(row=0,column=3,padx = 10,sticky=W)
    
    l_4 = Label(t_line, text="Phase",font="Arial 9")
    l_4.grid(row=0,column=4,padx = 18,sticky=W)

    l_5 = Label(t_line, text="Duration",font="Arial 9")
    l_5.grid(row=0,column=5,padx = 14,sticky=W)

    grid_lines[1] = BasicGridLine(wave_s_grid,1)
    
    m_form.mainloop()

 
#Plotter controller and calculations of waves
class Plotter:
    def __init__(self,root):
        self.root = root
        self.fig = Figure(figsize=(7.8, 4.6), dpi=100)

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, root)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    #View Plot
    def preview(self):
        global selected_wave
        self.fig.clear()
        plot = self.fig.add_subplot(111)
        plot.title.set_text(f"Viewing signal no{GridLine.selected_line.no}")
        plot.set_xlabel('Time (sec)')
        plot.set_ylabel('Amplitude')
        plot.plot(selected_wave.t,selected_wave.y)
        self.canvas.draw_idle()
    #SuperPositions
    def spos(self,w,grid):
        waves = []
        keys = []
        global grid_lines
        global line_no
        for key,item in w.items(): 
            waves.append(item)
            keys.append(key)
        
        if len(waves) > 1:
            wave = waves[0].superposition(waves[1:])

            grid_lines[line_no] = ComposedGridLine(grid,keys,"SuperPositioned",wave,line_no)
            line_no += 1
            
    #Convolution    
    def conv(self,w,grid):
        waves = []
        keys = []
        global grid_lines
        global line_no
        for key,item in w.items(): 
            waves.append(item)
            keys.append(key)
            
        if len(waves) > 1:
            wave = waves[0].convolve(waves[1:])

            grid_lines[line_no] = ComposedGridLine(grid,keys,"Convolved",wave,line_no)
            line_no += 1  

    #Fourier Transform        
    def fft(self,wave):
        if wave != None:
            t = wave.fft()
            self.fig.clear()
            plot = self.fig.add_subplot(111)
            plot.title.set_text(f"Fourier transform of signal no{GridLine.selected_line.no}")
            plot.set_xlabel('Frequency (Hz)')
            plot.set_ylabel('Amplitude')
            plot.plot(t[0],t[1])
            self.canvas.draw_idle()

#Export WAV file functions           
def export_wave(w):
    # The sampling rate of the analog to digital convert
    sampling_rate = 100_000
    try:
        file = fd.asksaveasfilename(initialdir="/", title="Save as",
            filetypes=(("audio file", "*.wav"), ("all files", "*.*")),
            defaultextension=".wav")
        if file is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        
        # Wave file parameters
        nframes = sampling_rate * int(w.d)
        comptype="NONE" #compress type
        compname="not compressed"
        nchannels=2
        sampwidth=2 #sample in bytes

        wav_file = wave.open(file, 'w')
        wav_file.setparams((nchannels, sampwidth, int(sampling_rate), nframes, comptype, compname))
        #Create file
        wave_array = []
        for o in w.y:
           wave_array.append(int(o.item()))
        values = []
        maxamp = max(wave_array)
        for i in wave_array:
            packed_value = struct.pack('h', int(i / (maxamp / 32000)))
            values.append(packed_value)
            values.append(packed_value)
        value_str = b''.join(values)
        wav_file.writeframes(value_str)

        wav_file.close()
    except ValueError:
        print(ValueError)
        messagebox.showerror(title='Export Error', message='Failed... Try again!')

#Main       
def main_Program():
    drawGraphics()            

main_Program()

