import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
import copy

class Wave:
    def __init__(self,start=-np.pi,end=np.pi,step=100_000):
        self.start = start
        self.end = end  ##Changed to domain
        self.dlength = self.end-self.start #Lenght of the domain
        self.step = step
        self.t = np.linspace(self.start,self.end,int(self.dlength*self.step))

    def setDomain(self,waves:list):
        waves.append(self)
        start = waves[0].start
        end = waves[0].end
        for wave in waves:
            if wave.start < start:
                start = wave.start
            if wave.end > end:
                end = wave.end
        return Wave(start,end)
    
    def convolve(self,waves:list):     
        convolved_wave = self.setDomain(waves)
        yc = signal.unit_impulse(len(convolved_wave.t),'mid')
        for wave in waves:
            yc = signal.fftconvolve(yc,wave.y,'same')/(self.step*convolved_wave.dlength)**0.5
        convolved_wave.y = yc
        return convolved_wave
        
    def superposition(self, waves:list):
        #temp_waves = copy.deepcopy(waves)
        superposed_wave = self.setDomain(waves)
        ys=np.zeros(int(np.ceil(superposed_wave.dlength*self.step))) #array filled with max domain lenght zeros, rounded up
        for wave in waves:
            start_diff = wave.start - superposed_wave.start #calculate start difference
            add_from = int(np.ceil(start_diff*self.step)) #find start index, rounded up
            ys[add_from:add_from+len(wave.y)] += wave.y
        superposed_wave.y = ys
        return superposed_wave
    
    def fft(self,freq): ##ADD  parameter freq
        N = len(self.y)
        self.yf = np.fft.rfft(self.y)[:N//2]*2*self.step/self.dlength
        self.tf = np.fft.rfftfreq(N, np.diff(self.t)[0])[:N//2]
        return (self.tf, abs(self.yf)) 
    
        
class Sinewave(Wave):
    def __init__(self,frequency,amplitude=1,phase=0,start=-np.pi,end=np.pi,step=100_000):
        super().__init__(start,end,step)
        self.a = amplitude
        self.phase = phase
        self.f = frequency
        self.y = self.a*np.sin(2*np.pi*self.f*self.t - self.phase)
        self.t_for_fft = np.linspace(0, 1/(self.step*4*self.f), int(1/self.step), endpoint=False) #WHAT THE FUCISDAT???
        self.y_for_fft = self.a*np.sin(2*np.pi*self.f*self.t_for_fft - self.phase)

    def __str__(self):
        return f'sine wave with:\nfrequency = {self.f}\namplitude = {self.a}\nphase = {self.phase}'


class Square_wave(Wave): 
    def __init__(self,frequency,amplitude=1,phase=0,start=-np.pi,end=np.pi,step=100_000):
      super().__init__(start,end,step)
      self.a = amplitude
      self.phase = phase
      self.f = frequency
      self.y = self.a * signal.square(np.sin(2*np.pi*self.f*self.t - self.phase))
      self.t_for_fft = np.linspace(0, 1/(self.step*4*self.f), int(1/self.step) , endpoint=False)
      self.y_for_fft = self.a * signal.square(np.sin(2*np.pi*self.f*self.t_for_fft - self.phase))
        
      def __str__(self):
        return f'square wave with:\nfrequency = {self.f}\namplitude = {self.a}\nphase = {self.phase}'

class Trianglewave(Wave):
   def __init__(self,frequency,amplitude=1,phase=0,start=-np.pi,end=np.pi,step=100_000):
      super().__init__(start,end,step)
      self.a = amplitude
      self.phase = phase
      self.f = frequency
      self.y = self.a * signal.sawtooth(2*np.pi*self.f*self.t - self.phase,width = 0.5)