import serial
import time
import colorama
from colorama import Fore, Back, Style 
from math import ceil, floor
import re
import math

class CRV:
    def __init__(self, port='/dev/ttyUSB0', verbose=False):
        self.ser = serial.Serial(port, 460800, timeout=0.1)
        self.verbose = verbose
        self.page_size = 0x400
        self.n_sample = 10
        self.rocFPGA = {1 : "4", 2:"8", 3:"C"}
        self.febFPGA = {0 : "0", 1 : "4", 2 : "8", 3 : "C"}

    def close(self):
        self.ser.close()

    def __del__(self):
        self.close()

    def cmd(self, cmd):
        self.ser.write((cmd+"\r").encode())

    def write(self, reg, value, lc=False):
        cmd = ""
        if lc:
            cmd += "LC "
        cmd += "WR "+reg+" "+value
        if self.verbose:
            print("send: ", cmd)
        self.cmd(cmd)
        if self.verbose:
            print("readback: ", self.ser.readline())
        self.ser.flushInput()

    def read(self, reg, n=1, lc=False):
        self.ser.flushInput()
        cmd = ""
        if lc:
            cmd += "LC "
        if n == 1:
            cmd += "RD "+reg
        else:
            cmd += "RDI "+reg+" "+str(n)
        if self.verbose:
            print("send: ", cmd)
        self.cmd(cmd)
        if self.verbose:
            print("readback: ", self.ser.readline())
        else:
            self.ser.readline()
        if lc:
            time.sleep(0.03)
        raw = self.ser.read(self.ser.in_waiting)
        if self.verbose:
            print("read :", raw)
        return self.parse(raw).split()

    def parse(self, response): 
        return response.decode('utf-8').replace('Socket?>','').replace('P1>','').replace('\x00\x00\x00','').replace('\x00', ' ').replace('\n', ' ').replace('\r','').replace('>','')

    def readm(self, reg, n,  lc=False):
        nn = 1024
        if n > nn:
            out = self.readm(reg=reg, n=nn,   lc=lc) + self.readm(reg=reg, n=n-nn, lc=lc)

        self.ser.flushInput()
        cmd = ""
        if lc:
            cmd += "LC "
        if lc:
            cmd += "RDM "+reg+" "+hex(n)[2:]+" 20"
        else:
            cmd += "RDM "+reg+" "+str(n)+" 10"
        if self.verbose:
            print("send: ", cmd)
        self.cmd(cmd)
        if self.verbose:
            print("readback: ", self.ser.readline())
        else:
             self.ser.readline()
        out = []
        if lc:
            time.sleep(0.2)
        else:
            time.sleep(0.0004*n)
        while self.ser.in_waiting>0:
            raw = self.ser.read(self.ser.in_waiting)
            if self.verbose:
                print("read :", raw)
                print(" ")
                print(" ")
            out = out + self.parse(raw).split()
        return out

    def readOutput(self, n=1):
        data = self.readm("21", 20*n, lc=False)
        if self.verbose:
            for n_ in range(n):
                print(data[n_*20   :n_*20+10])
                print(data[n_*20+10:n_*20+20])

    def readTriggers(self,n=1):
        data = self.readm("20", 20*n, lc=False)
        if self.verbose:
            for n_ in range(n):
                print(data[n_*20   :n_*20+10])
                print(data[n_*20+10:n_*20+20])

    def getTriggers(self, n=1):
        if self.verbose:
            print("send: UB2 "+str(n))
        self.cmd("UB2 "+str(n))
        if self.verbose:
            print("readback ", self.ser.readline())
        else:
            self.ser.readline()
        time.sleep(0.001)
        data = self.readm("20", 20*n, lc=False)
        if self.verbose:
            for n_ in range(n):
                print(data[n_*20   :n_*20+10])
                print(data[n_*20+10:n_*20+20])
        muB = []
        for n_ in range(n):
            muB.append(data[n_*20+3])
        return muB
    
    def rocDdrStatus(self, fpga=1):
        data = self.read(self.rocFPGA[fpga]+"02",4, lc=False)
        print("ROC DDR write ("+self.rocFPGA[fpga]+"02, "+self.rocFPGA[fpga]+"03): ", data[0], data[1])
        print("ROC DDR read ("+self.rocFPGA[fpga]+"04, "+self.rocFPGA[fpga]+"05):  ", data[2], data[3])

    def rocDdrRead(self, hi="0", lw="0", n=16, fpga=1):
        print("Reading ROC DDR ("+str(fpga)+") at ", hi, lw)
        self.write(self.rocFPGA[fpga]+"04", hi)
        self.write(self.rocFPGA[fpga]+"05", lw)
        data = self.readm(self.rocFPGA[fpga]+"07", n, lc=False)
        for n_ in range(n//16):
            print(data[n_*16:n_*16+16])

    def rocDdrReadEv(self, add0=True, fpga=1):
        if add0:
            if self.verbose:
                 print("Reset ROC DDR ("+str(fpga)+") Read address")
                 self.write(self.rocFPGA[fpga] +"04", "0")
                 self.write(self.rocFPGA[fpga]+"05", "0")
        read_add = self.read(self.rocFPGA[fpga]+"04", 2, lc=False)
        n = int(self.read(self.rocFPGA[fpga]+"07", 1, lc=False)[0], 16)
        if n > 1024+4:
            data = self.readm(self.rocFPGA[fpga]+"07", 4, lc=False)
            print("CORRUPT  EVENT?", data)
            return
        n16 = math.ceil(n/16)*16 # the next event always starts at a full 16 
        if n%16 == 0: # needed because we get an additional 16 woords if we have an event that would exactly fit into 16 words
            n16 = n16 + 16
        print("Read event with %i words, read total %i words" % (n, n16))
        data = self.readm(self.rocFPGA[fpga]+"07", n16-1, lc=False)
        print("words: ", n ,"status: ", data[0], ", uB: ", data[1], data[2], "(at read add: ", read_add,")")
        ev = (n - 4)//(self.n_sample + 2)
        out_data = []
        for ev_ in range(ev):
            print("%i)" % (ev_ + 1), data[ev_*(self.n_sample + 2)+3:(ev_+1)*(self.n_sample + 2)+3])
            out_data.append(data[ev_*(self.n_sample + 2)+3:(ev_+1)*(self.n_sample + 2)+3])
        if ev > 0:
            print("filler: ", data[(ev_+1)*(self.n_sample + 2)+3:])
        else:
            print("filler: ", data[4:])
        return out_data

    def rocDdrReset(self, fpga=1):
        # Don't read out the DDR
        #print("Disable the DDR read sequence")
        self.write(self.rocFPGA[fpga]+"00", "A8", lc=False) # default A8
        print("Reset DDR write address")
        self.write(self.rocFPGA[fpga]+"02","0", lc=False)
        self.write(self.rocFPGA[fpga]+"03","0", lc=False)
        self.write(self.rocFPGA[fpga]+"04","0", lc=False)
        self.write(self.rocFPGA[fpga]+"05","0", lc=False)
        if self.verbose:
            print("The read/write points should now point to 0 0 0 20")
            self.rocDdrStatus(fpga=fpga)

    def febDdrStatus(self, fpga=0):
        data = self.read(self.febFPGA[fpga]+"02",4, lc=True)
        print("FEB DDR write ("+self.febFPGA[fpga]+"02, "+self.febFPGA[fpga]+"03): ", data[0], data[1])
        print("FEB DDR read  ("+self.febFPGA[fpga]+"04, "+self.febFPGA[fpga]+"05): ", data[2], data[3])

    def febPageRead(self, hi="0", lw="0", fpga=0):
        print("Read FEB ("+str(fpga)+") Page ", hi, lw, end=" ")
        self.write("312", hi, lc=True)
        self.write("313", lw, lc=True)
        time.sleep(0.1)
        n = self.read(self.febFPGA[fpga]+"0D", lc=True)[0]
        if int(n, 16) == 1026:
            print("with NO (",int(n, 16),") events")
        else:
            print("with ", n, " (%i, ev: %i) words" % (int(n, 16), (int(n, 16)-3)/(2+self.n_sample)))
        data = self.readm(self.febFPGA[fpga]+"0C", n=int(n, 16), lc=True)
        ev = (int(n,16)-3)//(self.n_sample+2)
        #print("DEBUG", ev)
        print(data)
        for ev_ in range(ev):
            print("%02i) " % (ev_+1), data[ev_*(self.n_sample+2)+3:ev_*(self.n_sample+2)+3+(self.n_sample+2)])
        

    def febPageHeader(self, hi="0", lw="0", fpga=0):
        addr = int(hi + "%04x" % int(lw,16), 16) * self.page_size
        addr_str = "%08x" % addr
        addr_hi = addr_str[:4]
        addr_lw = addr_str[4:]
        print("Read FEB  DDR ("+str(fpga)+") for uB", hi, lw, " at ", addr_hi, addr_lw)
        self.write(self.febFPGA[fpga]+"04", addr_hi, lc=True)
        self.write(self.febFPGA[fpga]+"05", addr_lw, lc=True)
        data = self.readm(self.febFPGA[fpga]+"07", n=3, lc=True)
        if int(data[0],16)&(0x8000)>0:
            print("words (overflow!): ", data[0] ,"(%i, ev: %i)" % (int(data[0], 16)-0x8000, (int(data[0], 16)-0x8000-3)/(2+self.n_sample)), "uB: ", data[1], data[2])
        else:
            print("words: ", data[0] ,"(%i, ev: %i)" % (int(data[0], 16), (int(data[0], 16)-3)/(2+self.n_sample)), "uB: ", data[1], data[2])

    def febReset(self):
        self.write("316","20",lc=True)

    def febPwrCycle(self):
        print("Power cycling all FEB ports")
        self.cmd("PWRRST 25")

    def febSetup(self, n_sample=10):
        self.n_sample = n_sample
        print("Set external trigger to RJ45")
        self.cmd("LC TRIG 0")
        print("Set the port the FEB is connected to: 1")
        self.write("314","1",lc=True)
        print("Take new pedestral")
        self.write("316","100",lc=True)
        print("Enable self-triggering on spill gate")
        self.write("30E","2", lc=True)
        print("Set spill gate")
        print("    On-spill 0x70 @ 80MHZ (Default is 0x800)")
        self.write("305", "70", lc=True)
        print("    Off-spill 0x800 @ 80Mhz")
        self.write("306", "800", lc=True)
        print("Number of ADC samples: ", n_sample)
        self.write("30C", hex(n_sample)[2:], lc=True)
        print("Reset DDR write/read pointers")
        self.write("310","0",lc=True)
        self.write("311","0",lc=True)

    def rocSetup(self, tdaq=False, tdaq_timing=False):
        print("Test Fiber Connection")
        print(self.read("1"))
        print("Enable package forwarding to the FEB")
        if tdaq_timing:
            print("Enable Marker Sync, timing from TDAQ")
            self.write("0", hex(2**5+2**4)[2:])
        else:
            self.write("0", "0")
        print("set CSR")
        self.write("400", "A8")
        print("Reset GTP FIFO")
        self.write("2","1")
        print("Reset link reciver FIFO")
        self.write("27", "300")
        print("Reset DDR read/write addresses")
        self.write("402","0")
        self.write("403","0")
        self.write("404","0")
        self.write("405","0")
        if tdaq:
            print("Set TRIG 1")
            self.cmd("TRIG 1")


    def febPedestal(self, fpga=0):
        print("Take pedestals...")
        self.write("316","100",lc=True)
        self.ser.flushInput()
        data = self.read(self.febFPGA[fpga]+"80", "10", lc=True)
        print(data)
        return data

    def febGetThr(self, fpga=0):
        data = self.read(self.febFPGA[fpga]+"90", "10", lc=True)
        print(data)

    def febSetThr(self, ch, th, fpga=0):
        if ch == -1:
            for ch_ in range(16):
                self.febSetThr(ch_, th, fpga=fpga)
        add = "%x" % (0x90 + ch + int(self.febFPGA[fpga]+"00",16))
        print("Set threshold of fpga %i, channel %i (add %s) to %s" % (fpga, ch, add, th) )
        self.write(add, th, lc=True)
        self.febGetThr(fpga=fpga)
        #data = self.read(self.febFPGA[fpga]+"90", "10", lc=True)
        #print(data)

    def rocUBunchCnt(self):
        return self.read("36", 3)

    def febAFEHighGain(self, gain=31, afe=1, fpga=0):
        afe_ = hex(afe + int(self.febFPGA[fpga], 16))[2:]
        #print("Increase PGA gain from 24dB to 30dB")
        #self.write("133", hex(2**13)[2:], lc=True)
        #self.write("133", "2004", lc=True) # default 2004 30dB, 20Mhz
        
        #print("Increase LNA gain from 12dB to 24dB")
        #self.write("134", "2140", lc=True)
        #self.write("134", "4140", lc=True) # default 4140, active terminatin, 100Ohm, 12dB  
        if gain == 0:
            print("Disable digital gain, set LNA gain to nominal 12dB")
            self.write(afe_+"34", "4140", lc=True)
            self.write(afe_+"03", "0", lc=True)
        else:
            print("Enable digital gain, set to %.1fdB" % (gain*0.2))
            self.write(afe_+"03", hex(2**12)[2:],lc=True)
            print("Increase LNA gain from 12dB to 24dB")
            self.write(afe_+"34", "2140", lc=True)
        val = hex(gain * 2**11)[2:]
        self.write(afe_+"0D", val, lc=True) # ch1
        self.write(afe_+"0F", val, lc=True) # ch2
        self.write(afe_+"11", val, lc=True) # ch3
        self.write(afe_+"13", val, lc=True) # ch4
        self.write(afe_+"19", val, lc=True) # ch8
        self.write(afe_+"1b", val, lc=True) # ch7
        self.write(afe_+"1d", val, lc=True) # ch6
        self.write(afe_+"1f", val, lc=True) # ch5

    def rocUBCnt(self):
        data = self.read("36", n=3)
        print(data)

    def resetLink(self):
        self.write("0", "8")
        print(self.read("1"))

    def setup(self, n_sample=10, tdaq=False, tdaq_timing=False, gain=0, nfpga=1, nafe=2):
        self.rocSetup(tdaq=tdaq, tdaq_timing=tdaq_timing)
        self.rocDdrReset()
        self.febSetup(n_sample=n_sample)
        for fpga in range(nfpga):
            for afe in range(1, nafe):
                 print("DEBUG", afe, fpga)
                 self.febAFEHighGain(gain,afe=afe,fpga=fpga)

    def markerBits(self):
        data = self.read("77", lc=False)
        return "{0:b}".format(int(data[0],16))

    def single(self):
        self.rocDdrReset()
        time.sleep(0.1)
        self.getTriggers()
        return self.rocDdrReadEv()
