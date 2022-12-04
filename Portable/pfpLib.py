import pow_fp as pfp
import time
import instructions
import os
from pathlib import Path
import pickle
import sys

CORE_NUMBER = 8
#                              BROWSER  FUNCTIONS                              #
"""
Function to initialize the browser in headless mode.
Run it once before all you experiments.
It will create the browser, and instantiate ALL of the available wasm files.
It can take some time as there are a lot of instantiations (~10 sec for 10000 lines in the wasm file)
Then it returns the browser object. It is your handle to most computations so keep it in a variable.
"""
def initialize_browser():
    print("Initalizing browser and WASM functions...")
    browser = pfp.get_driver("firefox") # Creates the browser.
    browser.execute_script("""return initAllWasm()""") # Instantiates all the wasm files.
    # time.sleep(10) # Handling async is complicated, this should work until 10000 lines.
    print("Done.")
    return browser

"""
Pretty straightforward, close it after your computations.
"""
def close_browser(browser):
    browser.quit()


"""
Function to initialize web workers that will execute the experiments you wish.
It is used to compute on each core to amplify the signal. However, we don't control
on which core it runs.
You need to call it for each instruction you wish to test, and us ethe clean function between two usages.
"""
def initialize_workers(instruction, repetitions, browser, coreNumber = CORE_NUMBER):
    print("Initalizing workers")
    if type(instruction) == list:
        browser.execute_script("""return instantiateWorkers({}, {}, {})""".format(instruction,repetitions, coreNumber))
    else:
        browser.execute_script("""return instantiateWorkers("{}", {}, {})""".format(instruction,repetitions, coreNumber))
    print("Done")

def clean_workers(browser):
    print("Cleaning workers")
    browser.execute_script(""" for (worker of WORKER_ARRAY) {worker.terminate()}; """)
    browser.execute_script(""" SHARED_ARRAY = []; WORKER_ARRAY = [];""")
    print("Done")


#                             RUNNING  EXPERIMENTS                             #
"""
This is the most atomic way I can think of to call a wasm instruction repeatedly
and still be accessible in python.

Using the browser you created before, all the wasm is preloaded.
Call it with the instruction you want (all are in instructions.py)
repetitions is the number of time the wasm files will be called in js.
"""
def run_instruction(instruction, repetitions, browser):
    browser.execute_script("""return testInstructionLoop("{}",{})""".format(instruction, repetitions))



def run_instruction_worker(browser, coreNumber = CORE_NUMBER):
    print("Running experiments on {} cores". format(coreNumber))
    browser.execute_script("""return testInstructionWorkers({})""".format(coreNumber))
    print("Done")
#                               SAMPLE  FUNCTION                               #
"""
Skeleton of a sample function, I imagined it that way
"""
def test_all_instructions(browser,repetitions, measure_type):
    powers = list()
    # browser = initialize_browser() # Very important, you can do it even before if
    #you want to run more instructions
    for instruction in instructions.ALLOP:
        if (type(instruction) == list): # Sometimes we use double instruction
        # and the format is not the same in python and js
            instruction = ",".join(instruction)
        # Power measurement 1 here
        before = read_power()
        try:
            run_instruction(instruction, repetitions, browser)
        except:
            print(f'problem in instruction {instruction}')
            continue
        after = read_power()
        powers.append(after-before)
        # Power measurement 2 here
        # Instruction power_measurement = 2 - 1
        # And tadaaaaaaaa
    save_results(powers, measure_type)


"""
Same but for multicore
"""
def test_all_instructions_multicore(repetitions, coreNumber):
    browser = initialize_browser()
    power_measurement = {}
    for instruction in instructions.ALLOP:
        print("Testing: ", instruction)
        initialize_workers(instruction, repetitions, browser, coreNumber)
        #measure power
        run_instruction_worker(browser)
        #measure power
        # power_measurement[instruction] = p2 - p1
        clean_workers(browser)
    close_browser(browser) # DOnt forget it it wil run foreeeeeeever

def save_results(power_list, measure_type):
    cwd = os.getcwd()
    timestr = time.strftime("%d_%m_%y")
    if not os.path.exists(f'{cwd}/results') or not os.path.exists(f'{cwd}/results/{timestr}'):
        Path(f'results/{timestr}').mkdir(parents=True, exist_ok=True)
    sample_name = time.strftime("%d_%m_%H_%M_%S")
    with open(f"{cwd}/results/{timestr}/HSW{measure_type}_{sample_name}.pkl", "wb") as fp:   #Pickling
        pickle.dump(power_list, fp)
    # textfile = open("a_file.txt", "w")
    # for element in power_list:
    #     textfile.write(str(element) + ",")
    # textfile.close()
    

def read_power():
    with open('/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj') as ef:
        prev_call = int(ef.read())
    return prev_call

def measure_power_one_instruction(instruction_name, measurements, measure_type):
    powers = list()
    for i in range(measurements):
        before = read_power()
        run_instruction(instruction_name, 100, browser)
        after = read_power()
        powers.append(after-before)
    save_results(powers, measure_type)


if __name__ == '__main__':
    try:
        browser = initialize_browser()
        num_measurements = int(sys.argv[1]) #should be 100
        measure_type = (sys.argv[2])
        if measure_type == 'one':
            instruction = "i32.ctz"
            measure_power_one_instruction(instruction, num_measurements, measure_type)
        elif measure_type == 'all':
            test_all_instructions(browser,num_measurements, measure_type)
        else:
            print(' please choose -one- or -all- instructions')
        close_browser(browser)
    except:
        close_browser(browser)



    # pickle_file = open("/home/user/CPUFingerprint/power_fingerprint/web_pow_fp/results/27_03_22/HSWall_27_03_16_39_11.pkl", "rb")
    # objects = []
    # while True:
    #     try:
    #         objects.append(pickle.load(pickle_file))
    #     except EOFError:
    #         break
    # pickle_file.close()

    # print(objects)
    # print(len(objects.pop()))
    # run_instruction(instruction, 100, browser)

    # initialize_workers("i64x2.add", 100000, browser)
    # run_instruction_worker(browser)
    # clean_workers(browser)
    # initialize_workers(['i32.trunc_f64_s', 'f64.convert_i32_u'], 100000, browser)
    # run_instruction_worker(browser)
    # clean_workers(browser)
    # test_all_instructions_multicore(10, 8)
