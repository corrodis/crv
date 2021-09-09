import numpy as np
import struct
import pandas as pd


class CRV:
    def __init__(self, fname="", folder="data/"):
        self.fname = folder+fname
        self.n = 0 # current read position
        
        self.file = open(self.fname, "rb")
        self.file.seek(0,2)
        self.n_end = self.file.tell()
        self.file.seek(0,0)
        self.setNSamples()

        # Data Frames
        self.data_header = []
        self.data_event = []
        #self.df_header = None
        #self.df_events = None

        #self.fileContent = self.ile.read()
    
    def setNSamples(self, n=10):
        self.n = n

    class Header:
        def __init__(self, valid, uB, byt, pkt, formatv, stuff):
            self.valid   = valid
            self.uB      = uB
            self.byt     = byt
            self.pkt     = pkt
            self.formatv = formatv
            self.stuff   = stuff

        def print(self):
            print("=== HEADER ===") 
            print("uB:     %016x" % self.uB)
            print("byt:    %04x" % self.byt)
            print("pkt:    %04x" % self.pkt)
            print("stuff:  %04x %04x" % (self.formatv, self.stuff))


    class Status:
        def __init__(self, valid, word_cnt, trg_count, active_feb, status):
            self.valid  = valid
            self.wrd    = word_cnt
            self.trg    = trg_count
            self.active = active_feb
            self.status = status

        def print(self):
            print("=== CRV STATUS ===")
            print("wrd:    %04x" % self.wrd)
            print("trg:    %04x" % self.trg)
            print("active: %08x" % self.active)
            print("status: %04x" % self.status)

    class PayloadHeader:
        def __init__(self, valid, uB, n_words):
            self.valid   = valid
            self.uB      = uB
            self.n_words = n_words

        def print(self, words):
            print("=== PAYLOAD ===")
            print("uB: %08x" % self.uB)
            print("n_words: %04x" % self.n_words)
            print("events:  %04x" % (self.n_words//words) )
    
    class Event:
        def __init__(self, ch, n, timestamp, wf):
            self.ch = ch
            self.n  = n
            self.timestmap = timestamp
            self.wf = wf

        def print(self):
            print("-- Event --")
            print("ch:        %04x" % self.ch)
            print("timestamp: %03x" % self.timestmap)
            print("n:         %01x" % self.n)

    def read(self,n):
        return self.file.read(n)

    def readPackage(self, verbose=True):
        data = struct.unpack("<HHHHHHHH",self.read(2*8))
        if verbose:
            print("%04x %04x %04x %04x %04x %04x %04x %04x" % (data) )
        return data

    def findHeader(self, verbose=True):
        start = self.file.tell()
        while self.file.tell() < self.n_end:
            data = struct.unpack("<H",self.read(2))
            #print(self.file.tell()-2, "0x%04x" % (data[0]))
            if data[0] == 0x8050:
                self.file.seek(-2*2,1)
                if verbose:
                   print("Found next header package at byte 0x%x (+%i)" % (self.file.tell(), (self.file.tell()-start)))
                break

    def decodeHeader(self, data, verbose=True):
        byte_cnt = data[0]
        validAndType = data[1]
        pkt_cnt  = data[2]
        uB       = (data[5] << 32)+ (data[4] << 16)+ data[3]
        formatv  = data[6]
        stuff    = data[7]
        error = False
        #if verbose:
        #    print("byte_cnt: %04x" % byte_cnt)
        #    print("pkt_cnt:  %04x" % pkt_cnt)
        #    print("uB:       %04x %04x %04x" % (data[5], data[4], data[3]))
        #    print("stuff:    %04x %04x" % (formatv, stuff))
        if validAndType != 0x8050:
            error = True
            print("Error: the current package %04x at byte 0x%x is not a header package (0x8050)." % (validAndType, self.file.tell()))
        if not error:
            self.header = self.Header(True, uB, byte_cnt, pkt_cnt, formatv, stuff)
        else:
            self.header = self.Header(False, np.nan, -1, -1)
        if verbose:
            self.header.print()
        return error

    def decodeCRVStatus(self, data, verbose=True):
        pk_type    = data[0]
        word_cnt   = data[1]
        active_feb = (data[2] << 16) + data[3]
        trg_count  = data[4]
        status     = data[5]
        #if verbose:
        #    print("word_cnt:   %04x" % word_cnt)
        #    print("trg_count:  %04x" % trg_count)
        #    print("active_feb: %08x" % active_feb)
        #    print("status: %04x" % status)
        error = False
        if pk_type != 0x0061:
            error = True
            print("Error: the current package %04x at byte 0x%x is not a crv status package (0x0061)." % (pk_type, self.file.tell()))
        if not error:
            self.status = self.Status(True, word_cnt, trg_count, active_feb, status)
        else:
            self.status = self.Status(False, -1, -1, 0x00000000,-1)

        if verbose:
            self.status.print()
        return error

    def getEvent(self):
        nn = self.n+2
        data = struct.unpack("<"+"H"*nn, self.read(2*nn))
        ch = data[0]
        n = data[1] >> 12
        timestamp = data[1] - (n << 12)
        wf = np.array(data[2:], dtype='int8')
        return self.Event(ch, n, timestamp, wf)


    def readEvent(self, process=True, verbose=True):
        dataHeader = self.readPackage(verbose=verbose)
        if not self.decodeHeader(dataHeader, verbose=verbose):
            if self.header.pkt > 0:
               dataStatus = self.readPackage(verbose=verbose)
               if not self.decodeCRVStatus(dataStatus, verbose=verbose):
                   ## check if header and status are consistent
                   if (self.header.byt - 16) >= self.status.wrd*2:
                       # read uB
                       start = self.file.tell()
                       data = struct.unpack("<HH",self.read(2*2)) # two words
                       uB = (data[0] << 16) + data[1]
                       n_payload = self.status.wrd - 10
                       self.payload = self.PayloadHeader(True, uB, n_payload)
                       if verbose:
                            self.payload.print(self.n+2)
                       n_events = n_payload//(self.n+2)
                       if n_payload%(self.n+2) == 0:
                           self.events = []
                           for ev in range(n_events):
                               self.events.append(self.getEvent())
                               if verbose:
                                   self.events[-1].print()
                           # move to the end of a package 
                           frac = (self.file.tell() - start) % (8*2) # a package has 8 words
                           if verbose:
                               print("Move by %i bytes to the end of the current package." % (16-frac))
                           self.file.seek(16-frac,1)
                           if process:
                               self.processEvent()
                       else:
                           print("The number of payload words (%i) can't be devided by the words per event (%i)." % (n_payload, self.n+2))
                   else:
                       print("Byte count from header backage (0x%04x) is smaller than word count in status (0x%04x * 2+16)." % (sel.header.byt, self.status.wrd))

    def processEvent(self):
        self.data_header.append([c.header.uB, c.header.pkt, c.header.byt, c.status.wrd, c.status.trg, c.status.status, c.payload.uB, c.payload.n_words, len(c.events)])
        self.data_event.extend([[c.header.uB, ev.ch, ev.timestmap] + [ev.wf[k] for k in range(self.n)] for ev in c.events])
        
    def data2Dataframe(self):
        self.df_header = pd.DataFrame(self.data_header, columns=["h:uB", "h:pkt", "h:byt", "s:wrd", "s:trg","s:status", "p:uB","p:wrd","p:n"])
        self.df_event  = pd.DataFrame(self.data_event,  columns=["uB", "ch","timestamp"] + ["wf%i" % i for i in range(self.n)])

        '''

        df_header = pd.DataFrame([[c.header.uB, c.header.pkt, c.header.byt, c.status.wrd, c.status.trg, c.status.status, c.payload.uB, c.payload.n_words, len(c.events)]], columns=["h:uB", "h:pkt", "h:byt", "s:wrd", "s:trg","s:status", "p:uB","p:wrd","p:n"])
        df_data = pd.DataFrame([[c.header.uB, ev.ch, ev.timestmap, ev.wf] for ev in c.events], columns=["uB", "ch","timestamp","wf"]) 
        if self.df_header is None:
            self.df_header = df_header
        else:
            self.df_header.append(df_header)

        if self.df_events is None:
            self.df_events = df_data
        else:
            self.df_events.append(df_data)
        '''

    def run(self, verbose=False, nmax=10000000):
        n=0
        while c.file.tell() < c.n_end:
            if n%10==1:
                #print(n)
                print("%07i (%03i)" % (n, len(self.events)), end="\r")
            self.findHeader(verbose=verbose)
            self.readEvent(n>10, verbose=verbose)
            n = n + 1
            if n >= nmax:
                break
        self.data2Dataframe()

    def save(self):
        outname = self.fname[:-3]+"hd5"
        print(outname)
        self.df_header.to_hdf(outname, key="header")
        self.df_event.to_hdf(outname,  key="event")

#c = CRV("20210812_data_n1M_v6.bin") 
#c = CRV("20210811_data_n1M_v5.bin")
#c = CRV("20210811_data_n1M_v4.bin")
#c = CRV("20210908_data_n1M_D20000_v4.bin")
#c = CRV("20210908_data_n1M_D20000_v6.bin")
#c = CRV("20210908_data_n1M_D2000_v7.bin") # crashed
#c = CRV("20210908_dataNewVErsion_nM_D20000_v21.bin")
#c = CRV("20210908_dataNewVErsion_nM_D20000_v22.bin") # something is wrong
#c = CRV("20210908_dataNewVErsion_nM_D20000_v23.bin")
#c = CRV("20210909_data_n1M_D20000_v1.bin")
import sys

#if __name__ == '__main__':
if True:
    if len(sys.argv) <= 1:
        print("USAGE python readCRV.py FILENAME [n-events]")
        sys.exit()
    n_events = 8
    if len(sys.argv) > 2:
        n_events = int(sys.argv[2])

    c = CRV(sys.argv[1])
    c.setNSamples(n_events)
    c.run(nmax=2000010)
    c.save()

