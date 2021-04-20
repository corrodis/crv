# Reset Timers
./readTiming.sh 0

n=$1
fname=$2


DTCLIB_SIM_ENABLE=N mu2eUtil --cfoDRP -q 1 -c 1 -n $n -o 0x1 -D 20000 buffer_test -f ${fname}.bin

echo "Store Timing Info"
./readTiming.sh $n >> ${fname}.dat
