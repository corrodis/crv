import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.optimize import curve_fit
import numpy as np

def func(x, a, b):
    return a + b*x

if False:
    data = []
    files = ["syncTestGain28FPGA1D20000_300.csv", "syncTestGain28FPGA1D50000_1000.csv", "syncTestGain28FPGA1D200000_1000.csv", "syncTestGain28FPGA1D100000_1000.csv"]
    D = [20000, 50000, 200000, 100000]
    skip = [0,20,0,10]

    for k, f in enumerate(files):
        data.append(np.loadtxt("data/"+f)[:,skip[k]:])
    for k, d in enumerate(data):
        plt.plot(d[1,:]+k*0.1, np.array(d[2,:])*1e-3,'.', label=f"{D[k]/200}")
    plt.legend(title="time between heartbeats [us]")
    plt.xlabel("hits/request")
    plt.ylabel("readout time [us]")
    plt.tight_layout()
    plt.show()


if False:
    files_ = ["syncTestGain28FPGA1D20000_300.csv", "syncTestGain28FPGA1D50000_1000.csv", "syncTestGain28FPGA1D200000_1000.csv", "syncTestGain28FPGA1D100000_1000.csv", "syncTestGain10FPGA1_1000.csv", "syncTestGain20FPGA1_1000.csv", "syncTestGain28FPGA1_1000.csv", "syncTestGain28FPGA2_1000.csv", "syncTestGain28FPGA4D200000_1000.csv", "syncTestGain28FPGA4Th10D200000_1000.csv", "syncTestGain28FPGA4Th8D200000_100.csv", "syncTestGain28FPGA4Th8D200000_300.csv","syncTestEmpty100.csv","syncTestOutOfSync100.csv"]

    FPGAS = [1, 1, 1, 1, 1, 1, 1, 2, 4, 4, 4, 4, 4, 0]
    skip  = [0, 20, 0, 10, 0, 0, 6, 0, 45, 10, 0, 5, 0, 0]
    data_ = []
    nsamples = 10
    for k, f in enumerate(files_):
        data_.append(np.loadtxt("data/"+f)[:,skip[k]:])
    nn_    = np.array([])
    delay_ = np.array([])
    test = {}
    for k, d in enumerate(data_):
      if k not in [10]:
        if FPGAS[k] not in test:
            plt.plot( np.floor((d[1,:]*8-2)/(nsamples + 2))+k*0.1, np.array(d[2,:])*1e-3,'.', label=f"{FPGAS[k]} FPGAs", color=sns.color_palette()[FPGAS[k]])
            test[FPGAS[k]] = FPGAS[k]
        else:
            plt.plot( np.floor((d[1,:]*8-2)/(nsamples+2))   +k*0.1, np.array(d[2,:])*1e-3,'.', color=sns.color_palette()[FPGAS[k]])
      if k not in [10, 13]:
          nn_    = np.concatenate([nn_,     np.floor((np.array(d[1,:])*8-2)/(nsamples+2))])
          delay_ = np.concatenate([delay_,  np.array(d[2,:])*1e-3]) 

    popt, pcov = curve_fit(func, nn_, delay_)
    if nsamples == -1:
        plt.text(0.55, 0.1, 'delay: %.1f $\mu s$ + %.1f $\mu s / word \cdot N$' % (popt[0], popt[1]) , fontsize=12, horizontalalignment='center',
            verticalalignment='center', transform=plt.gca().transAxes)
    else:
        plt.text(0.55, 0.1, 'delay: %.1f $\mu s$ + %.1f $\mu s / hit(2+%i words) \cdot N$' % (popt[0], popt[1], nsamples) , fontsize=12, horizontalalignment='center',
            verticalalignment='center', transform=plt.gca().transAxes)
    plt.legend(title="data from 1 FEB and  ")
    if nsamples == -1:
        plt.xlabel("words/request")
    else:
        plt.xlabel("hits/request")
    plt.ylabel("readout time [us]")
    plt.tight_layout()
    plt.show()


if True:



    files_ = ["syncTestGain28FPGA1D20000_300.csv", "syncTestGain28FPGA1D50000_1000.csv", "syncTestGain28FPGA1D200000_1000.csv", "syncTestGain28FPGA1D100000_1000.csv", "syncTestGain10FPGA1_1000.csv", "syncTestGain20FPGA1_1000.csv", "syncTestGain28FPGA1_1000.csv", "syncTestGain28FPGA2_1000.csv", "syncTestGain28FPGA4D200000_1000.csv", "syncTestGain28FPGA4Th10D200000_1000.csv","syncTestGain28FPGA4Th8D200000_300.csv","syncTestEmpty100.csv","syncTestGain28FPG1Nsample8_1000.csv","syncTestGain28FPG4Nsample8_1000.csv", "syncTestGain28FPG4Nsample8_1000_2.csv","syncTestGain28FPG4Nsample2_1000.csv",]


    FPGAS = [1, 4, 4,5, 1, 1, 1, 1, 1, 1, 1, 2, 4, 4, 4, 4, 4, 0]
    skip  = [0, 20, 0, 10, 0, 0, 6, 0, 45, 10,  5, 0,  10, 10, 20, 50]
    nsamples = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 8, 8, 2, 2]
    data_ = []
    nsamples_ = -1 # 10
    for k, f in enumerate(files_):
        data_.append(np.loadtxt("data/"+f)[:,skip[k]:])
    nn_    = np.array([])
    delay_ = np.array([])
    test = {}
    for k, d in enumerate(data_):
      if k not in [10]:
        if nsamples[k] not in test:
            plt.plot( np.floor((d[1,:]*8-2)/(nsamples_ + 2))+k*0.1, np.array(d[2,:])*1e-3,'.', label=f"{nsamples[k]} samples", color=sns.color_palette()[nsamples[k]%10//2])
            test[nsamples[k]] = FPGAS[k]
        else:
            plt.plot( np.floor((d[1,:]*8-2)/(nsamples_+2))   +k*0.1, np.array(d[2,:])*1e-3,'.', color=sns.color_palette()[nsamples[k]%10//2])
      if k not in [10, 13]:
          nn_    = np.concatenate([nn_,     np.floor((np.array(d[1,:])*8-2)/(nsamples_+2))])
          delay_ = np.concatenate([delay_,  np.array(d[2,:])*1e-3]) 

    popt, pcov = curve_fit(func, nn_, delay_)
    #if nsamples == -1:
    plt.text(0.55, 0.1, 'delay: %.1f $\mu s$ + %.1f $\mu s / word \cdot N$' % (popt[0], popt[1]) , fontsize=12, horizontalalignment='center',
            verticalalignment='center', transform=plt.gca().transAxes)
    #else:
    #    plt.text(0.55, 0.1, 'delay: %.1f $\mu s$ + %.1f $\mu s / hit(2+%i words) \cdot N$' % (popt[0], popt[1], nsamples) , fontsize=12, horizontalalignment='center',
    #        verticalalignment='center', transform=plt.gca().transAxes)
    plt.legend(title="event: (2 + nsample) words")
    #if nsamples == -1:
    plt.xlabel("words/request")
    #else:
    #    plt.xlabel("hits/request")
    plt.ylabel("readout time [us]")
    plt.tight_layout()
    plt.show()
