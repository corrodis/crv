import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.optimize import curve_fit
import numpy as np

def func(x, a, b):
    return a + b*x


if True:
    files_ = ["syncTestGain28And28FPG1Port1And9_1000.csv", "syncTestGain28And28FPG1Port1And9_1000_2.csv", "syncTestGain28And28Th10FPG1Port1And9_1000.csv", "syncTestGain28And28Th8FPG1Port1And9_1000.csv","syncTestGain0And0FPG1Port1And9_1000.csv","syncTestGain28And0FPG1Port1And9_1000.csv","syncTestGain28Th10And0FPG1Port1And9_1000.csv", "syncTestGain28Th8And0FPG1Port1And9_1000.csv","syncTestGain28Th8And10FPG1Port1And9_1000.csv", "syncTestGain28And10FPG4Port1And9_1000.csv", "syncTestGain28Th10And28FPG1Port1And9_1000.csv","syncTestGain28Th10And0FPG1Port1And9_1000.csv", "syncTestGain28Th10And0FPG1Port1And9_1000_2.csv",  "syncTestGain28Th10And0FPG1Port1And9_1000_3.csv", "syncTestGain28Th10And10FPG1Port1And9_1000_3.csv","syncTestGain28Th28And10FPG1Port1And9_1000_3.csv", "syncTestGain28Th8And28Th8FPG1Port1And9_1000_5.csv","syncTestGain28Th8And28Th8FPG1Port1And9_1000_6.csv"]

    skip  = np.ones([len(files_)], dtype='int')*10
    data_ = []
    for k, f in enumerate(files_):
        data_.append(np.loadtxt("data/"+f)[:,skip[k]:])
    nn1_    = np.array([])
    nn2_    = np.array([])
    nn_    = np.array([])
    delay_ = np.array([])
    test = {}
    for k, d in enumerate(data_):
      if k in [0,1,2,4,5,6]:#,10,11,12]:
        if k in [0]:
          plt.plot(np.minimum(d[4,:], d[3,:]) +0.1,        np.array(d[2,:])*1e-3,'v', label=f"# hits of less active FEB", color=sns.color_palette()[0])
          plt.plot(np.maximum(d[4,:], d[3,:]) -0.1,        np.array(d[2,:])*1e-3,'x', label=f"# hits of more active FEB", color=sns.color_palette()[2]) 
          plt.plot(d[3,:]+d[4,:],                          np.array(d[2,:])*1e-3,'.', label=f"sum of hits from both FEBs", color='k')#sns.color_palette()[2]) 
        else:
          plt.plot(np.minimum(d[4,:], d[3,:]) +0.1,        np.array(d[2,:])*1e-3,'v', color=sns.color_palette()[0])
          plt.plot(d[3,:]+d[4,:],                          np.array(d[2,:])*1e-3,'.', color='k')#sns.color_palette()[2]) 
          plt.plot(np.maximum(d[4,:], d[3,:]) -0.1,        np.array(d[2,:])*1e-3,'x', color=sns.color_palette()[2])
    
    
    plt.plot([0,50], func(np.array([0,50]),43.0, 4.5),'--', color='k', label="expectations from single FEB")
    plt.legend()
    plt.xlabel("hits/request")
    plt.ylabel("readout time [us]")
    plt.tight_layout()
    plt.show()


if False:
    files_ = ["syncTestGain31Th10And28FPG1Port1And9_1000.csv", "syncTestGain31Th8And28FPG1Port1And9_1000_3.csv", "syncTestGain31Th9And28Th9FPG1Port1And9_1000.csv", "syncTestGain31Th8And28FPG1Port1And9_1000_2.csv", "syncTestGain31Th9And28FPG1Port1And9_1000.csv"]


    skip  = [50, 200, 50, 50, 50]
    data_ = []
    for k, f in enumerate(files_):
        data_.append(np.loadtxt("data/"+f)[:,skip[k]:])
    nn1_    = np.array([])
    nn2_    = np.array([])
    nn_    = np.array([])
    delay_ = np.array([])
    test = {}
    for k, d in enumerate(data_):
      if k not in  [1]:
        if k in [0]:
          plt.plot(d[4,:] +0.1,        np.array(d[2,:])*1e-3,'.', label=f"# hits of less active FEB", color=sns.color_palette()[0])
          plt.plot(d[3,:] -0.1,        np.array(d[2,:])*1e-3,'.', label=f"# hits of more active FEB", color=sns.color_palette()[1]) 
          plt.plot(d[3,:]+d[4,:],                          np.array(d[2,:])*1e-3,'.', label=f"sum of hits from both FEBs", color=sns.color_palette()[2]) 
        else:
          plt.plot(d[4,:] +0.1,        np.array(d[2,:])*1e-3,'.', color=sns.color_palette()[0])
          plt.plot(d[3,:]+d[4,:],                          np.array(d[2,:])*1e-3,'.', color=sns.color_palette()[2]) 
          plt.plot(d[3,:] -0.1,        np.array(d[2,:])*1e-3,'.', color=sns.color_palette()[1])
    
    
    plt.plot([0,50], func(np.array([0,50]),43.0, 4.5),'--', color='k', label="expectations from single FEB")
    plt.legend()
    plt.xlabel("hits/request")
    plt.ylabel("readout time [us]")
    plt.tight_layout()
    plt.show()
