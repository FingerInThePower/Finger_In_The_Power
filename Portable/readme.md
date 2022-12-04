# Power consumption WebAssembly


## Description

API to run WebAssembly instructions in headless mode.
It's based on Selenium to handle the browser without the GUI.
The python scripts run the browser and the experiments.

It offers handles to Selenium to run tests on WASM instructions


## Run it
It should work directly in the command line interface, but you need to build all the wasm files before.

### Installing dependencies:

```
sudo apt update
sudo apt install firefox, python3-pip, cmake, python3.8
pip install -r requirements.txt
```

You will also need to build wabt from sources, as the apt version is not recent enough.

```
git clone https://github.com/WebAssembly/wabt.git
cd wabt
git submodule update --init
mkdir build
cd build
cmake ..
cmake --build .
```

Then you need to add the file to the $PATH for the makefile to run with the following commmand in the folder where the build bin is with:  `export PATH=$PATH:$(pwd)`

You also need to download your version of geckodriver available here: https://github.com/mozilla/geckodriver/releases and set it up in the path with `export PATH=$PATH:/path/to/geckodriver`

### Wasm Files
Wasm is a compiled language, so we need to build the files beforehand.

```
python3 ./wasm_generator.py -l 1000
mkdir build
make
```

### Run the tests

First you need to launch the server:
```
python3 ./server.py
```

The handles currently involves:

| Function | Description |
|:--:|:--|
| initalize_browser() | Create the headless browser (Firefox) and instantiates all the WASM functions. You can run it only once before running all your experiments. We initalize everything to diminish the overhead in the measurement.|
|close_browser(browser) | Closes an instance of browser. Run it after the experiment. |
| run_instruction(instruction, repetitions, browser) | Run a JavaScript code in the browser that repeats the instruction given in parameter a certain number of repetitions. Single core. |
|initialize_workers( instruction, repetitions, browser, coreNumber) | Creates coreNumber webworkers (subthread) and pass them the instruction to test. They will not run the test yet, they are just created. This lets the test be more atomic. |
| clean_workers(browser) | Delete all said workers |
|run_instrution_worker(browser, coreNumber) | Use the previously created workers to call an instruction in a loop. The parameters are passed during intitialization. This is the function to be measured.|

The typical workflow for a single corewould be:

```
browser = initialize_browser
instruction = "i32.ctz"
repetitions = 1000
measure_power_consumption() # This is not implemented here
run_instruction(instruction, 1000)
measure_power_consumption() # This is not implemented here
close_browser(browser)
```

This will start the browser, instantiates all the wasm, and measure the power consumption of running a 1000 "i32.ctz" wasm script.

For a multicore:
```
browser = initialize_browser()
initialize_workers("i64x2.add", 100000, browser)
measure_power_consumption() # This is not implemented here
run_instruction_worker(browser)
measure_power_consumption() # This is not implemented here
clean_workers(browser)
close_browser(browser)
```

Keep in mind that a call to the wasm file is not a single call to the instruction, but it depends on what you used with wasm_generator.py.
You have two factors to the total number of instructions, one in the python, and one depends on the number of lines in the wasm file created by the generator.
That is because generating and building very large files in wasm can take some time.
