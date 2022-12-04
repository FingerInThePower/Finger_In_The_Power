# Finger in The Power: The Code!
This repository contains code related to the paper The Finger in the Power: How to Fingerprint PCs by Monitoring their Power Consumption. 


## Prerequisites

### Hardware and Software

This fingerprint technique was test only on Intel's and AMD's CPU.
If you want to run it on other types of CPUs please check how to measure the power consumption on your machine.
Under Linux, you can check your power consumption information by running the command:
* Intel - `cat /sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj` or `modprobe msr` + `rdmsr 0x611 -d`
* AMD - `modprobe msr` + `rdmsr 0xc001029b -d`

The implementation currently only works on Linux OS.

All the Python code is designed for Python3!

### Dependencies
To install the dependencies, please run the following command (adapt it with you packet manager)

For native code:
```
sudo apt update
sudo apt install python3-pip
sudo apt-get install python3-venv
python3 -m venv env
./env/bin/pip install -r requirements.txt
```

For portable code:
```
sudo apt update
sudo apt install firefox, python3-pip, cmake, python3.8
pip install -r requirements.txt
git clone https://github.com/WebAssembly/wabt.git
cd wabt
git submodule update --init
mkdir build
cd build
cmake ..
cmake --build .
export PATH=$PATH:$(pwd) //the path of wabt/build
cd ..
cd .. //the path of web_pow_fp
export PATH=$PATH:$(pwd) //Dont forget to set them in path !
python3 ./wasm_generator.py -l 1000
mkdir build
make
```
### How to collect traces

To run the the power consumption collection , you need to check your architecture first.
The architecture should be specified using the three-letter convention.
currently, these are the architectures that are supported with the current version of the code:
`DW CFL CNL CON HSW ICL IVB KBL NHM SKL SKX SNB WOL WSM ZEN+ ZEN2`

Then, run the following line:

Native
```
sudo bash go.sh <CHOSEN ARCHITECTURE> <NUMBER OF TRACES>
```
example: sudo bash go.sh HSW 1000

Portable
```
bash go.sh all \\all stands for the entire webAssembly instruction set available for power measuring. 
```

# Acknowledgement
Some code from this repository, mainly the native component, are based on Gras et al code, available [here](add later)
