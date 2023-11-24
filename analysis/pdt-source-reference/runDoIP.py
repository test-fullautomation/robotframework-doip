from robot.api.deco import keyword, library # required when using @keyword, @library decorators
import subprocess
import os
import re
from textwrap import wrap
@keyword
def run_DoIP(targetIP, testerIP, lMsg, route=0):

    cmd = F"python {os.path.realpath(os.path.dirname(__file__))}/send.py --targetIP={targetIP} --testerIP={testerIP} --route={route}"
    for msg in lMsg:
        cmd = cmd + F" -m {msg}"

    result = str(subprocess.check_output(cmd))
    index = result.find("RES  :")
    if index != -1:
        resp = result[index:]
        return True , resp
    return False, "FAIL"

@keyword
def getBuildVersionLabel(sResp):
    sVersion = ""
    head = sResp.find("62700d") + len("62700d")
    sBuff = sResp[head:]
    sBuff = wrap(sBuff, 2)
    for item in sBuff:
        if item == '00':
            break
        sVersion = sVersion + chr(int(item,16))
    return sVersion

@keyword
def getPackageVersionLabel(sPackagePath, sHeader=None):
    pattern = re.compile('_([0-9_.]*).zip')
    for file in os.listdir(sPackagePath):
        if sHeader:
            if (file.endswith(".zip") and (str(file).find(sHeader) != -1)):
                name = file.split("_")
                version = name[2].split(".z")[0]
                return True, version
        else:
            matchList = pattern.findall(str(file))
            if matchList:
                version = matchList[0]
                version = version.replace("_", ".")
                return True, version
    return False, "Not Found"

@keyword
def getSoftwareVersion(sResp):
    sVersion = ""
    head = sResp.find("62f195") + len("62f195")
    sBuff = sResp[head:]
    tail = sBuff.find(" - ")
    sBuff = sBuff[0:tail]
    sBuff = wrap(sBuff, 2)
    for item in sBuff:
        sVersion = sVersion + chr(int(item, 16))
    return sVersion