if [ "$1" -le "0" ]; then
   my_cntl write 0x9460 0x0
   echo "Reset Counter"
else
  for k in `seq $1`; do
    my_cntl read 0x9460;
    #my_cntl read 0x9460 >> timing.dat;
  done
fi
