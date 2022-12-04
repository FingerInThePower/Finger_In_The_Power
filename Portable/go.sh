#!/bin/bash
set -e
ulimit -c 0

expsize=100
numofinstr=$1

export PATH=$PATH:$(pwd)
export PATH=$PATH:/home/user/CPUFingerprint/power_fingerprint/web_pow_fp

echo "Changing permissions of rapl"
echo "p@\$w0r\$d" | sudo -S chmod 777 /sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj

echo "Turning server on"
python3.8 server.py &
PID=$!

for value in {1..1000}
do
  echo "Round $value"
  
  echo "Executing power measurement with one instruction and save result"
  python3 pfpLib.py $expsize $numofinstr
  echo "Executing power measurement done"
done

kill -9 $PID

echo "Changing permissions of rapl back"
echo "p@\$w0r\$d" | sudo -S chmod og-rwx /sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj




