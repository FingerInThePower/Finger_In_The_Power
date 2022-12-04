#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import JavascriptException, WebDriverException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

import plotly.graph_objects as go
import subprocess
import os
import time
import math
import json
import statistics
import sys
import numpy as np
import instructions
import re
import cpuinfo
import argparse

URL = "http://localhost:8000/"


def get_driver(browser_s):
    ''' Create a driver instance and returns it.
    We use it to waste less time starting and closing the browser.

    Parameters:
    browser_s(string): The name of the browser. Either firefox or chrome

    Returns:
    selenium.webdriver: A handle to the browser
    '''
    if (browser_s == 'firefox'):
        options = FirefoxOptions()
        options.add_argument("-devtools") # Opening the console somehow makes things better
        options.add_argument("-headless") # Opening the console somehow makes things better

        driver = webdriver.Firefox(options=options)
    elif (browser == 'chrome'):
        options = ChromeOptions()
        options.add_argument("auto-open-devtools-for-tabs") # Opening the console somehow makes things better
        driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.set_script_timeout(10000000000) # Sometimes the computations are too long so we set a high timeout ot be sure
    driver.get(URL)
    return driver

#
# def read_power():
#     cat_pow = 'sudo cat /sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:1/energy_uj'
#     process = subprocess.Popen(cat_pow, stdout=subprocess.PIPE, shell=True)
#     for line in iter(process.stdout.readline, ''):
#         prev_call = int(line[:-2])
#         break
#     return prev_call

def read_power():
    ef = open('/sys/class/powercap/intel-rapl/intel-rapl:0/intel-rapl:0:1/energy_uj', 'r')
    prev_call = int(ef.read())
    ef.close()
    return prev_call


def test_instruction(instruction, driver):
    try:
        if instruction in instructions.PUNOP: #Difference in quotes, maybe i should unify it.
                driver.execute_script("""return testInstruction({})""".format(instruction))
        else:
                driver.execute_script("""return testInstruction("{}")""".format(instruction))
    except Exception as e:
        print("Failed test: ",e)



def test_all_instructions(browser="firefox"):
    counter = 0
    driver = get_driver(browser)
    try:
        for instruction in instructions.ALLOP:
            print("{}/{} - {}%: Testing {}; ".format(counter,len(instructions.ALLOP), math.floor(counter/len(instructions.ALLOP)*100), instruction))
            res_instr = test_instruction(instruction,driver)
            counter+=1
    finally:
        driver.close()


def square_signal(instruction, repetitions = 10, browser='firefox'):
    driver = get_driver(browser)
    try:
        for i in range(repetitions):
            test_instruction(instruction, driver)
            driver.execute_script("return idle()")
    except:
        print("Failed")
    finally:
        driver.close()


#                                     MAIN                                     #


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', help = "Test all instructions in a row.", action = 'store_true', default = False)
    parser.add_argument('-s', '--square', help = "Runs a single instruction with pauses between instructions to create a square signal.", type=str)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    driver = get_driver("firefox")
    print(driver.execute_script("""return """))
