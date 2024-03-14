import tools as tl
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

w1 = tl.Sinewave(3,2,0)
w2 = tl.Sinewave(3,2,0,-4,6)
w3 = tl.Sinewave(3,7,0,-1,1)
w4 = w1.superposition([w2,w3])
w5 = w1.convolve([w2,w3])

# print(w1.t,w2.y)
# print(w4.t,w4.y)
plt.plot(w4.t,w4.y)
plt.show()

