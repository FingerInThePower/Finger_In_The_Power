set -e
ulimit -c 0

if [ "$#" -ne 2 ]
then    echo "Usage: sudo bash $0 <arch> <numOfSamples>"
        echo "<arch> should be specified using the three-letter convention, e.g."
        echo "one of BDW CFL CNL CON HSW ICL IVB KBL NHM SKL SKX SNB WOL WSM ZEN+ ZEN2"
        exit 1
fi

arch="$1"
asmfile=s/out-$arch.S
exe=test-$arch
expsize=1000
numOfSamples=$2

if [ ! -s $asmfile ]
  then	echo "Generating assembly file $asmfile"
    ./env/bin/python xmlToAssembler.py $arch >s/out-$arch.S
    echo "Generating assembly file done"
  else	echo "Using existing $asmfile"
  fi

  echo "Compiling with C test program"
  gcc -Ic/ -o$exe c/instrout-test.c s/out-$arch.S -no-pie -pthread
  echo "Compiling with C test program done"
  
for value in $(seq $numOfSamples)
do
  echo "Round $value"
  echo arch: $arch asmfile: $asmfile executable: $exe

  echo "Executing test program in all combinations, number of measurements =  $expsize "
  ./env/bin/python testall.py ./$exe testall $expsize
  echo "Executing test program in all combinations done"

  echo "Executing in plot mode"
  ./env/bin/python testall.py plot
  echo "Executing plot done"

  echo "Saving results"
  ./env/bin/python saveResults.py
  echo "Saving results done"

  echo "Deleting unnecessary results"
  ./env/bin/python deleteResults.py
  echo "Deleting unnecessary results done"
done





