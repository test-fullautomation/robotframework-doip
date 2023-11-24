# base-classes Node and Tester
import sys
import socket
import binascii
import doiptypes
import time
import subprocess
from platform import system
from robot.libraries.BuiltIn import BuiltIn
if sys.version_info[0] == 2:
    import thread
if sys.version_info[0] == 3:
    import _thread as thread
# global var introduced do to Trace
verbose = False
def setVerbose(doSet):
    global verbose
    verbose=doSet
def Trace(info):
    global verbose
    if verbose:
        print("["+str(time.time())+"][ doip.py ]" + info)
        sys.stdout.flush()
class Node:
   def __init__(self, address, identification, tester):
      Trace("Node:__init__")
      self.active = 0
      self.identification = identification
      self.address = address
      self.tester = tester
      self.nodeType = -1
      self.maxTcpSockets = -1
      self.currTcpSockets = -1
      self.maxDataSize = -1
      self.powerMode = -1
      self.activationType = -1
   def __str__ (self):
      return f"{self.address[0]} >>> {self.identification} [{self.powerMode},\
             {self.nodeType},{self.maxTcpSockets},{self.currTcpSockets},{self.maxDataSize}]"
   # application commands
   def connect (self):
      Trace("Node:connect: self.address=" + str(self.address))
      self.active = 1
      self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socketTCP.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
      self.socketTCP.connect(self.address)
      self.access = thread.allocate_lock()
      self.listener = thread.start_new_thread(self.listenTCP, ())
   def powerModeReq (self):
      Trace("Node:powerModeReq")
      message = doiptypes.Message(doiptypes.PowerModeRequest())
      Trace("SEND[UDP]: " + str(self.address) + " >> " + str(binascii.hexlify(message.serialize())))
      self.tester.socketUDP.sendto(message.serialize(), self.address)
   def entityStatusReq (self):
      Trace("Node:entityStatusReq")
      message = doiptypes.Message(doiptypes.EntityStatusRequest())
      Trace("SEND[UDP]: " + str(self.address) + " >> " + str(binascii.hexlify(message.serialize())))
      self.tester.socketUDP.sendto(message.serialize(), self.address)
   def routingActivationReq (self, actNumber, oemdata):
      Trace("Node:routingActivationReq")
      self.activationType = actNumber
      message = doiptypes.Message(doiptypes.RoutingActivationRequest(self.tester.testerAddr, actNumber, oemdata))
      try:
          Trace("SEND[TCP]: " + str(self.address) + " >> " + binascii.hexlify(message.serialize()))
      except:
          Trace("SEND[TCP]: " + str(self.address) + " >> " + str(binascii.hexlify(message.serialize())))
      self.socketTCP.send(message.serialize())
   def diagnosticRequest (self, targetAddress, data):
      Trace("Node:diagnosticRequest")
      message = doiptypes.Message(doiptypes.DiagnosticMessage(data, self.tester.testerAddr, targetAddress))
      try:
          Trace("SEND[TCP]: " + str(self.address) + " >> " + binascii.hexlify(message.serialize()))
      except:
          Trace("SEND[TCP]: " + str(self.address) + " >> " + str(binascii.hexlify(message.serialize())))
      self.socketTCP.send(message.serialize())
   # the TCP socket listener
   def listenTCP (self):
      Trace("Node:listenTCP START")
      self.tester.entityConnectInd(self)
      while self.active == 1:
         data = self.socketTCP.recv(2048)
         if len(data) == 0:
            #socket closed
            self.active = 0
            Trace("END[TCP]: " + str(self.address))
            self.tester.entityDisconnectInd(self)
         else:
            Trace("Node:listenTCP: RECV[TCP]: " + str(self.address) + " >> " + str(binascii.hexlify(data)))
            while len(data) > 0:
               (message, data) = doiptypes.parseMessage(bytearray(data))
               #Trace message
               message.payload.visit(self, self.address)
   # callbacks from message visitors
   def protocolError(self, payload, address):
      Trace("Node:protocolError")
      Trace(str(address) + " >> " + str(payload))
   def aliveCheckReq(self, payload, address):
      Trace("Node:aliveCheckReq")
      # just ping back
      message = doiptypes.Message(doiptypes.AliveCheckResponse(self.tester.testerAddr))
      Trace("SEND[TCP]: " + str(self.address) + " >> " + str(binascii.hexlify(message.serialize())))
      self.socketTCP.send(message.serialize())
   def activationResponse(self, payload, address):
      Trace("Node:activationResponse")
      if payload.ResponseType != 0x10: #activation failed?
         self.activationType = -1
      self.tester.routingActivationInd(self, self.activationType, payload.ResponseType)
   def diagnosticResponse(self, payload, address):
      Trace("Node:diagnosticResponse")
      self.tester.diagnosticResponse(self, payload.data)
   def diagnosticAck(self, payload, address):
      Trace("Node:diagnosticAck")
      self.tester.diagnosticAck(self, payload.ACK)
   def diagnosticNack(self, payload, address):
      Trace("Node:diagnosticNack")
      self.tester.diagnosticNack(self, payload.NACK)
# Tester can connect to serveral nodes.
class Tester:
   def __init__(self, host, port, testerAddr):
      Trace("Tester:__init__")
      self.nodes = []
      self.active = 1
      self.port = port
      Trace("  port:" + str(port))
      self.host = host
      Trace("  host:" + host)
      self.testerAddr = testerAddr
      Trace("  testerAddr:" + str(testerAddr))
      self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.socketUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
      localport = port
      #check IP validity before binding
      parameter = '-n' if system().lower()=='windows' else '-c'
      command = ['ping', parameter, '1', host]
      result = subprocess.run(command, capture_output=True)
      BuiltIn().log(result.stdout, 'ERROR')
      if result.returncode != 0:
         return
      while True:
         try:
            self.socketUDP.bind((host, localport))
         except:
            localport = localport + 1
            continue
         break
      self.access = thread.allocate_lock()
      Trace("listenUDP")
      self.listener = thread.start_new_thread(self.listenUDP, ())
   def stop(self):
      Trace("Tester:stop")
      self.active = 0
      self.socketUDP.close()
   # the UDP socket listener
   def listenUDP(self):
      Trace("Tester:listenUDP START")
      Trace( "self.active "+str(self.active))
      while self.active == 1:
         data, address = self.socketUDP.recvfrom(8096)
         Trace("data, address"+str(data)+" "+str(address))
         Trace("Tester:listenUDP: RECV[UDP]: " + str(address) + " >> " + str(binascii.hexlify(data)))
         if address != self.host: # ignore loopback messages (e.g. broadcasts)
            while len(data) > 0:
               (message, data) = doiptypes.parseMessage(bytearray(data))
               #print message
               message.payload.visit(self, address)
   # application commands
   def discoverEntities(self, target='255.255.255.255'):
      message = doiptypes.Message(doiptypes.VehicleIdentificationRequest())
      Trace("Tester:discoverEntities: SEND[UDP]: " + str((target, self.port)) + " >> " + str(binascii.hexlify(message.serialize())))
      self.socketUDP.sendto(message.serialize(), (target, self.port))
   # to be overriden by derived classes
   def createNode(self, address, payload):
      Trace("Tester:createNode: : " + str(address) + " " + str(payload))
      return Node(address=address, identification=payload, tester=self)# to be overridden when required
   def discoveredEntityInd(self, node):
      Trace(f"Tester:discoveredEntityInd: : {node.address} {node.identification}")
      return # to be overridden
   def powerModeInd(self, node):
      Trace("Tester:powerModeInd: tbd")
      return # to be overridden
   def entityStatusInd(self, node):
      Trace("Tester:entityStatusInd: tbd")
      return # to be overridden
   def entityConnectInd(self, node):
      Trace("Tester:entityConnectInd: tbd")
      return # to be overridden
   def entityDisconnectInd(self, node):
      Trace("Tester:entityDisconnectInd: tbd")
      return # to be overridden
   def routingActivationInd(self, node, actType, respType):
      Trace("Tester:routingActivationInd: tbd")
      return # to be overridden
   def diagnosticResponse(self, node, data):
      Trace("Tester:diagnosticResponse: tbd")
      return # to be overridden
   def diagnosticAck(self, node, ACK):
      Trace("Tester:diagnosticAck: tbd")
      return # to be overridden
   def diagnosticNack(self, node, NACK):
      Trace("Tester:diagnosticNack: tbd")
      return # to be overridden
   # callbacks from message visitors
   def protocolError(self, payload, address):
      Trace("Tester:protocolError!!!")
      Trace(str(address) + " >> " + str(payload))
   def vehicleAnnouncement(self, payload, address):
      Trace("Tester:vehicleAnnouncement")
      currNode = None
      self.access.acquire()
      try:
         for node in self.nodes:
            if node.address == address:
               node.identification = payload #Node was already discovered, just update the payload
               currNode = node
               break
         else:
            node = self.createNode(address, payload)
            currNode = node
            self.nodes.append(node)
      except BaseException as e:
         print(e)
      self.access.release()
      if currNode != None:
         self.discoveredEntityInd(currNode)
   def powerModeResp (self, payload, address):
      Trace("Tester:powerModeResp")
      currNode = None
      #print str(address) + " >> " + str(payload)
      self.access.acquire()
      for node in self.nodes:
         if node.address == address:
            node.powerMode = payload.mode
            currNode = node
            break
      self.access.release()
      if currNode != None:
         self.powerModeInd(currNode)
   def entityStatusResp (self, payload, address):
      Trace("Tester:entityStatusResp")
      currNode = None
      #print str(address) + " >> " + str(payload)
      self.access.acquire()
      for node in self.nodes:
         if node.address == address:
            node.nodeType = payload.nodeType
            node.maxTcpSockets = payload.maxTcpSockets
            node.currTcpSockets = payload.currTcpSockets
            node.maxDataSize = payload.maxDataSize
            currNode = node
            break
      self.access.release()
      if currNode != None:
         self.entityStatusInd(currNode)