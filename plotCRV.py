import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

#fname = "data/20210812_data_n1M_v6.hd5"
#fname = "data/20210811_data_n1M_v5.hd5"
#fname = "data/20210811_data_n1M_v4.hd5"
fname = "data/20210908_data_n1M_D20000_v4.hd5"
fname = "data/20210908_data_n1M_D20000_v6.hd5"
fname = "data/20210908_dataNewVErsion_nM_D20000_v21.hd5"
fname = "data/20210908_dataNewVErsion_nM_D20000_v23.hd5"

import sys
if len(sys.argv) > 1:
    fname = sys.argv[1]

dfh = pd.read_hdf(fname, key="header") 
dfe = pd.read_hdf(fname, key="event") 

# Missing uB?
if (np.diff(dfh['h:uB'].values).min()==1)&(np.diff(dfh['h:uB'].values).max()==1):
    print("header uB: ok")
else:
    print("header uB: missing")
trgdiff = np.diff(dfh['s:trg'].values) 
if (trgdiff[trgdiff != -65535].min()==1)&(trgdiff[trgdiff != -65535].max()==1):
    print("status trg: ok")
else:
    print("status trg: missing")
if (np.diff(dfh['p:uB'].values).min()==1)&(np.diff(dfh['p:uB'].values).max()==1):
    print("payload uB: ok")
else:
    print("payload uB: missing")


 

# number of events
plt.figure(figsize=[6.4*1.5, 4.8])
ax1 = plt.subplot(121)
#plt.plot(dfh['h:uB'].values-dfh['h:uB'].values.min(), dfh['p:n'].values,'.')
plt.plot(dfh['h:uB'].values, dfh['p:n'].values,'.')
plt.xlabel("uB [#]")
plt.ylabel("no of events")
ax2 = plt.subplot(122, sharey=ax1)
plt.hist(dfh['p:n'].values, bins=np.arange(-0.5,52.5), orientation='horizontal')
plt.xlabel("count")
plt.tight_layout()
plt.show()

'''
# channels
ch_min = dfe['ch'].min()
ch_max = dfe['ch'].max()
plt.hist(dfe['ch'].values, bins=np.arange(ch_min-0.5, ch_max+1.5))
plt.xlabel("channel")
plt.ylabel("count")
plt.tight_layout()
plt.show()

f = plt.figure(figsize=[6.4, 4.8*1.5])
ax1 = plt.subplot(411)
for ch in range(ch_min, ch_min+8):
    if ch%2 == 0:
        print(411+(ch-ch_min)//2)
        if ch > ch_min:
            plt.legend()
            plt.subplot(411+(ch-ch_min)//2, sharex=ax1)
    plt.hist(dfe[dfe['ch']==ch][['uB','timestamp']].groupby(['uB']).count()['timestamp'].values, bins=np.arange(-0.5, 12.5), histtype='step', label="ch %i" % ch, linewidth=2)
plt.legend()
plt.ylabel("count")
plt.xlabel("no of events")
plt.tight_layout()
plt.subplots_adjust(hspace=0.0)
plt.show()

df = dfe.join(dfh.set_index('h:uB'), on='uB')
# timestamp
for ch in range(64, 64+8):
    plt.hist(df[(df['ch']==ch)&(df['p:n']<50)]['timestamp'].values, bins=np.arange(0,260))
    plt.xlabel("timestamp")
    plt.ylabel("count")
    plt.title("channel %i" % ch)
    plt.tight_layout()
    plt.show()

'''
# waveforms
n_samples = 8
ch=64
dd = dfe[dfe['ch']==ch][["wf%i" % k for k in range(n_samples)]].values
plt.plot(dd[:100,:].T)
plt.xlabel("sample")
plt.ylabel("amplitude [adc]")
plt.title("channel %i" % ch)
plt.tight_layout()
plt.show()


# dd = dfe[dfe['ch']==ch][["wf%i" % k for k in range(10)]].values
plt.hist2d(np.tile(np.arange(n_samples), dd.shape[0]), dd[:,:].reshape([-1]), bins=(n_samples, (dd.max()-dd.min())//2), cmap=plt.cm.jet)
plt.xlabel("sample")
plt.ylabel("amplitude [adc]")
plt.title("channel %i" % ch)
plt.colorbar()
plt.tight_layout()
plt.show()
'''

# cross-talk
ch = 64
x = []
y = []
for n, uB in enumerate(dfh['h:uB']):
    print(uB)
    for ts1 in dfe[(dfe['uB']==uB)&(dfe['ch']==ch)]['timestamp']:
        for ts2 in dfe[(dfe['uB']==uB)&(dfe['ch']==ch+1)]['timestamp']:
            #plt.plot([ts1],[ts2],'.')
            x.append(ts1)
            y.append(ts2)
    if n > 1000:
         break

plt.hist2d(x, y, bins=(100,100), cmap=plt.cm.jet, vmax=7.) 
plt.xlabel("timestamp channel %i" % ch)
plt.xlabel("timestamp channel %i" % (ch+1))
plt.tight_layout()
plt.show()
'''

