#----------------------------------------------------------------------------
#initialize things
export DTCLIB_DTC=0
export TRACE_FILE=/proc/trace/buffer
export TRACE_FILE=/tmp/trace_buffer_root

source /mu2e/ups/setup

setup pcie_linux_kernel_module v2_03_00 -qe19:s96:prof

source $PCIE_LINUX_KERNEL_MODULE_FQ_DIR/bin/Setup_DTC.sh


#configure JA
source /home/kwar/dtc/JAConfig.sh
sleep 5

source /home/kwar/dtc/loadEventTable2.sh


#set number of null heartbeats
my_cntl write 0x91BC 0x10

#set emulator event mode bits (for non-null heartbeats)
my_cntl write 0x91c0 0xffffffff
my_cntl write 0x91c4 0xffffffff

#set DDR write response timer
my_cntl write 0x9180 0xffffffff

#set control register
my_cntl write 0x9100 0x00808404



### remove?
#enable markers
#my_cntl write 0x91f8 0x00003f3f
#enable tx and rx
#my_cntl write 0x9114 0x00007f7f


# Send data
#enable event marker

#my_cntl write 0x91f0 0x4e20
#enable heartbeats
#my_cntl write 0x91a8 0x4e20
#set num dtcs
#my_cntl write 0x9158 0x1

#set ROC data timeout
# ~52us
#my_cntl write 0x9188 0x00002000
# ~160us
#my_cntl write 0x9188 0x00006000
# ~320us
#my_cntl write 0x9188 0x0000c000
# ~640us
my_cntl write 0x9188 0x00018000

# enable punched clock
my_cntl write 0x9100 0x00808604

#read ja lock bits
#my_cntl read 0x9308

#enable free running null markers
#my_cntl write 0x91bc 0x0

#initialization complete


#-------------------------------------------------------------------------
# ROC response timer for link 0

#read ROC response timer fifo for link 0
#my_cntl read 0x9460
#reset ROC response timer fifo for link 0
#my_cntl write 0x9460 0x0

#---------------------------------------------------------------------------
#Want to see some data?
