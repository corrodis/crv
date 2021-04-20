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

fname = "empty_10000.bin"
nstart=0
nn_ = 10000

fname = "empty_100_.bin"
fname = "empty_160_.bin"
fname = "empty_n10_D20000.bin"
fname = "empty_n100_D20000.bin"
fname = "empty_n1000_D20000.bin"
fname = "empty_n10000_D20000.bin"
fname = "test.bin"
fname = "largeRead10000_2.bin"
fname = "consecutiveRead_2.bin"
fname = "header_test.bin"
fname = "testtest.bin"
fname = "syncTestGain28FPGA1D20000_300.bin"

import sys

v = 1

if len(sys.argv) <= 1:
    print("USAGE: python readTDAQ.py FILENAME")
    sys.exit()

if len(sys.argv)>2:
    v = int(sys.argv[2])

fname = sys.argv[1]

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
        if get(start+1) == '8550':
            print("TIMEOUT")
            if v >2 :
              for k in range(10):
                print(get(start+k), end=" ")
              print(" ")
            return start+7, np.nan, 0, False, 2
        else:    
          if v > 2:
            print("NOT A HEADER PACKAGE!!! at", start+1, get(start+1))
        return readEv(start+1, v=v, err=err+1)
    n = int(nn, 16)
    ev = int(get(start+2),16)-1
    if (ev+2)*16 != n:
        #print("BYTE CNT AND PACKAGE CNT IS NOT CONSISTENT!", n , "!=", (ev+2)*16)
        cnt_check = False
    uB = int(get(start+3),16) + int(get(start+4),16) * 0x10000 + int(get(start+5),16) * 0x100000000
    fbctrl = True
    if (get(start+8) != '0061'):
        #print("TEST", get(start+8), get(start+9), get(start+10))
        print("Missing Fibre Ctrl!")
        fbctrl = False
        #for j in range(0, ((ev+2)*16)//2):
        #  print(get(start+j), end=" ")
        #  if j%8==7:
        #    print("")
    if v>0:
      cnt = int(get(start+9),16)
      print("Word", start, "n_bytes", n, "(", cnt, ")", "hits", ev, "uB:", uB)
    if v>1:
      #for j in range(0, n//2):
      for j in range(0, ((ev+2)*16)//2):
        print(get(start+j), end=" ")
        if j%8==7:
            print("")
    ev_next = (ev+2)*8#n//2#(math.ceil(n/16)*16)//2
    return ev_next+start, uB, ev-1, cnt_check, err, fbctrl





ev_n = nstart
evs_ = np.ones([nn_]) * np.nan
check_ = np.zeros([nn_])
err_ = np.zeros([nn_])
evs = []
ubs = []
uB_=1
missmatch = False
n_total = 0
n_missmatch = 0
n_fbctrl = 0

data_ev = {}

while ev_n + 4 < len(fileContent)//2:
    ev_n, uB, ev, check, err, fbctrl = readEv(ev_n, v)
    if not np.isnan(uB):
        data_ev[uB] = ev
    else:
        data_ev[uB_+1] = -1
    missmatch = False
    if uB != uB_ + 1:
        print("uB MISSMATCH!", uB)
        n_missmatch = n_missmatch + 1
        missmatch = True
    #print("uB: ", uB)
    uB_ = uB
    n_total = n_total + 1 
    if fbctrl is False:
        n_fbctrl = n_fbctrl + 1

    #if ev_n > nn_:
    #    break
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
print("n_total:", n_total)
print("n_missmatch:", n_missmatch)
print("n_fbctrl:", n_fbctrl)

if False:
    ftimes = open(fname[:-3]+"dat", 'r')
    times = []
    for line in ftimes.readlines():
        #print(line[:2])
        if line[:2] == "0x":
            times.append(int(line[2:],16))
            #print(line, int(line[2:],16))

    #data1 = {}
    data_time = {}
    for j, t in enumerate(times):
        #print(0x1000+len(times)-j-1, t * 6.4)
        #data1[0x1000+len(times)-j-1] = {'t': t * 6.4}
        data_time[0x1000+j]              = t * 6.4
        #data_time[0x1+j]              = t * 6.4

    dout = np.array([list(data_ev.keys()), list(data_ev.values()), [data_time[ev] for ev in data_ev]])
    np.savetxt("data/"+fname[4:-3]+"csv", dout)


