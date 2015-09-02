#!/usr/bin/python
# Authors:
#             Zou Yuanyuan<zouyuanyuan@xiaomi.com>

import os
import sys
import time
import subprocess
import string

def load_json_config():
    import json
    # Pretend that we load the following JSON file:
    source = '''
        {"--force": true,
        "--timeout": "10",
        "--baud": "9600"}
        '''
    return json.loads(source)

def shell_command(cmd, timeout=15):
    """shell communication for quick return in sync mode"""
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    time_cnt = 0
    exit_code = None
    while time_cnt < timeout:
        exit_code = proc.poll()
        if not exit_code is None:
            break
        time_cnt += 0.2
        time.sleep(0.2)
    print cmd,exit_code
    if exit_code is None:
        # killall(proc.pid)
        exit_code = -1
        result = []
    else:
        result = proc.stdout.readlines() or proc.stderr.readlines()
    return [exit_code, result]
    
def str2str(src):
    """string to printable string"""
    if isinstance(src, unicode):
        return src.encode("utf8")
    if isinstance(src, str):
        accept = string.punctuation + string.letters + string.digits + ' \r\n'
        return filter(lambda x: x in accept, src)
    return ""

def shell_command_ext(cmd="", timeout=None, boutput=False,  stdout_file=None,  stderr_file=None):
    """shell executor, return [exitcode, stdout/stderr]
       timeout: None means unlimited timeout
       boutput: specify whether print output during the command running
    """
    if stdout_file is None:
        stdout_file = os.path.expanduser("~") + os.sep + "shell_stdout"

    if stderr_file is None:
        stderr_file = os.path.expanduser("~") + os.sep + "shell_stderr"

    exit_code = None
    wbuffile1 = file(stdout_file, "w")
    wbuffile2 = file(stderr_file, "w")
    rbuffile1 = file(stdout_file, "r")
    rbuffile2 = file(stderr_file, "r")
    cmd_open = subprocess.Popen(args=cmd,  shell=True,   stdout=wbuffile1, stderr=wbuffile2)
    rbuffile1.seek(0)
    rbuffile2.seek(0)

    def print_log():
        """print the stdout to terminate"""
        sys.stdout.write(rbuffile1.read())
        sys.stdout.write(rbuffile2.read())
        sys.stdout.flush()

    while True:
        exit_code = cmd_open.poll()
        if exit_code is not None:
            break
        if boutput:
            print_log()
        if timeout is not None:
            timeout -= 0.1
            if timeout <= 0:
                try:
                    exit_code = "timeout"
                    cmd_open.terminate()
                    time.sleep(5)
                except OSError:
                    killall(cmd_open.pid)
                break
        time.sleep(0.1)

    if boutput:
        print_log()
    rbuffile1.seek(0)
    rbuffile2.seek(0)
    stdout_log = str2str(rbuffile1.read())
    stderr_log = str2str(rbuffile2.read())
    if 'returncode=' in stdout_log:
        index = stdout_log.find('returncode=') + 11
        exit_code = str(stdout_log[index:]).strip('\r\n')
    # stdout_log = '<![CDATA[' + stdout_log + ']]>'
    # stderr_log = '<![CDATA[' + stderr_log + ']]>'

    wbuffile1.close()
    wbuffile2.close()
    rbuffile1.close()
    rbuffile2.close()
    os.remove(stdout_file)
    os.remove(stderr_file)
    return [exit_code, stdout_log, stderr_log]
