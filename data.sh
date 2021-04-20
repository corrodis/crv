#---------------------------------------------------------------------------
#Want to see some data?

# one event
#with punch enable
my_cntl write 0x9100 0x40808604
DTCLIB_SIM_ENABLE=N mu2eUtil --cfoDRP -q 50 -c 1 -n 1 -o 0x1 -D 20000 buffer_test -f sten_test.bin


# 10 events
#with punch enable
my_cntl write 0x9100 0x40808604
DTCLIB_SIM_ENABLE=N mu2eUtil --cfoDRP -q 50 -c 1 -n 10 -o 0x1 -D 20000 buffer_test -f sten_test.bin

#10000 events
#supress output to screen.  send data to file.
rm sten_test10000.bin
my_cntl write 0x9100 0x40808604
DTCLIB_SIM_ENABLE=N mu2eUtil --cfoDRP -Q -c 1 -n 10000 -o 0x1 -D 20000 buffer_test -f sten_test10000.bin
