#!/usr/bin/python3
##
## See README.md for usage explanation
##
from os import path, listdir, getcwd
from typing import Dict, Union, List, Type
import sys
from time import sleep
from argparse import ArgumentParser, Namespace
from traceback import print_exc
from binascii import hexlify
import re
import json
# TODO: Use a consistent solution to find testerbase 
# -> e.g. install as pip package
libpath = path.abspath(path.dirname(sys.argv[0]))
sys.path.append(path.join(libpath, 'tester'))
import testerBase
## Global Hardcoded Constants ##
PORT = 13400
TESTER_IP = "172.17.0.5"
TARGET_IP = "172.17.0.111"
TESTER_ADDRESS = 0x767
TARGET_ADDRESS = 0x747
ROUTE = 0x00
MACROFILE = ""
MACROS: List[str] = [
    "10 01 # Enter Default Session",
    "10 60 # Enter Prod Session",
    "22 c0 0b # Read PD SW Version",
    "22 20 00 # Read CAN ID",
    "22 70 31 # Read uBlox Version",
    "31 01 11 20 # Run RTC Selftest",
    "22 30 00 # Read Part Number",
    "22 80 01 # Read ECU ID"]
def find_file(search_dir: str, filename: str) -> Union[str, None]:
    """This function searches recursively upwards for a file.
       Beginning in the start directory it goes one directory
       up until it reaches the root directory or the file was found.
    Args:
        search_dir (str): The start directory for the search
        filename (str): Name of the config file
    Returns:
        (str, None): Either the absolute path to the config file
            or None if no file was found.
    """
    file_abspath = None
    while True:
        file_list = listdir(search_dir)
        parent_dir = path.dirname(search_dir)
        if filename in file_list:
            file_abspath = path.join(search_dir, filename)
            break
        else:
            if search_dir == parent_dir:
                break #if dir is root dir then break
            else:
                # next iteration we search one directory upwards
                search_dir = parent_dir
    return file_abspath
def load_config_file(start_dir: str, filename: str) ->dict:
    """This function loads an existing config file
       for send.py into a dictionary.
    Args:
        start_dir (str): The start directory for the search
        filename (str): Name of the config file
    Returns:
        dict: A configuration for send.py
    """
    args: dict = {}
    foundfile = find_file(start_dir, filename)
    if not foundfile:
        return args
    with open(file=foundfile, mode='r', encoding='utf-8') as fp:
        doc = json.load(fp)
        args = doc
    return args
def safe_ba2ascii(str):
    return re.sub(r'[^\x20-\x7e]', r' ', str.decode('ascii', errors='ignore'))
def split_cmd_comment(cmd:str, separator: str = '#'):
    cmmnt = None
    cmmntpos = cmd.find(separator)
    if cmmntpos >= 0:
        cmmnt = cmd[cmmntpos:].strip()
        cmd = cmd[:cmmntpos].strip()
    return cmd, cmmnt
def print_hexcode(data, info, bare):
    data_bin = hexlify(data)
    if bare:
        print(data_bin.decode(), flush=True)
    else:
        print(f"{info} {data_bin.decode()} - {safe_ba2ascii(data)}")
def execute_request(args, tester, req):
    req = "".join(req)
    req, _ = split_cmd_comment(req)
    req = bytearray.fromhex(req)
    if len(req) < 1:
        return
    print_hexcode(data=req, info="REQ  :", bare=args.bare)
    tester.sendUds(bytearray(req))
    response = tester.expectUds()
    print_hexcode(data=response.data, info="RES  :", bare=args.bare)
def print_formated_list(list_obj: List[str], sep:str) -> None:
    sep_max_index: int = max([entry.find(sep) if entry is not None else -1 for entry in list_obj])
    for i, entry in enumerate(list_obj):
        cmd, cmmnt = split_cmd_comment(entry, sep)
        whitespace: str = " "*(sep_max_index-len(cmd))
        print(f"  {i+1}: {cmd} {whitespace}{cmmnt}")
def list_select(lst):
    if not lst:
        print("No selection available")
        return ""
    print_formated_list(list_obj=lst, sep="#")
    lstsel = input("1...0 or <ENTER> to abort: ").strip()
    if not lstsel:
        return ""
    try:
        lstidx = int(lstsel)-1
        if lstidx < -1 or lstidx >= len(lst):
            raise ValueError('Out of range.')
        if lstidx == -1:
            lstidx = lstidx+10
        return lst[lstidx]
    except:
        print("Invalid selection")
    return ""
def get_default_config(config: dict)->dict:
    # Hardcoded defaults
    config["port"] = config.get("port", PORT)
    config["testerIP"] = config.get("testerIP", TESTER_IP)
    config["targetIP"] = config.get("targetIP", TARGET_IP)
    config["testerAddress"] = config.get("testerAddress", TESTER_ADDRESS)
    config["targetAddress"] = config.get("targetAddress", TARGET_ADDRESS)
    config["route"] = config.get("route", ROUTE)
    config["macrofile"] = config.get("macrofile", MACROFILE)
    return config
def get_command_line_arguments(default_args: dict) -> Namespace:
    parser=ArgumentParser()
    # Communication parameters
    parser.add_argument("--port", nargs='?', default=default_args["port"],
                        type=int, help="default: 13400")
    parser.add_argument("--testerIP", nargs='?', default=default_args["testerIP"],
                        type=str, help="default: 172.17.0.5")
    parser.add_argument("--targetIP", nargs='?', default=default_args["targetIP"],
                        type=str, help="default: 172.17.0.111")
    parser.add_argument("--testerAddress", nargs='?', default=default_args["testerAddress"],
                        type=int, help="default: 1895 (0x767)")
    parser.add_argument("--targetAddress", nargs='?', default=default_args["targetAddress"],
                        type=int, help="default: 1863 (0x747)")
    parser.add_argument("--route", nargs='?', default=default_args["route"], type=int,
                        help="doip-route default: 0x00")
    # Other parameters
    parser.add_argument("--macros", dest="macrofile", default=default_args["macrofile"],
                        type=str, help="Macro Requests to be used in Interactive mode")
    parser.add_argument("--verbose", "-v", dest="verbose", default=False, action='store_true',
                        help="Verbose output")
    parser.add_argument("--bare", "-b", dest="bare", default=False, action='store_true',
                        help="Only print the bare request and response messages")
    parser.add_argument("--msg", "-m", metavar='N', action="append", type=str,
                        nargs='+', help='UDS requests to send. e.g. 22 D1 00')
    return parser.parse_args()
def set_user_input_macros(macrofile: Union[str, None]) -> None:
    """This function set the default macros the user can choose
        the requests from. If the macrofile argument is None then
        the default macros will be used
    Args:
        macrofile (str, None): Absolute path to a file containing
        macro definition for send.py
    """
    global MACROS
    if not macrofile:
        return
    with open(macrofile) as f:
        macros = [line.rstrip() for line in f]
        MACROS = macros
def execute_commandline_requests(args: Namespace, tester: Type[testerBase.TesterBase]) -> None:
    for msg in args.msg:
        command = "".join(msg)
        execute_request(args, tester, command)
def execute_user_inputs(args: Namespace, tester: Type[testerBase.TesterBase]) -> None:
    history: List[str] = []
    while True:
        msg = input("Enter Request: ").strip()
        if not msg:
            break
        if msg == "*":
            msg = list_select(history)
        if msg == "/":
            msg = list_select(MACROS)
        if not msg:
            continue
        if ("exit" in msg) or ("quit" in msg) or ("q" in msg):
            break
        if not history or history[-1] != msg:
            history.append(msg)
            while len(history) > 10:
                history = history[1:]
        execute_request(args, tester, msg.split())
def main() -> None:
    cfgargs: Dict[str, Union[str, int]] = get_default_config(load_config_file(getcwd(), ".diag"))
    args: Namespace = get_command_line_arguments(cfgargs)
    set_user_input_macros(args.macrofile)
    if args.verbose:
        print ("Using arguments: " + str(args))
    try:
        tester=testerBase.TesterBase(args)
        tester.connectWithRoute()
        if args.msg:
            execute_commandline_requests(args, tester)
        else:
            execute_user_inputs(args, tester)
    except Exception as e:
        testerBase.EmitResult("__FATAL__", "Exception:" + str(e))
        print_exc(file=sys.stderr)
        sys.stdout.flush()
        sleep(1)
    finally:
        tester.disconnect()
if __name__=="__main__":
    main()