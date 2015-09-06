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
    --testpkg=DIR      run regression tests from dir

runtest.py --testpkg=com.mitv.buildchecktest.test
"""
from tools.docopt import docopt
from tools.commandfile import shell_command_ext, shell_command
import os
import sys
import time
import subprocess
import string
import json
from datetime import datetime

APK_INSTALL = "adb -s %s install %s"
LAUNCH_TEST = "adb -s %s  shell am  instrument  -w  -r  %s/android.support.test.runner.AndroidJUnitRunner"


def _get_device_ids():
    """get android deivce list of ids"""
    cmd_result = []
    exit_code, ret = shell_command("adb devices")
    for line in ret:
        if str.find(line, "\tdevice") != -1:
            cmd_result.append(line.split("\t")[0])
    return cmd_result

def _testreport(logsrc):
    START_TIME = datetime.today().strftime("%Y-%m-%d_%H_%M_%S")
    logfile = sys.path[0]+ os.sep + "result_file" + os.sep +"log"+START_TIME
    f = open(logfile,'w')
    f.write(logsrc)
    f.close()
    tmp_report = open(logfile,'r')
    result = []
    temp_result = {}
    readlog = False
    for line in tmp_report.readlines():
        line = line.strip()
        if "INSTRUMENTATION_STATUS_CODE:" in line :
            if "0" in line:
                temp_result["status"] = "pass"
                continue
            if "-2" in line or "-1" in line:
                temp_result["status"] = "failed"
                continue
        if "class=" in line:
             temp_result["class"] = line[line.find("class")+6:]
             continue
        if " test=" in line:
            temp_result["testcase"] = line[line.find("test=")+5:]
            continue
        if "stream=" in line:
            temp_result["log"] = ""
            readlog = True
            continue
        if readlog:
            if "INSTRUMENTATION_STATUS:" in line or "Time:" in line:
                readlog =False
                continue
            else:
                temp_result["log"] = temp_result["log"] +line
                continue

        if len(temp_result) ==4 :
            result.append(temp_result)
            temp_result = {}
            continue
    print result
    tmp_report.close()
    resultfile =sys.path[0]+ os.sep + "webshow" + os.sep + "result"
    file = open(resultfile,"w")  
    file.write(json.dumps(result))  
    file.close()

class AndroidMobile:

    def __init__(self, device_id=None):
          self.deviceid = device_id
    def shell_cmd(self, cmd="", timeout=15):
        cmdline = "adb -s %s shell %s" % (self.deviceid, cmd)
        return shell_command(cmdline, timeout)

    def shell_cmd_ext(self,
                      cmd="",
                      timeout=None,
                      boutput=False,
                      stdout_file=None,
                      stderr_file=None):
        cmdline = "adb -s %s shell '%s; echo returncode=$?'" % (
            self.deviceid, cmd)
        return shell_command_ext(cmdline, timeout, boutput, stdout_file, stderr_file)


    def install_package(self, pkgpath):
        """install a package on android device:
        push package and install with shell command
        """
        cmd = APK_INSTALL % (self.deviceid, pkgpath)
        exit_code, ret = shell_command(cmd)
        return ret

    def launch_test(self, pkg_name):
        timecnt = 0
        blauched = False
        cmdline = LAUNCH_TEST % (self.deviceid, pkg_name)
        exit_code, stdout_log, stderr_log= shell_command_ext(cmdline)
        self.result_json = _testreport(stdout_log)
        return blauched

    def result_show(self):
        import webbrowser
        webbrowser.open_new_tab("webshow" + os.sep +"index.html")


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0.0rc2') 
    Devices = AndroidMobile( _get_device_ids()[0])
    if arguments['--install']:
        Devices.install_package( arguments['--install'])
    elif arguments['--testpkg']:
        Devices.launch_test(arguments['--testpkg'])
        Devices.result_show()

         #adb shell am  instrument  -w  -r   com.mitv.buildchecktest.test/android.support.test.runner.AndroidJUnitRunner
