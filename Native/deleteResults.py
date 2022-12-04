# Run it if you want a clear start and all the results will be deleted

import glob
import pathlib
import os
import shutil


def delete_results(list_to_delete):
    for item in list_to_delete:
        if len(item) != 0:
            if item[0] != 'ccgrid':
                path = './' + str(item.pop())
                pathlib.Path(path).unlink()
            else:
                path = './' + str(item.pop())
                grid_files = os.listdir(path)
                for file in grid_files:
                    if file != 'README':
                        shutil.rmtree(path + '/' +file)


if __name__ == '__main__':
    results_list = list()
    results_list.append(glob.glob('state-test-*[A-Z+].json'))
    results_list.append(glob.glob('ccgrid'))
    delete_results(results_list)
