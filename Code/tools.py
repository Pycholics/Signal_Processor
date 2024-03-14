import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
import copy

class Wave:
    def __init__(self,duration=6,step=1/100_000):
        self.d = duration     ##Change to Span 
        self.step = step
        self.t = np.linspace(0,self.d,int(self.d/self.step),endpoint = False)
    
    def convolve(self,other_waves):
        maxlen = 0
        maxwave = 0
        other_waves.append(self)
        for i in range(len(other_waves)):
            if len(other_waves[i].y) > maxlen:
                maxlen = len(other_waves[i].y)
                maxwave = other_waves[i]
                
        convolved_wave = Wave(duration = maxwave.d)
        yc =maxwave.y
        other_waves.remove(maxwave)
        for wave in other_waves:
            yc = signal.fftconvolve(yc,wave.y,'same')*(self.step*self.d)**0.5
        convolved_wave.y = yc
        return convolved_wave
        
    def superposition(self, other_waves):
        maxlen = 0
        maxwave = 0
        other_waves.append(self)
        temp_waves = copy.deepcopy(other_waves)
        for i in range(len(temp_waves)):
            if len(temp_waves[i].y) > maxlen:
                maxlen = len(temp_waves[i].y)
                maxwave = temp_waves[i]
        
        superposed_wave = Wave(duration = maxwave.d)
        ys = 0
        for wave in temp_waves:
            if len(wave.y) < maxlen:
                print(len(wave.y))
                wave.y = np.append(wave.y,np.zeros(maxlen-len(wave.y)))
                print(len(wave.y))
                ys += wave.y
            elif len(wave.y) == maxlen:
                ys += wave.y
        superposed_wave.y = ys
        return superposed_wave
    
    def fft(self,freq): ##ADD  parameter freq
        N = len(self.y)
        self.yf = np.fft.rfft(self.y)[:N//2]*2*self.step/self.d
        self.tf = np.fft.rfftfreq(N, np.diff(self.t)[0])[:N//2]
        return (self.tf, abs(self.yf)) 
    
        
class Sinewave(Wave):
    def __init__(self,frequency,amplitude=1,phase=0,duration=6,step=1/100_000):
        super().__init__(duration,step)
        self.a = amplitude
        self.phase = phase
        self.f = frequency
        self.y = self.a*np.sin(2*np.pi*self.f*self.t - self.phase)
        self.t_for_fft = np.linspace(0, 1/(self.step*4*self.f), int(1/self.step), endpoint=False) #WHAT THE FUCISDAT???
        self.y_for_fft = self.a*np.sin(2*np.pi*self.f*self.t_for_fft - self.phase)

    def __str__(self):
        return f'sine wave with:\nfrequency = {self.f}\namplitude = {self.a}\nphase = {self.phase}'


class Square_wave(Wave): 
    def __init__(self,frequency,amplitude=1,phase=0,duration=6,step=1/100_000):
      super().__init__(duration,step)
      self.a = amplitude
      self.phase = phase
      self.f = frequency
      self.y = self.a * signal.square(np.sin(2*np.pi*self.f*self.t - self.phase))
      self.t_for_fft = np.linspace(0, 1/(self.step*4*self.f), int(1/self.step) , endpoint=False)
      self.y_for_fft = self.a * signal.square(np.sin(2*np.pi*self.f*self.t_for_fft - self.phase))
      
        
      def __str__(self):
        return f'square wave with:\nfrequency = {self.f}\namplitude = {self.a}\nphase = {self.phase}'

class Trianglewave(Wave):
   def __init__(self,frequency,amplitude=1,phase=0,duration=6,step=1/100_000):
      super().__init__(duration,step)
      self.a = amplitude
      self.phase = phase
      self.f = frequency
      self.y = self.a * signal.sawtooth(2*np.pi*self.f*self.t - self.phase,width = 0.5)