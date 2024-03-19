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
import matplotlib.pyplot as plt
import numpy as np

#Variables
grid_lines = {}
selected_wave = None
use_waves = {}
waves = {}
line_no = 2
view_graph = None
fft_graph  = None
fft_x = None

#Superclass of the signal lines
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
        global fft_graph
        if self != GridLine.selected_line:
            if GridLine.selected_line == None:
                GridLine.selected_line = self
                self.line.configure(bg = "blue")
            else: #Deselect Re-color
                self.line.configure(bg = "blue")
                if (type(GridLine.selected_line) is Periodic_GridLine) or (type(GridLine.selected_line) is NonPeriodic_GridLine) :
                    descolor = '#07EFF7' ##Light-Blue
                else:
                    descolor = '#FF0096' ##Light-Purple
                GridLine.selected_line.line.configure(bg = descolor)
                GridLine.selected_line = self
                
            if (GridLine.selected_line.no in waves.keys()) or (type(GridLine.selected_line) is ComposedGridLine): #See
                selected_wave  = waves[GridLine.selected_line.no]
                print(selected_wave)
                view_graph.preview()
                fft_graph.fft(selected_wave)
            else:
                messagebox.showerror(title='Exist Error', message='This is not a configured signal!') 
    #Delete line of wave               
    def del_line(self):
        self.line.destroy()
        
#The class of the periodic signals lines      
class Periodic_GridLine(GridLine):
    def __init__(self,grid,no):
        super().__init__(grid,no)
        if GridLine.selected_line != None:
            if type(GridLine.selected_line) is ComposedGridLine:  
                GridLine.selected_line.line.configure(bg = '#FF0096')
            else:
                GridLine.selected_line.line.configure(bg = '#07EFF7')
        GridLine.selected_line = self
        self.line.grid_columnconfigure(9, weight=1)
        self.line.grid_rowconfigure(0, weight=1)
        self.line.grid(row = no,column=0,sticky=N)
               
        self.noL = Label(self.line, text = no, font = 'Arial 9')
        self.noL.grid(row = 0,column=0, padx=7)
        

        self.type = StringVar(value=None)
        self.freq = StringVar(value=None)
        self.ampl = StringVar(value=None)
        self.phase = StringVar(value=None)
        self.spanB = StringVar(value=None)  #Span Begining
        self.spanE = StringVar(value=None)  #Span End
        
        self.combitems = ['Cosine','Square','Triangular']
        self.typeC = ttk.Combobox(self.line, values=self.combitems,state="readonly",textvariable=self.type,width=7)
        self.typeC.set("Choose")
        self.typeC.grid(row = 0,column=1, padx=7)
        
        self.freqE = Entry(self.line, font = 'Arial 9',width=8,textvariable = self.freq)
        self.freqE.grid(row = 0,column=2, padx=7)
        
        self.amplE = Entry(self.line, font = 'Arial 9',width=8,textvariable = self.ampl)
        self.amplE.grid(row = 0,column=3, padx=7)

        self.phaseE = Entry(self.line, font = 'Arial 9',width=8,textvariable = self.phase)
        self.phaseE.grid(row = 0,column=4, padx=7)

        self.spanEB = Entry(self.line, font = 'Arial 9',width=6,textvariable = self.spanB)
        self.spanEB.grid(row = 0,column=5, padx=7)

        self.l = Label(self.line, text="-",font="Arial 16")
        self.l.grid(row=0,column=6)

        self.spanEE = Entry(self.line, font = 'Arial 9',width=6,textvariable = self.spanE)
        self.spanEE.grid(row = 0,column=7, padx=5)

        self.used.grid(row = 0,column=8, padx=7)

        self.save = Button(self.line, text="Save",font='Arial 7',width = 6,bg='#66FF00',command=lambda: self.saveline())
        self.save.grid(row=0,column=9,padx = 1)

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
            
        data.append(self.spanB.get())  
        data.append(self.spanE.get())  
             
        return data 
                    
    #Save line as wave
    def saveline(self):
        global line_no
        global waves
        global selected_wave
        global grid_lines
        wave = self.get_data()
        dur_analogy = 5  #For focus on wave correction
        try:
            float(wave[1])
            float(wave[2])
            float(wave[3])
            #Duration of the wave for best plot quality
            if wave[4] == '':
                wave[4] = 0
                self.spanB.set(wave[4])
            float(wave[4])
            if wave[5] == '':
                wave[5] = dur_analogy/float(wave[1])
                self.spanE.set(wave[5])
            float(wave[5])
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
            
        if check:              ##The signals creator tools.py connection
                                ##Type|Frequency|Amplitude|Phase|SpanBegin|SpanEnd
            if wave[0] =='Cosine':
                waves[self.no] = Cosinewave(float(wave[1]),float(wave[2]),float(wave[3]),float(wave[4]),float(wave[5]))
            elif wave[0] =='Square':
                waves[self.no] = Square_wave(float(wave[1]),float(wave[2]),float(wave[3]),float(wave[4]),float(wave[5]))
            elif wave[0] =='Triangular':
                 waves[self.no] = Trianglewave(float(wave[1]),float(wave[2]),float(wave[3]),float(wave[4]),float(wave[5]))

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
            self.spanEB.config(state='disabled')
            self.spanEE.config(state='disabled')
            self.save.destroy()
            export = lambda: export_wave(waves[self.no])
            self.export = Button(self.line, text="Export",font='Arial 7',width = 7,bg='#fdbf00',command=export)
            self.export.grid(row=0,column=9,padx = 3)
            
            return True

#The class of the non-periodic signals lines    
class NonPeriodic_GridLine(GridLine):
    def __init__(self,grid,no):
        super().__init__(grid,no)
        if GridLine.selected_line != None:
            if type(GridLine.selected_line) is ComposedGridLine:  
                GridLine.selected_line.line.configure(bg = '#FF0096')
            else:
                GridLine.selected_line.line.configure(bg = '#07EFF7')
        GridLine.selected_line = self
        self.line.grid_columnconfigure(9, weight=1)
        self.line.grid_rowconfigure(0, weight=1)
        self.line.grid(row = no,column=0,sticky=N)
               
        self.noL = Label(self.line, text = no, font = 'Arial 9')
        self.noL.grid(row = 0,column=0, padx=7)
        

        self.type = StringVar(value=None)
        self.freq = StringVar(value=None)
        self.ampl = StringVar(value=None)
        self.phase = StringVar(value=None)
        self.spanB = StringVar(value=None)  #Span Begining
        self.spanE = StringVar(value=None)  #Span End
        
        self.combitems = ['Delta','Square_Pulse','Sinc']
        self.typeC = ttk.Combobox(self.line, values=self.combitems,state="readonly",textvariable=self.type,width=7)
        self.typeC.set("Choose")
        self.typeC.grid(row = 0,column=1, padx=7)
        
        self.freqE = Entry(self.line, font = 'Arial 9',width=8,textvariable = self.freq)
        self.freqE.grid(row = 0,column=2, padx=7)
        
        self.amplE = Entry(self.line, font = 'Arial 9',width=8,textvariable = self.ampl)
        self.amplE.grid(row = 0,column=3, padx=7)

        self.phaseE = Entry(self.line, font = 'Arial 9',width=8,textvariable = self.phase)
        self.phaseE.grid(row = 0,column=4, padx=7)

        self.spanEB = Entry(self.line, font = 'Arial 9',width=6,textvariable = self.spanB)
        self.spanEB.grid(row = 0,column=5, padx=7)

        self.l = Label(self.line, text="-",font="Arial 16")
        self.l.grid(row=0,column=6)

        self.spanEE = Entry(self.line, font = 'Arial 9',width=6,textvariable = self.spanE)
        self.spanEE.grid(row = 0,column=7, padx=5)

        self.used.grid(row = 0,column=8, padx=7)

        self.save = Button(self.line, text="Save",font='Arial 7',width = 6,bg='#66FF00',command=lambda: self.saveline())
        self.save.grid(row=0,column=9,padx = 1)

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
            
        data.append(self.spanB.get())  
        data.append(self.spanE.get())  
             
        return data 
                    
    #Save line as wave
    def saveline(self):
        global line_no
        global waves
        global selected_wave
        global grid_lines
        wave = self.get_data()
        dur_analogy = 5  #For focus on wave correction
        try:
            float(wave[1])
            float(wave[2])
            float(wave[3])
            #Duration of the wave for best plot quality
            if wave[4] == '':
                wave[4] = 0
                self.spanB.set(wave[4])
            float(wave[4])
            if wave[5] == '':
                wave[5] = dur_analogy/float(wave[1])
                self.spanE.set(wave[5])
            float(wave[5])
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
            
        if check:         ##The signals creator tools.py connection
                                ##Type|Frequency|Amplitude|Phase|SpanBegin|SpanEnd     
            if wave[0] =='Delta':
                waves[self.no] = Delta(float(wave[2]),float(wave[4]),float(wave[5]))
            elif wave[0] =='Square_Pulse':
                waves[self.no] = Square_Pulse(float(wave[2]),float(wave[4]),float(wave[5]))
            elif wave[0] =='Sinc':
                 waves[self.no] = Sinc(float(wave[1]),float(wave[2]),float(wave[3]),float(wave[4]),float(wave[5]))

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
            self.spanEB.config(state='disabled')
            self.spanEE.config(state='disabled')
            self.save.destroy()
            export = lambda: export_wave(waves[self.no])
            self.export = Button(self.line, text="Export",font='Arial 7',width = 7,bg='#fdbf00',command=export)
            self.export.grid(row=0,column=9,padx = 3)
            
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
    global selected_wave
    #Add wave line  
    def addline(root):
        global grid_lines
        global line_no
        if type(GridLine.selected_line) is (Periodic_GridLine):   #Choose which line to add by checking what type is now selected
            grid_lines[line_no] = Periodic_GridLine(root[0],line_no)
            line_no += 1
        elif type(GridLine.selected_line) is (NonPeriodic_GridLine): 
            grid_lines[line_no] = NonPeriodic_GridLine(root[1],line_no)
            line_no += 1
    #Use wave line on calculations
    def use_wave(no,state): 
        if state:
            global grid_lines
            check = False
            if type(grid_lines[no]) is Periodic_GridLine:
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
    global fft_graph
    m_form = Tk()
    m_form.grid_rowconfigure(1, weight=2)
    m_form.grid_columnconfigure(1, weight=1)
    m_form.title("Signal Processor------- © 2024 Developed by Pycholics")
    m_form.geometry('1500x700+0+0')
    
    tabControl = ttk.Notebook(m_form)
    view_tab = Frame(tabControl)
    fft_tab = Frame(tabControl)
    tabControl.add(view_tab, text='View Signal')
    tabControl.add(fft_tab, text='Fourier Transform')
    tabControl.grid(row=0, column=0, sticky="nw")

    fft_graph = Plotter(fft_tab)
    view_graph = Plotter(view_tab)

    # Buttons
    controlPanel = LabelFrame(m_form, bg='#6C2DC7', bd=3, text="Control Panel", font='Arial 12')
    controlPanel.grid_rowconfigure(1, weight=2)
    controlPanel.grid_columnconfigure(2, weight=1)
    controlPanel.grid(row=1, column=0, sticky=(E,W,S))

    # Signals SuperFrame
    wave_list = LabelFrame(m_form, bg='#C2BEBC', bd=3, text="Signals", font='Arial 14')
    wave_list.grid(row=0, column=1, rowspan=2, sticky="ne")

    # Periodic Grid
    wave_p_grid = LabelFrame(wave_list, bg='#C2BEBC', bd=3, text="Periodic", font='Arial 12')
    wave_p_grid.grid_rowconfigure(0, weight=1)
    wave_p_grid.grid_columnconfigure(0, weight=1)
    wave_p_grid.grid(row=0, column=0, sticky="nw")

    tp_line = Frame(wave_p_grid, bg='#C2BEBC')
    tp_line.grid_rowconfigure(0, weight=1)
    tp_line.grid_columnconfigure(6, weight=1)
    tp_line.grid(row=0, column=0, sticky="nw")

    pl_0 = Label(tp_line, text="No", font="Arial 9")
    pl_0.grid(row=0, column=0, padx=4, sticky="w")

    pl_1 = Label(tp_line, text="Type", font="Arial 9")
    pl_1.grid(row=0, column=1, padx=20, sticky="w")

    pl_2 = Label(tp_line, text="Frequency", font="Arial 9")
    pl_2.grid(row=0, column=2, padx=12, sticky="w")

    pl_3 = Label(tp_line, text="Amplitude", font="Arial 9")
    pl_3.grid(row=0, column=3, padx=0, sticky="w")

    pl_4 = Label(tp_line, text="Phase", font="Arial 9")
    pl_4.grid(row=0, column=4, padx=21, sticky="w")

    pl_5 = Label(tp_line, text="Span", font="Arial 9")
    pl_5.grid(row=0, column=5, padx=44, sticky="w")

    # Non-Periodic Grid
    wave_np_grid = LabelFrame(wave_list, bg='#C2BEBC', bd=3, text="Non-Periodic", font='Arial 12')
    wave_np_grid.grid_rowconfigure(0, weight=1)
    wave_np_grid.grid_columnconfigure(0, weight=1)
    wave_np_grid.grid(row=1, column=0, sticky="nw")

    tnp_line = Frame(wave_np_grid, bg='#C2BEBC')
    tnp_line.grid_rowconfigure(0, weight=1)
    tnp_line.grid_columnconfigure(6, weight=1)
    tnp_line.grid(row=0, column=0, sticky="nw")

    npl_0 = Label(tnp_line, text="No", font="Arial 9")
    npl_0.grid(row=0, column=0, padx=4, sticky="w")

    npl_1 = Label(tnp_line, text="Type", font="Arial 9")
    npl_1.grid(row=0, column=1, padx=20, sticky="w")

    npl_2 = Label(tnp_line, text="Time Scale(s)\n  sgn(sx)", font="Arial 9")
    npl_2.grid(row=0, column=2, padx=2, sticky="w")

    npl_3 = Label(tnp_line, text="Amplitude", font="Arial 9")
    npl_3.grid(row=0, column=3, padx=1, sticky="w")

    npl_4 = Label(tnp_line, text="Shift", font="Arial 9")
    npl_4.grid(row=0, column=4, padx=26, sticky="w")

    npl_5 = Label(tnp_line, text="Span", font="Arial 9")
    npl_5.grid(row=0, column=5, padx=46, sticky="w")


    #Composed Signals Grid
    wave_c_grid = LabelFrame(wave_list, bg = '#C2BEBC', bd = 3,width= 800,height = 700,text="Composed", font = 'Arial 12')
    wave_c_grid.grid_rowconfigure(0, weight=1)
    wave_c_grid.grid_columnconfigure(0, weight=1)
    wave_c_grid.grid(row=2,column=0,sticky=NW)
    
    #Control Panel
    del_btn = Button(controlPanel, text="Delete Wave",font=40,width = 10,bg='red',command=lambda: Buttons.delline(wave_p_grid))
    del_btn.grid(row=1,column=2,sticky=SE,padx = 10,pady = 20)
    
    add_btn = Button(controlPanel, text="Add Wave",font=40,width = 10,bg='#66FF00',command=lambda: Buttons.addline((wave_p_grid,wave_np_grid)))
    add_btn.grid(row=0,column=2,sticky=SE,padx = 10,pady = 10)

    spos_btn = Button(controlPanel, text="SuperPosition",font=('Roman', 17, 'bold'),width = 14,bg='#4CC417',command=lambda: view_graph.spos(use_waves,wave_c_grid))
    spos_btn.grid(row=0,column=0,sticky=SE,padx = 10,pady = 10)
    
    conv_btn = Button(controlPanel, text="Convolution",font=('Roman', 17, 'bold'),width = 14,bg='#307D7E',command=lambda: view_graph.conv(use_waves,wave_c_grid))
    conv_btn.grid(row=1,column=0,sticky=SE,padx = 10,pady = 10)

    #Fourier Panel
    global fft_x
    fftPanel = LabelFrame(controlPanel, bg='#6C2DC7', bd=3, text="Fourier", font='Arial 10')
    fftPanel.grid_rowconfigure(1, weight=2)
    fftPanel.grid_columnconfigure(2, weight=1)
    fftPanel.grid(row=0, column=1, sticky=(E,W,S))

    fft_btn = Button(fftPanel, text="Fourier Transform",font=('Roman', 17, 'bold'),width = 17,bg='#678003',command=lambda: fft_graph.fft(selected_wave))
    fft_btn.grid(row=0,column=0,sticky=SE,padx = 10)

    fft_x = StringVar(value=None)
    combitems = ['F(Hz)','Ω(rad/s)']
    fft_C = ttk.Combobox(fftPanel, values=combitems,state="readonly",textvariable=fft_x,width=7)
    fft_C.set('F(Hz)')
    fft_C.grid(row = 0,column=2, padx=7)

    #SubPlot Panel
    spanB = StringVar(value=0)
    spanE = StringVar(value=3.1415*2) #2π

    subpltPanel = LabelFrame(controlPanel, bg='#6C2DC7', bd=3, text="SubPlot", font='Arial 10')
    subpltPanel.grid_rowconfigure(1, weight=2)
    subpltPanel.grid_columnconfigure(2, weight=1)
    subpltPanel.grid(row=1, column=1, sticky=(E,W,S))

    subplt_btn = Button(subpltPanel, text="SubPlot",font=('Roman', 17, 'bold'),width = 15,bg='#2FF3E0',command=lambda: Plotter.subplot(use_waves,spanB,spanE))
    subplt_btn.grid(row=0,column=0,sticky=SE,padx = 10)

    subplt_spanEB = Entry(subpltPanel, font = 'Arial 9',width=6,textvariable = spanB)
    subplt_spanEB.grid(row = 0,column=1, padx=7)

    subplt_l1 = Label(subpltPanel, text="-",font="Arial 16")
    subplt_l1.grid(row=0,column=2)

    subplt_spanEE = Entry(subpltPanel, font = 'Arial 9',width=6,textvariable = spanE)
    subplt_spanEE.grid(row = 0,column=3, padx=5)

    subplt_l2 = Label(subpltPanel, text="Time Span(sec)",font="Arial 8")
    subplt_l2.grid(row=0,column=4)
    
    grid_lines[1] = Periodic_GridLine(wave_p_grid,1)
    grid_lines[2] = NonPeriodic_GridLine(wave_np_grid,2)

    
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
            self.fig.clear()
            plot = self.fig.add_subplot(111)
            plot.title.set_text(f"Fourier transform of signal no{GridLine.selected_line.no}")
            if fft_x.get() == "Ω(rad/s)":
                t = wave.fft(False) #Do fft ##Give it a boolean  True freq
                plot.set_xlabel('Ω (rad/s)')
            else:
                t = wave.fft(True) #Do fft ##Give it a boolean  True freq
                plot.set_xlabel('Frequency (Hz)')
            plot.set_ylabel('Amplitude')
            plot.plot(t[0],t[1])
            self.canvas.draw_idle()

    #Subplot        
    def subplot(signals,start,end):
        if len(signals) < 6:
            axis = []
            i=1
            first_loop = True
            for signal in signals.items():
                if first_loop:
                    axis.append(plt.subplot(len(signals),1,i))
                else:
                    axis.append(plt.subplot(len(signals),1,i, sharex=axis[0]))
                plt.plot(signal[1].t, signal[1].y)
                plt.tick_params('x', labelsize=7)
                plt.ylabel(f"Signal {signal[0]}")
                i=i+1
                first_loop = False
            plt.xlim(float(start.get()), float(end.get()))
            plt.show()
        else:
            messagebox.showerror(title='SubPlot Limit', message='Subplot cannot plot over 5 signals!')
                
    

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