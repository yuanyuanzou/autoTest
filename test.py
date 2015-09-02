#!/usr/bin/python
# Authors:
#             Zou Yuanyuan<zouyuanyuan@xiaomi.com>
"""Example of program with many options using docopt.

Usage:
    runtest.py --testpkg=DIR
    runtest.py --version
    runtest.py --install=DIR

Arguments:

Options:
    -h --help            show this help message and exit
    --version            show version and exit
    --testsuite=DIR      run regression tests from dir

"""
from tools.docopt import docopt
from tools.commandfile import shell_command_ext, shell_command
import os
import sys
import time
import subprocess
import string

APK_INSTALL = "adb -s %s install %s"
LAUNCH_TEST = "adb -s %s  shell am  instrument  -w  -r  %s/android.support.test.runner.AndroidJUnitRunner"


def _get_device_ids():
    """get android deivce list of ids"""
    result = []
    exit_code, ret = shell_command("adb devices")
    for line in ret:
        if str.find(line, "\tdevice") != -1:
            result.append(line.split("\t")[0])
    return result

def _testreport():
    logfile = os.path.expanduser("~") + os.sep + "logsrc"
    tmp_report = open(logfile,'r')
    result = []
    temp_result = {}
    readlog = False
    for line in tmp_report.readlines():
        line = line.strip()        
        if readlog:
            if "INSTRUMENTATION_STATUS:" in line or "Time:" in line:
                readlog =False
            else:
                temp_result["log"] = temp_result["log"] +line
        else:          
            if "INSTRUMENTATION_STATUS_CODE:" in line :
                if "0" in line:
                    temp_result["status"] = "success"      
                    continue  
                if "-2" in line or "-1" in line:
                    temp_result["status"] = "failed"
                    continue
            if "class" in line:
                 temp_result["class"] = line[line.find("class")+6:]
                 continue
            if " test=" in line:
                temp_result["testcase"] = line[line.find("test=")+5:]
                continue
            if "stream=" in line:
                temp_result["log"] = "log:"
                readlog = True
                continue

        if len(temp_result) >=3 :
            result.append(temp_result)
            temp_result = {}
        continue
    print result

if __name__ == '__main__':
    _testreport()