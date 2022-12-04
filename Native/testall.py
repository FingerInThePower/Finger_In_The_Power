import json
import subprocess
import pickle
import glob
import os
import csv
import random
import sys
import ujson
import cpus
import numpy
from io import StringIO
from scipy import stats
import xml.etree.ElementTree as ET
import psutil
from pathlib import Path
import time
import hwcounter
import socket

if __name__ != "__main__":
    raise Exception('not intended for import but for execution')


def getconfig(exe):
    """
    We invoke the test executable to get some configuration from it so we
    don't have to hard-code it between python and C.
    The executable returns it in a python dict which we eval() to get it.
    'writerfailstring' is the string the executable will produce when its
    sibling test program has crashed. 'available' is a list of numbers
    corresponding to available instructions (workloads).

    we need a high recursion limit to eval() the output.
    """
    process_output = subprocess.check_output(["./" + exe, "available"])
    process_output = process_output.decode('ascii')
    try:
        lim = sys.getrecursionlimit()
        if lim < 35000:
            sys.setrecursionlimit(35000)
        print('doing eval with recursion limit %d' % sys.getrecursionlimit())
        configdict = eval(process_output)
    except RecursionError:
        print('parsing of binary output failed with recursionerror.')
        sys.exit(1)
    return configdict['writerfailstring'], configdict['available']


def get_work_cpus():
    """
        Work cpus are the processors (logical processors) that are used to execute the
        cross-thread measurement worklads. We allow all the LP's in the system to do
        this, except for the LP's for one physical core. These are the 'master cpus,'
        reserved for the parent process, the python interpreter. We use the affinity
        module to pin the python interpreter to these LP's. We return the rest of the
        LP's.
        """
    cpulist = cpus.corelist(True)
    master_cpus = cpulist.pop()
    p = psutil.Process()
    p.cpu_affinity(master_cpus)
    print('master cpus (for python):', master_cpus, file=sys.stderr)
    print('worker cpus:', cpulist, file=sys.stderr)
    return cpulist


def usage():
    print('Usage:  %s <generated-binary> testall <number-of-instrs>' % sys.argv[0])
    print('        %s plot' % sys.argv[0])
    sys.exit(1)


def read_power():
    with open('/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:0/energy_uj') as ef:
        prev_call = int(ef.read())
    return prev_call

def read_temperature():
    tempFile = open( "/sys/class/thermal/thermal_zone2/temp" )
    cpu_temp = tempFile.read()
    tempFile.close()
    return cpu_temp

def activate_core(killall, exe, trial_cpu1, write, num_measurements, warmup_number):
    # Kill any lingering processes that didn't exit for some reason
    # This shouldn't happen but if it does would totally mess up the experiments.
    subprocess.call(['sudo', killall, '-9', os.path.basename(exe)], stdout=devnull, stderr=devnull)
    invoke_args = ['sudo', "./" + exe, str(trial_cpu1), str(trial_cpu1), str(write), str(num_measurements),
                    str(warmup_number)] + [str(write)]
    p = subprocess.Popen(invoke_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = None
    err = None
    try:
        time_before = hwcounter.count()
        power_before = read_power()
        out, err = p.communicate(timeout=4)
        power_after = read_power()
        time_after = hwcounter.count_end() - time_before
        temperature = read_temperature()
    except subprocess.TimeoutExpired:
        print('timeout')
        subprocess.call(['sudo', killall, '-9', os.path.basename(exe)], stdout=devnull, stderr=devnull)
        out, err = p.communicate()
    out = out.decode('ascii')
    err = err.decode('ascii')
    f = StringIO(out)
    if p.returncode != 0:
        print('WARNING: exitcode:', p.returncode)
        print('err out:', err)
        out = "ERROR!!!"
    return f, out, power_after-power_before, time_after, temperature

def acquire(exe, num_measurements, trial_cpu1):
    state_json_fn = 'state-' + os.path.basename(exe) + '.json'
    if os.path.exists(state_json_fn):
        state = ujson.load(open(state_json_fn))
        unreliable_set = set(state['unreliable_set'])
    else:
        state = dict()
        unreliable_set = set()

    writerfailstring, baseline_list = getconfig(exe)


    ### The initial definition of baseline_list - random first 500 instructions (I don't know why they chose the instructions this way)t)
    ## List of numbers of the instructions that are running only on ports 0, 1, 5, 0+1 (474 instructions)
    baseline_list = list(set([13444, 13704, 13323, 13325, 13327, 13329, 918, 13438, 675, 677, 679, 553, 301, 693, 695, 697, 60, 62, 64, 66, 68, 715, 333, 334, 717, 11215, 11217, 13521, 11219, 11221, 11223, 344, 474, 476, 732, 734, 736, 738, 13424, 13302, 13693, 510, 13695,
                         13828, 518, 520, 522, 524, 1038, 1040, 1042, 1044, 13332, 1046, 1048, 1050, 1052, 13345, 13347, 554, 556, 558, 560, 562, 564, 566, 568, 570, 572, 574, 576, 595, 597, 599, 601, 603, 613, 13422, 629, 13443, 657, 659, 661, 663, 665, 13465, 667, 13467, 669, 13469, 671, 699, 701, 703, 705, 13510, 223, 13535, 13537, 13539, 13541, 744, 13545, 746, 748, 750, 752, 754, 243, 756, 245, 758, 13561, 770, 771, 772, 774, 776, 779, 787, 13587, 789, 13589, 791, 13591, 793, 13593, 13595, 13597, 13599, 13601, 13605, 299, 811, 303, 305, 13617, 13619, 827, 829, 831, 833, 322, 835, 837, 327, 839, 841, 13639, 843, 13641, 13643, 343, 857, 861, 863, 865, 354, 867, 356, 869, 358, 13670, 360, 13673, 13675, 13679, 13691, 382, 13186, 13706, 13708, 13710, 919, 921, 410, 923, 412, 925, 414, 927, 416, 929, 13728, 931, 13730, 933, 13732, 935, 13734, 937, 13736, 939, 13738, 941, 13740, 13742, 13744, 434, 13746, 13748, 13750, 446, 447, 960, 962, 964, 966, 968, 978, 470, 478, 480, 13792, 482, 484, 486, 488, 490, 492, 494, 1006, 13296, 13299,
                         11776, 11777, 11784, 11785, 11786, 11793, 11666, 11667, 11689, 11690, 11691, 12594, 12595, 12596, 12606, 13758, 12608, 13759, 12610, 12995, 12612, 12996, 12997, 13760, 13654, 13655, 13656, 13660, 13661, 13662, 11901, 11902, 11383, 11384, 11385, 11389, 11390, 11391,
                         13824, 1028, 1030, 1032, 13832, 1034, 13836, 526, 528, 13840, 530, 532, 534, 536, 538, 540, 542, 544, 546, 548, 550, 552, 579, 581, 583, 73, 585, 75, 587, 589, 591, 81, 83, 85, 87, 605, 607, 609, 612, 616, 619, 622, 625, 628, 632, 635, 129, 131, 643, 645, 647, 137, 649, 139, 13479, 13481, 13483, 13485, 689, 691, 13493, 13495, 13497, 13499, 13501, 13503, 13505, 13507, 13512, 13514, 13516, 13518, 720, 13520, 722, 13523, 13525, 13527, 728, 730, 13531, 13542, 13546, 13549, 13552, 13555, 13558, 13562, 13565, 259, 261, 13577, 267, 13579, 269, 781, 271, 783, 273, 785, 13581, 13583, 279, 281, 801, 803, 805, 807, 817, 819, 845, 847, 849, 851, 853, 855, 859, 13681, 883, 885, 895, 897, 386, 899, 901, 903, 392, 905, 394, 907, 909, 911, 13712, 913, 13714, 915, 404, 917, 406, 13716, 408, 13718, 13720, 13722, 13724, 13820, 13726, 424, 426, 428, 430, 944, 946, 948, 950, 440, 952, 442, 954, 956, 13752, 13754, 450, 452, 454, 456, 970, 972, 974, 977, 466, 468, 981, 13780, 983, 472, 985, 13784, 987, 13788, 989, 992, 995, 997, 999, 1002, 1005, 1009, 1011, 1013, 1015, 1017, 1020]))


    ## only vectorial instruction list = a total of 294 instructions

    # baseline_list = list(set([1028 ,1030 ,1032 ,1034 ,1038 ,1040 ,1042 ,1044 ,1046 ,1048 ,1050 ,1052 ,73 ,75 ,81 ,83 ,85 ,87 ,129 ,131 ,137 ,139 ,223 ,243 ,245 ,259 ,261 ,267 ,269 ,271 ,273 ,279 ,281 ,299 ,301 ,303 ,305 ,322 ,327 ,333 ,334 ,343 ,344 ,354 ,356 ,358 ,360 ,382 ,386 ,392 ,394 ,404 ,406 ,408 ,410 ,412 ,414 ,416 ,424 ,426 ,428 ,430 ,434 ,440 ,442 ,446 ,447 ,450 ,452 ,454 ,456 ,466 ,468 ,470 ,472 ,474 ,476 ,478 ,480 ,482 ,484 ,486 ,488 ,490 ,492 ,494 ,510 ,518 ,520 ,522 ,524 ,526 ,528 ,530 ,532 ,534 ,536 ,538 ,540 ,542 ,544 ,546 ,548 ,550 ,552 ,553 ,554 ,556 ,558 ,560 ,562 ,564 ,566 ,568 ,570 ,572 ,574 ,576 ,579 ,581 ,583 ,585 ,587 ,589 ,591 ,595 ,597 ,599 ,601 ,603 ,605 ,607 ,609 ,612 ,613 ,616 ,619 ,622 ,625 ,628 ,629 ,632 ,635 ,643 ,645 ,647 ,649 ,657 ,659 ,661 ,663 ,665 ,667 ,669 ,671 ,675 ,677 ,679 ,689 ,691 ,693 ,695 ,697 ,699 ,701 ,703 ,705 ,715 ,717 ,720 ,722 ,728 ,730 ,732 ,734 ,736 ,738 ,744 ,746 ,748 ,750 ,752 ,754 ,756 ,758 ,770 ,771 ,772 ,774 ,776 ,779 ,781 ,783 ,785 ,787 ,789 ,791 ,793 ,801 ,803 ,805 ,807 ,811 ,
    # 817 ,819 ,827 ,829 ,831 ,833 ,835 ,837 ,839 ,841 ,843 ,845 ,847 ,849 ,851 ,853 ,855 ,857 ,859 ,861 ,863 ,865 ,867 ,869 ,883 ,885 ,895 ,897 ,899 ,901 ,903 ,905 ,907 ,909 ,911 ,913 ,915 ,917 ,918 ,919 ,921 ,923 ,925 ,927 ,929 ,931 ,933 ,935 ,937 ,939 ,941 ,944 ,946 ,948 ,950 ,952 ,954 ,956 ,960 ,962 ,964 ,966 ,968 ,970 ,972 ,974 ,11215 ,11217 ,977 ,11219 ,978 ,11221 ,981 ,983 ,11223 ,985 ,987 ,989 ,992 ,995 ,997 ,999 ,1002 ,1005 ,1006 ,1009 ,1011 ,1013 ,1015 ,1017 ,1020]))
    
    
    baseline_list = sorted(baseline_list)
    warmup_number = 500
    reliable_list = list(set(baseline_list) - unreliable_set)
    assert 0 not in reliable_list
    writerlist = [0] + reliable_list
    for write in writerlist:
        if write == 0:
            continue
        if not os.path.exists(f'ccgrid/cores_{trial_cpu1}/'):
            Path(f'ccgrid/cores_{trial_cpu1}/').mkdir(parents=True, exist_ok=True)
        fn_summary = f'ccgrid/cores_{trial_cpu1}/write{write}-{os.path.basename(exe)}-summary.pickle'
        data_updated = False
        alldata_summary = dict()
        if os.path.exists(fn_summary):
            with open(fn_summary, 'rb') as fp_summary:
                try:
                    alldata_summary = pickle.load(fp_summary)
                except:
                    alldata_summary = dict()
            print('loaded summary for writer %d: %s' % (write, fn_summary))
            continue
        acquire_set = set(baseline_list) - unreliable_set
        have_set_summary = set(alldata_summary)
        if acquire_set <= have_set_summary:
            print(write, ': all entries already there in summary')
            continue
        writerfail = False
        retries = 0
        alldata = dict()
        with open(state_json_fn, 'w') as fp:
            state['unreliable_set'] = list(unreliable_set)
            state['baseline_list'] = baseline_list
            ujson.dump(state, fp)
        retries += 1
        have_set = set([int(x) for x in alldata])
        acquire_list = list(set(baseline_list) - unreliable_set - have_set)
        random.shuffle(acquire_list)
        f, out ,power, time, temperature = activate_core(killall, exe, trial_cpu1, write, num_measurements, warmup_number)
        if(out == "ERROR!!!"):
            print(f'error in instruction: {write}')
            continue
        alldata_summary = [power, time, temperature]
        with open(fn_summary, 'wb') as fp:
            pickle.dump(alldata_summary, fp)
        print('writing done for instruction: ', write)


parsed_root = None

def plot():
    directory = 'ccgrid'
    for core_folder in os.listdir(directory):
        if not os.path.isdir(f'{directory}/{core_folder}'):
            continue
        states = dict()
        baseline_list = dict()
        alldata_by_writers = dict()
        for statefile in sorted(glob.glob('*state-test-*json')):
            base_state = os.path.basename(statefile)
            dashes = base_state.split('-')
            last = dashes[-1]
            dots = last.split('.')
            assert dots[1] == 'json'
            arch = dots[0]
            assert len(arch) == 3 or len(arch) == 4
            states[arch] = ujson.load(open(statefile))
            baseline_list[arch] = states[arch]['baseline_list']
            print('baseline list len', arch, 'is', len(baseline_list[arch]))
            assert baseline_list[arch] == sorted(baseline_list[arch])
            assert 0 not in baseline_list[arch]
            assert len(set(baseline_list[arch])) == len(baseline_list[arch])
            n = 0
            all_writers = set()
            all_files = glob.glob(f'ccgrid/{core_folder}/*{arch}*summary*.pickle')
            print('arch:', arch, 'summaries:', len(all_files), file=sys.stderr)
            if len(all_files) < 1:
                print('no data found', file=sys.stderr)
                raise Exception('no data files found in ccgrid/ for arch %s' % arch)
            for fn in sorted(all_files):
                n += 1
                base = os.path.basename(fn)
                writerinfo = base.split('-')[0]
                writerinfo = writerinfo.replace('write', '')
                writeno = int(writerinfo)
                all_writers.add(writeno)
                if writeno != 0:
                    assert writeno in baseline_list[arch]
                else:
                    assert writeno not in baseline_list[arch]
                assert writeno not in alldata_by_writers
                with open(fn, 'rb') as fp:
                    data = pickle.load(fp)
                    power = data[0]
                    time_consumed = data[1]
                    temperature = int(data[2][:-1])
                    alldata_by_writers[int(writeno)]= [power,temperature,time_consumed] 
            print('saving')
            timestr = time.strftime("%d_%m_%H_%M_%S")
            hostname = socket.gethostname()
            numpy.save('(%s)(%s)_%s_Native.npy' % (hostname,arch,timestr,), alldata_by_writers)
            print('saving done') 
        
    
if __name__ == "__main__":
    global killall, measurements, warmup, devnull
    killall = '/usr/bin/killall'
    measurements = 5
    warmup = 5
    devnull = open('/dev/null', 'w')
    if not os.path.exists(killall):
        raise Exception('need killall binary')

    if len(sys.argv) < 2:
        usage()
    if len(sys.argv) >= 4 and sys.argv[2] == 'testall':
        work_cpus = get_work_cpus()
        trial_cpu1 = work_cpus.pop().pop()
        exe = sys.argv[1]
        num_measurements = int(sys.argv[3])
        acquire(exe, num_measurements, trial_cpu1)


    if sys.argv[1] == 'plot':
        plot()
