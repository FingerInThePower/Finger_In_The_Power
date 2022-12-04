# Run it if you want to save your results

import glob
import os
from pathlib import Path
import platform
import time
import socket

# def just_toSee():
#     import numpy as np
#     cwd = os.getcwd()
#     data = np.load('results/asm_info/KBL_ops_asm_name_matrix.npy', allow_pickle=True)
#     print('yay')


def save_results(list_to_save):
    hostname = socket.gethostname()
    cwd = os.getcwd()
    timestr = time.strftime("%d_%m_%y")
    if not os.path.exists(f'{cwd}/results_({hostname})'):
        Path(f'results/maps').mkdir(parents=True, exist_ok=True)
    # if not os.path.exists(f'{cwd}/results/maps/{timestr}'):
    #     Path(f'results/maps/{timestr}').mkdir(parents=True, exist_ok=True)
    # if not os.path.exists(f'{cwd}/results/asm_info'):
    #     Path(f'results/asm_info').mkdir(parents=True, exist_ok=True)

    new_list = []

    for item in list_to_save:
        if isinstance(item, list) and len(item)!= 0:
            for pop in item:
               new_list.append(pop)


    for item in new_list:
        pop = item
        curr_path = cwd + '/' + pop
        # if 'png' in pop:
        #     path_to_save = 'results/pngs/' + pop
        # if 'asm' in pop:
        #     path_to_save = 'results/asm_info/' + pop
        #     if Path(path_to_save).exists():
        #         continue
        # else:
        import re
        split = re.split('_|\(|\)',pop)
        # cores = f'cores_{split[2]}_{split[3]}'
        if not os.path.exists(f'{cwd}/results_({hostname})/{timestr}'):
            Path(f'{cwd}/results_({hostname})/{timestr}').mkdir(parents=True, exist_ok=True)
        path_to_save = f'{cwd}/results_({hostname})/{timestr}/' + pop
        os.replace(curr_path, path_to_save)

if __name__ == '__main__':
    # just_toSee()
    results_list = list()
    # results_list.append(glob.glob('covert-nuke.png'))
    results_list.append(glob.glob('*(*[A-Z+])_*[0-9]_*[0-9]_*[0-9]_*[0-9]_*.npy'))
    results_list.append(glob.glob('*[A-Z+]_num_to_asm_dict.npy'))
    results_list.append(glob.glob('*[A-Z+]_ops_asm_name_matrix.npy'))
    save_results(results_list)