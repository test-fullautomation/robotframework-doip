#!/usr/bin/python
###################
# provide basic framework for test-scripts.
# TesterBase is limited to one connection.
###################
#import os
import sys
import time
import binascii
import doip
import doiptypes
#import udstypes
import socket
from threading import Timer
import traceback
import argparse
verbose=False
##########################
#  utilities
##########################
def EmitResult(indicator, msg):
    print("RES:__" + indicator + "__:" +str(msg))
    sys.stdout.flush()
def toHex(binInput):
    res=""
    for b in binInput:
#        TraceLocal("toHex: " + str(b))
        res += "%02x" %b
    return res
def strToArray(strVal):
    return strVal.encode()
def U16ToByteArray(u16):
    u16=int(u16)
    TraceLocal("U16ToByteArray: u16=" + str(u16))
    res=bytearray([(u16 >> 8) & 0xFF, u16 & 0xFF])
    TraceLocal("U16ToByteArray: u16=" + str(u16) + " -> " + str(binascii.hexlify(res)))
    return res
def U8ToByteArray(u8):
    res=bytearray([u8 & 0xFF])
    TraceLocal("U8ToByteArray: u8=" + str(u8) + " -> " + str(binascii.hexlify(res)))
    return res
def uxxToByteArray(uxxValue, formatSize):
    res=bytearray()
    for i in range(0, formatSize):
        shift=(formatSize - (1+ i))*8
        val=(uxxValue >> shift) & 0xFF
        TraceLocal("formatSize: i= " + str(i) + " shift=" + str(shift) +  " val=" + str(val) + "(" + toHex(bytearray([val])) + ")")
        res.append(val)
    TraceLocal("uxxToByteArray(uxxValue=" + str(uxxValue) + " formatSize="+ str(formatSize) + ") -> " + toHex(res))
    return res
def getUxxFromByteArray(bArray, iStart, numBytes):
    TraceLocal("getUxxFromByteArray: iStart=" + str(iStart) + " numBytes=" + str(numBytes))
    res=bArray[iStart];
    TraceLocal("getUxxFromByteArray: res0=" + str(res))
    if (numBytes==1):
        return res;
    for i in range(1, numBytes):
        res= (res << 8) + bArray[iStart + i] ;
        TraceLocal("getUxxFromByteArray: adding val=" + str(bArray[iStart + i])  + " res=" + str(res))
    return res;
def TraceLocal(info):
    Trace(info, "testerBase")
def Trace(info, source="main"):
    global verbose
    if verbose:
        print("["+str(time.time())+"][" + source + "]: " + str(info))
        sys.stdout.flush()
class TestFailException(Exception):
    pass
def tcFail(comment=None):
    TraceLocal("tcFail: " + str(comment))
    traceback.print_stack()
    raise TestFailException(str(comment))
def getArgumentParser():
    parser=argparse.ArgumentParser()
    parser.add_argument("--port",          default=13400, type=int, help="default: 13400")
    parser.add_argument("--testerIP",      default="172.17.0.5", type=str, help="default: 172.17.0.5")
    parser.add_argument("--targetIP",      default="172.17.0.1", type=str, help="default: 172.17.0.1")
    parser.add_argument("--testerAddress", default=0x767, type=int, help="default: 1895 (0x767)")
    parser.add_argument("--targetAddress", default=0x747, type=int, help="default: 1863 (0x747)")
    parser.add_argument("--route",         default=0x02, type=int, help="doip-route default: 0x02")
    parser.add_argument("--verbose",       default=False, const=True, action='store_const', dest='verbose', help="verbose-mode")
    return parser
###################################################
# class to combine several tests into a test-suite
###################################################
class TestSuite:
    def __init__(self):
        self.tests=[]
        self.numTc=0
        self.numPassed=0
        self.numFailed=0
    def doTest(self, testFn):
        self.tcName=testFn.__name__
        self.passed=True
        self.numTc=self.numTc + 1
        result= {
            "name" : self.tcName,
            "passed" : True
        }
        try:
            testFn()
        except TestFailException as error:
            TraceLocal("#### tcFail(" + str(self.tcName) + ")")
            TraceLocal("Cought TestFailException: " + str(error))
            result["passed"]=False
        self.tests.append(result)
        if (result["passed"]==True):
            self.numPassed=self.numPassed+1
        else:
            self.numFailed=self.numFailed+1
    def showVerdict(self):
        TraceLocal("showVerdict:")
        TraceLocal("num TC=" + str(self.numTc))
        TraceLocal("numPassed=" + str(self.numPassed))
        TraceLocal("numFailed=" + str(self.numFailed))
        for tc in self.tests:
            if (tc["passed"]==True):
                TraceLocal("   " + tc["name"] + " -> PASSED")
            else:
                TraceLocal("   " + tc["name"] + " -> FAILED")
class Uds:
    def __init__(self, data=None):
        self.data=bytearray()
        if data:
            self.data=data
    def fromDoipMsg(self, doipMsg):
        self.data=doipMsg.payload[4:]
    def getType(self):
        if len(self.data):
            return self.data[0];
        else:
            return 0
    def getData(self):
        if len(self.data)>1:
            return self.data[1:];
        else:
            return bytearray()
class TestNode(doip.Node):
    def __init__ (self, targetIP, targetAddress, tester):
        TraceLocal("TestNode:__init__")
        TraceLocal("   targetIP=" + str(targetIP))
        TraceLocal("   targetAddress=" + str(targetAddress))
        doip.Node.__init__(self, targetIP, U16ToByteArray(targetAddress), tester)
        self.targetIP=targetIP
        self.targetAddress=targetAddress
class DoipMsg():
    def __init__ (self, prot=0x02, protInv=0xFD, payloadType=0x8001, payloadLen=None, payload=bytearray(), doPrint=False):
        if payloadLen==None:
            payloadLen=len(payload)
        self.hdr=bytearray(8)
        self.hdr[0]=prot;
        self.hdr[1]=protInv;
        self.hdr[2]=((payloadType >> 8) & 0xFF);
        self.hdr[3]=((payloadType >> 0) & 0xFF);
        self.hdr[4]=((payloadLen >> 24) & 0xFF);
        self.hdr[5]=((payloadLen >> 16) & 0xFF);
        self.hdr[6]=((payloadLen >>  8) & 0xFF);
        self.hdr[7]=((payloadLen >>  0) & 0xFF);
        self.payload=payload
        if (doPrint):
            TraceLocal("DoipMsg len=" + str(len(self.payload)))
            TraceLocal("   hdr:" + str(binascii.hexlify(self.hdr)))
            TraceLocal("   payload:" + str(binascii.hexlify(self.payload)))
        self.data=self.hdr+self.payload
        self.message=None
    def set(self, data, message):
        self.hdr=data[0:8]
        self.payload=data[8:]
        self.data=data
        self.message=message
    def getName(self):
        if (self.message==None):
            return "Unknown"
        return self.message.payload.Name
#######################################################
# test-cases use TesterBase to communicate with server
#######################################################
class TesterBase(doip.Tester):
    def __init__ (self, args):
        TraceLocal("TesterBase:__init__")
        if (args.testerIP == None):
            raise Exception("missing arg testerIP")
        if (args.targetIP == None):
            raise Exception("missing arg targetIP")
        if (args.testerAddress == None):
            raise Exception("missing arg testerAddress")
        if (args.targetAddress == None):
            raise Exception("missing arg targetAddress")
        if (args.port == None):
            raise Exception("missing arg port");
        global verbose
        verbose=args.verbose
        doiptypes.setVerbose(verbose)
        doip.setVerbose(verbose)
        doip.Tester.__init__(self, args.testerIP, args.port, args.testerAddress)
        self.testerIP=args.testerIP
        self.targetIP=args.targetIP
        self.route=args.route
        TraceLocal("TesterBase:targetIP=" + str(self.targetIP))
        self.targetAddress=args.targetAddress
        self.testerAddress=args.testerAddress
        self.testNode = TestNode(self.targetIP, self.targetAddress, self)
        self.connected=False
    def connectSync(self):
      self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socketTCP.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
      self.socketTCP.settimeout(5)
      TraceLocal("Tester:connectSync: try to connect to " + self.targetIP + ":" + str(self.port))
      self.socketTCP.connect((self.targetIP, self.port))
      self.testNode.socketTCP=self.socketTCP
      self.connected=True
    def disconnect(self):
        TraceLocal("Tester:disconnect()")
        try:
            self.socketTCP.shutdown(socket.SHUT_RDWR);
            self.socketTCP.close();
        except Exception as e:
            TraceLocal("disconnect: not connected");
        self.connected=False
    def receiveBytes(self, numBytes, timeout):
        self.socketTCP.settimeout(timeout)
        numReceived=0;
        data=bytearray();
        try:
            chunk = self.socketTCP.recv(numBytes)
            data+=chunk
        except socket.timeout as e:
            TraceLocal("Tester:receiveBytes: Timeout")
#            self.socketTCP.close()
            return ("Timeout", data)
        if (len(chunk)==0):
            self.socketTCP.close()
            return ("Disconnect", data)
        else:
            return ("Ok", data)
    def receiveMsg(self, timeout=4):
        # receive header
        allOk=False
        doipMsgBin=bytearray()
        TraceLocal("Test::receiveMsg START timeout=" + str(timeout))
        (res, doipMsgBin)=self.receiveBytes(8, timeout)
        if res=="Timeout":
            TraceLocal("Test::receiveMsg Timout waiting for doipHeader")
            message = doiptypes.Message(doiptypes.Timeout())
            doipMsgBin=message.payload.getDefaultData()
        elif res=="Disconnect":
            TraceLocal("Test::receiveMsg Disconnect waiting for doipHeader")
            message = doiptypes.Message(doiptypes.Disconnect())
            doipMsgBin=message.payload.getDefaultData()
        else:
            payloadLen=(doipMsgBin[4]<<24) + (doipMsgBin[5]<<16) + (doipMsgBin[6]<<8) + (doipMsgBin[7])
            TraceLocal("Test::receiveMsg doipHdr=" + str(binascii.hexlify(doipMsgBin)) + " payloadLen=" + str(payloadLen))
            allOk=True
        if allOk:
            (res, payloadBin)=self.receiveBytes(payloadLen, timeout)
            if res=="Timeout":
                TraceLocal("Test::receiveMsg Timout waiting for payload")
                message = doiptypes.Message(doiptypes.Timeout())
                doipMsgBin=message.payload.getDefaultData()
            elif res=="Disconnect":
                TraceLocal("Test::receiveMsg Disconnect waiting for payload")
                message = doiptypes.Message(doiptypes.Disconnect())
                doipMsgBin=message.payload.getDefaultData()
            else:
                doipMsgBin=doipMsgBin+payloadBin
                (message, bla)=doiptypes.parseMessage(doipMsgBin)
                allOk=True
        TraceLocal("Tester:receiveMsg:got:" + str(binascii.hexlify(doipMsgBin)))
        doipMsg=DoipMsg(doPrint=False)
        doipMsg.set(doipMsgBin, message)
        return doipMsg
    def expectMsg(self, msgName, timeout=4, expect=None, doFail=True):
        TraceLocal("Tester:expectMsg:" + str(msgName) + " START")
        doipMsg=self.receiveMsg(timeout)
        res=(msgName==None or (doipMsg.getName()==msgName))
        TraceLocal("Tester:expectMsg next step: got " + doipMsg.getName())
        if expect:
            if expect.data != doipMsg.data:
                TraceLocal("Tester:expectMsg: wrong data:")
                TraceLocal("expected: " + str(binascii.hexlify(expect.data)))
                TraceLocal("got:      " + str(binascii.hexlify(doipMsg.data)))
                tcFail("Expect "  + str(msgName) + " : wrong content")
                TraceLocal("Tester:expectMsg: END res=" + str(res))
                if not res:
                    if (doFail):
                        tcFail("Expect "  + str(msgName) + " : wrong type")
                        return None
        return doipMsg
    def send(self, doipMsg):
        # for some reason, large chunks don't make it to the target, so we split.
        TraceLocal("send: " + str(binascii.hexlify(doipMsg.data)))
        numBytes=len(doipMsg.data)
        offset=0
        TraceLocal("send() START numBytes=" + str(numBytes))
        while  numBytes:
            numSend=numBytes
            if numSend > 0x4000:
                numSend=0x4000
            numBytes=numBytes-numSend
            TraceLocal("send() chunk numSend=" + str(numSend))
            self.socketTCP.send(doipMsg.data[offset:offset+numSend])
            offset=offset+numSend
            time.sleep(0.1)
        TraceLocal("send() DONE numBytes=" + str(numBytes))
    def sendUds(self, uds):
        TraceLocal("sendUds: SID=" + str(hex(uds[0])))
        self.testNode.diagnosticRequest(self.targetAddress, uds)
    def getTimeMs(self):
        return int(round(time.time() * 1000))
    def expectUds(self, udsType=0, udsContent=None, timeout=6 ):
        TraceLocal("Tester:expectUds START")
        timeStartMs=self.getTimeMs()
        timeEndMs=timeStartMs + timeout*1000
        while self.getTimeMs() < timeEndMs:
            TraceLocal("Tester:expectUds timeLeftMs=" + str(timeEndMs- self.getTimeMs()))
            msgtimeout=max(1, timeEndMs-self.getTimeMs())
            doipMsg=self.expectMsg(None, msgtimeout/1000)
            msgName=doipMsg.getName()
            TraceLocal("doipMsg.payload=" + toHex(doipMsg.payload))
            if (msgName=="Timeout"):
                TraceLocal("Tester:expectUds: got Timeout")
                break
            if (msgName=="DiagnosticMessageAck"):
                TraceLocal("Tester:expectUds: got DiagnosticMessageAck")
                continue
            if (msgName=="DiagnosticMessage"):
                TraceLocal("Tester:expectUds got DiagnosticMessage")
                uds=Uds()
                uds.fromDoipMsg(doipMsg)
                if uds.getType()==0x7F:
                    TraceLocal("Tester:received negative Response 7F")
                    if len(uds.data) == 2  and uds.data[1]==0x3e:
                        TraceLocal("Tester:expectUds ignore error on tester-present")
                        continue
                    if len(uds.data) == 3  and uds.data[2]==0x78:
                        TraceLocal("Tester:expectUds ignore response pending")
                        continue
                break
        content=bytearray()
        if udsContent:
            content=udsContent[0:]
#02fd80020000000c074707670007670747
        uds=Uds()
        if len(doipMsg.data)<5:
            tcFail("expectUds: uds-content empty:")
        uds.fromDoipMsg(doipMsg)
        if udsType and udsType != uds.getType():
            tcFail("expectUds: wrong uds-type: expected: "  + hex(udsType) + " got: " + hex(uds.getType()))
        if len(content):
            if (udsType != 0):
                content.insert(0, udsType)
            if content != uds.data:
                TraceLocal("Tester:expectUds: wrong data:")
                TraceLocal("expected: " + str(binascii.hexlify(content)))
                TraceLocal("got:      " + str(binascii.hexlify(doipMsg.data)))
                tcFail("ExpectUds "  + msgName + " : wrong content")
        TraceLocal("expectUds ok, got:      " + str(binascii.hexlify(uds.data)))
        return uds
    def connectWithRoute(self, route=None):
        TraceLocal("connectWithRoute")
        if (route==None):
            route=self.route
        self.connectSync()
        self.testNode.routingActivationReq(route, bytearray(4))
        data=self.expectMsg("RoutingActivationResponse")
    def enterSession(self, sessionType):
        TraceLocal("enterSession:" + str(sessionType))
        uds = bytearray([0x10, sessionType])
        self.testNode.diagnosticRequest(self.targetAddress, uds)
        doipMsg=self.expectMsg("DiagnosticMessageAck")
        doipMsg=self.expectMsg("DiagnosticMessage")
    def getDiagMsgHeader(self, testerAddress=None, targetAddress=None):
        if testerAddress==None:
            testerAddress=self.testerAddress
        if targetAddress==None:
            targetAddress=self.targetAddress
        diagMsgHdr=bytearray();
        diagMsgHdr=diagMsgHdr+U16ToByteArray(testerAddress)+U16ToByteArray(targetAddress)
        return diagMsgHdr
def exitHandler():
    TraceLocal("ExitHandler!!!");
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(1)
import atexit
atexit.register(exitHandler)