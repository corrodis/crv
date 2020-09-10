import numpy as np
import struct

fname = "sten_test10000_2_2.bin"
nn_ = 10000

fname = "sten_test100000.bin"
nn_ = 100000
nmax = 10

fname = "sten_test10000.bin"
nn_ = 10000
nmax = 10


fname = "sten_test1000_1.bin"
nn_ = 396
nmax= 55

print(fname)
with open(fname, mode='rb') as file:
    fileContent = file.read()

def get(n):
    return  "%04x" % struct.unpack("<H", fileContent[n*2:(n+1)*2])

def readEv(start, v=1, err=0):
    cnt_check = True
    nn = get(start)
    if nn == 'cafe':
        #print ("TIMEOUT PACKAGE?")
        return readEv(start+4, v=v)
    if get(start+1) != '8050':
        print("NOT A HEADER PACKAGE!!! at", start+1, get(start+1))
        return readEv(start+1, v=v, err=err+1)
    n = int(nn, 16)
    ev = int(get(start+2),16)-1
    if (ev+2)*16 != n:
        #print("BYTE CNT AND PACKAGE CNT IS NOT CONSISTENT!", n , "!=", (ev+2)*16)
        cnt_check = False
    uB = int(get(start+3),16) + int(get(start+4),16) * 0x10000 + int(get(start+5),16) * 0x100000000
    if v>0:
      print("Word", start, "n_bytes", n, "hits", ev, "uB:", uB)
    if v>1:
      for j in range(0, n//2):
        print(get(start+j), end=" ")
        if j%8==7:
            print("")
    ev_next = (ev+2)*8#n//2#(math.ceil(n/16)*16)//2
    return ev_next+start, uB, ev-1, cnt_check, err


ev_n = 0
evs_ = np.ones([nn_]) * np.nan
check_ = np.zeros([nn_])
err_ = np.zeros([nn_])
evs = []
ubs = []
uB_=1
missmatch = False
while ev_n + 4 < len(fileContent)//2:
    ev_n, uB, ev, check, err = readEv(ev_n, 0)
    missmatch = False
    if uB != uB_ + 1:
        print("uB MISSMATCH!", uB)
        missmatch = True
    print("uB: ", uB)
    uB_ = uB
    #if np.isnan(ev):
    #    evs.append(-1)
    #else:
    evs.append(ev)
    ubs.append(uB)
    if (np.isnan(uB) == False)&(missmatch == False):
        if uB < nn_:
            evs_[uB] = ev
            check_[uB] = check
            err_[uB] = err
            #tos_[uB] = to

evs  = np.array(evs)
evs_ = np.array(evs_)
ubs  = np.array(ubs)
check_ = np.array(check_)
err_ = np.array(err_)

evs_ = evs_ - evs_//5

import matplotlib.pyplot as plt
import seaborn as sns


f = plt.figure(figsize=[6.4*2, 4.8])
ax1 = plt.subplot(121)
good = np.isnan(evs_) == False
bad  = np.isnan(evs_)
check = check_ == False
errors = err_ > 0
#timeout = tos_ > 0
plt.plot(np.argwhere(good), evs_[good], '.',markersize=2, label="good")
plt.plot(np.argwhere(check&good), evs_[check&good], '.',markersize=2, label="byte cnt issue")
plt.plot(np.argwhere(errors&good), evs_[errors&good], '.',markersize=2, label="surpluse words")
plt.plot(np.argwhere(bad)[2:-60], np.zeros([np.argwhere(bad).shape[0]])[2:-60]  , 'o',markersize=2,color=sns.color_palette()[3], label="corrupt")
plt.ylabel("hits per uBunch")
plt.xlabel("uBunch [128us]")
plt.legend()
plt.ylim([-0.5,nmax]) 
plt.subplot(122, sharey=ax1)
plt.hist(evs_[good], bins=np.arange(nmax)-0.5, orientation='horizontal',label="all")
plt.hist(evs_[good&check], bins=np.arange(nmax)-0.5, orientation='horizontal', label="byte cnt issue (%.1f%%)" % (np.argwhere(check).shape[0]/check.shape[0]*100.))
plt.hist(evs_[good&errors], bins=np.arange(nmax)-0.5, orientation='horizontal', label="surpluse words (%.1f%%)" % (np.argwhere(errors).shape[0]/errors.shape[0]*100.))
plt.legend()
plt.tight_layout()
plt.subplots_adjust(wspace=0.1, hspace=0)
plt.show()

