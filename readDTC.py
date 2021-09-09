import numpy as np
import struct
import sys

def load(fname):
    with open(fname, mode='rb') as file:
        fileContent = file.read() 

def get(n):
    return  "%04x" % struct.unpack("<H", fileContent[n*2:(n+1)*2])

def read(start, v=0, test=True, uBOut=False, uBExp=None, ):
    n = int(get(start), 16)
    uB_hex = get(start+4)+get(start+3)+get(start+2)
    
    header_start = start+11
    header_n_ =  int(get(header_start), 16)
    header_type_ = get(header_start+1) 
    header_package_cnt_ = int(get(header_start+2), 16) 
    header_uB_hex_ = get(header_start+5)+get(header_start+4)+get(header_start+3)

    header_start = start+28 
    header_n =  int(get(header_start), 16)
    header_type = get(header_start+1) 
    header_package_cnt = int(get(header_start+2), 16)
    header_uB_hex = get(header_start+5)+get(header_start+4)+get(header_start+3) 

    dead = False
    if header_type_ == '0030':
        if header_type == '0050':
            dead = True


    if v in [1, 3]:
        print("==========================================================================")
        print("DMA: \t\tn: %i, \tuB: %s'%s'%s" % (n, uB_hex[:4], uB_hex[4:8], uB_hex[8:]))
        print("Hdr(%s): \tn: %i (%i), \tuB: %s'%s'%s"% (header_type_, header_n_, header_package_cnt_, header_uB_hex_[:4], header_uB_hex_[4:8], header_uB_hex_[8:]))
        if not dead:
            print("Hdr(%s): \tn: %i (%i), \tuB: %s'%s'%s"% (header_type, header_n, header_package_cnt, header_uB_hex[:4], header_uB_hex[4:8], header_uB_hex[8:]))
        else:
            print("Hdr(%s): \tn: %i (%i), \t TIMEOUT"% (header_type, header_n, header_package_cnt)) 

    crv = False
    #if (header_type_ == '0050')&(header_type == '8050')&(not dead):
    if (header_type == '8050')&(not dead):
      crv = True
      crv_start = start+36
      crv_type = get(crv_start)
      crv_n  = int(get(crv_start+1),16)
      crv_active = get(crv_start+2) + get(crv_start+3)
      crv_dreq   = get(crv_start + 4)
      crv_cnt = get(crv_start + 5)
      crv_type_ = get(crv_start + 7)[:2]
      crv_error = get(crv_start + 7)[2:]

      if v in [1, 3]:
        #print("==========================================================================")
        #print("DMA: \t\tn: %i, \tuB: %s'%s'%s" % (n, uB_hex[:4], uB_hex[4:8], uB_hex[8:]))
        #print("Hdr(%s): \tn: %i (%i), \tuB: %s'%s'%s"% (header_type_, header_n_, header_package_cnt_, header_uB_hex_[:4], header_uB_hex_[4:8], header_uB_hex_[8:]))
        #print("Hdr(%s): \tn: %i (%i), \tuB: %s'%s'%s"% (header_type, header_n, header_package_cnt, header_uB_hex[:4], header_uB_hex[4:8], header_uB_hex[8:]))
        print("CRV(%s) \tn:%i (%s), \t\t\tdreq:%s\tact:%s, err:%s" % (crv_type, crv_n, crv_cnt, crv_dreq, crv_active,crv_error))
    if test:
        p1 = get(start+5)+get(start+6)+get(start+7)
        if p1 != "ff01ffffffff":
             print("ERROR (start %i): header issue mis-match? (%s, expect ff01ffffffff)" % (start, p1))
        if header_type_ == '0050':
            if header_type != '8050':
                print("ERROR (start %i): header type mis-match? (%s, %s)" % (start, header_type_, header_type))
        #if (uB_hex != header_uB_hex_)|(uB_hex != header_uB_hex):
        elif(int(header_type_, 16) != n - 0x18):
            print("WARNING (start %i): event count 0x%s != 0x%s - 0x18" % (start, header_type_, hex(n)))
        if dead:
            print("ERROR (start %i): timeout (%s)" % (start, uB_hex))
        if (header_uB_hex_ != header_uB_hex)&(not dead):
            print("ERROR (start %i): header uB missmatch (%s, %s, %s)" % (start, uB_hex, header_uB_hex_, header_uB_hex))
        if crv: # has CRV Status
            if crv_type != '0061':
                print("ERROR (start %i): CRV Status Type Package Error (%s != 0061)" % (start, crv_type)) 
            if crv_error != '00':
                print("ERROR (start %i): CRV Status Error (%s)" % (start, crv_error))
        if header_type_ == '0030':
            if header_type == '0050': # timeout?
                print()
        if uBExp:
          if uBExp != int(header_uB_hex_,16):
              print("ERROR (start %i): error in expected uB (%s !=  %s)" % (start, header_uB_hex_, hex(uBExp)))
          #if uBExp != int(uB_hex,16):
          #  print("ERROR (start %i): error in expected uB (%s !=  %s)" % (start, uB_hex, hex(uBExp)))
    
    if v in [2, 3]:
        for k in range(n//2): 
           print(get(start+k), end=" ") 
           if k%12 == 11: 
               print(" ") 

    if uBOut:
        return start+n//2, header_uB_hex_
    return start+n//2


def raw(start, size=0x68, nstart=-3, nend=4):
    nn = size//2
    for ev in range(nstart,nend+1): 
        for k in range(nn):
            print(get(start+nn*ev+k), end=" ")
            if k%12 == 11:
                print(" ")
        print(" ")
        print(" ")
