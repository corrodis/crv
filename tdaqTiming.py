import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
import numpy as np

ev_bad   = [ 0]
time_bad = [43]
ev =   [ 8,  8,  4,  1,  2,  44,  50,  33,  50,  46,  46, 46,   33, 50,   49,  50]
time = [51, 53, 36, 31, 37, 148, 230, 166, 168, 158, 168, 154, 121, 163, 149, 175]

two_ev   = [ 62,  65,  49,  56,  52] 
two_time = [198, 240, 165, 182, 173]

four_ev   = [ 0,  0,  0, 52,  85,  81,  33] 
four_time = [29, 36, 25, 177, 260, 260, 121]

def func(x, a, b):
    return a + b*x
popt, pcov = curve_fit(func, ev_bad+ev+two_ev+four_ev, time_bad+time+two_time+four_time)

tt = np.array([0,80])
#plt.plot(tt, func(tt, *popt))
plt.title("single FEB")
plt.plot(ev, time, 'o', label="1 FPGA")
plt.plot(two_ev, two_time, 'd', label="2 FPGA")
plt.plot(four_ev, four_time, '>', label="4 FPGA")
plt.plot(ev_bad, time_bad, 'v', label="0 FPGA")
plt.xlabel("hits per uBunch")
plt.ylabel("data request delay [$\mu s$]")
plt.text(0.25, 0.82, 'delay: %.1f $\mu s$ + %.1f $\mu s \cdot$ (hits/ev)' % (popt[0], popt[1]) , horizontalalignment='center',
        verticalalignment='center', transform=plt.gca().transAxes)
plt.legend(ncol=2)
plt.tight_layout()
plt.savefig("plots/crv_vertical_slice_delay.pdf")
plt.savefig("plots/crv_vertical_slice_delay.png")
plt.show()
