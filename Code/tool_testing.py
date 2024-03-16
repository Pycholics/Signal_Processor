import tools as tl
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft , fftshift

w1 = tl.Square_wave(30,2,0,-4,-2)
w2 = tl.Sinewave(18,2,0,-4,-2)
w3 = tl.Sinewave(3,7,0,-10,-5)
wup = tl.Square_Pulse()
w4 = w1.superposition([w2,w3])
w5 = w1.convolve([w2,w3])
w6 = signal.fftconvolve(w1.y,signal.unit_impulse(100_000,'mid'),'same')
w7 = tl.Delta()
# print(w1.t,w2.y)
# print(w4.t,w4.y)
#plt.plot(w5.t,w5.y)
# plt.plot(np.linspace(-np.pi,np.pi,len(w6)),w6)
#plt.plot(np.fft.fftfreq(300_000,1/10000),np.fft.fft(np.repeat([0,1,0],100_000)/100000))
#a = fftshift(fft(np.repeat([0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],20))/20)
#a = [a[i] for i in range(len(a)) if i%2==0]
x1,y1 = w1.fft()
x2,y2 = w2.fft(False)
x3,y3 = w3.fft(False)
x4,y4 = wup.fft()
x5,y5 = w7.fft()
ax1 = plt.subplot(511)
ax1 = plt.plot(x1,y1)
plt.xlim(-500,500)
ax2 = plt.subplot(512)
ax2 = plt.plot(x2,y2)
plt.xlim(-400,400)
ax3 = plt.subplot(513)
ax3 = plt.plot(x3,y3)
plt.xlim(-100,100)
ax4 = plt.subplot(514)
ax4 = plt.plot(x4,y4)#,x4,np.sinc(x4))
plt.xlim(-20,20)
ax5 = plt.subplot(515)
ax5 = plt.plot(x5,y5)
plt.show()

