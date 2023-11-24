import binascii
import time
import sys
verbose=False
def setVerbose(doSet):
    global verbose
    verbose=doSet
def Trace(info):
    if verbose:
        print("["+str(time.time())+"][doiptypes]: " + info)
        sys.stdout.flush()
class GenericNack:
   def __init__ (self, stream):
      self.errorcode = stream[0]
      self.Length = 1
      self.Type = 0x0000
      self.Name="GenericNack"
   def __str__ (self):
      return "GenericNack[" + hex(self.errorcode) + "]"
   def visit (self, visitor, address):
      visitor.protocolError(self, address)
      
   def serialize (self):
      array = bytearray(self.Length)
      array[0] = self.errorcode
      return array
class VehicleIdentificationRequest:
   def __init__ (self, stream=None):
      self.Length = 0
      self.Type = 0x0001
      self.Name="VehicleIdentificationRequest"
   def __str__ (self):
      return "VehicleIdentificationRequest"
   def serialize (self):
      return bytearray()
   def visit (self, visitor, address):
      #simply ignore foreign identification requests
      return
class VehicleIdentificationRequestEID:
   def __init__ (self, EID):
      self.EID = EID#[6]byte
      self.Length = 6
      self.Type = 0x0002
      self.Name="VehicleIdentificationRequestEID"
   def __str__ (self):
      return "VehicleIdentificationRequestEID[" + self.EID + "]"
   def serialize (self):
      return bytearray(self.EID)
class VehicleIdentificationRequestVIN:
   def __init__ (self, VIN):
      self.VIN = VIN#[17]byte
      self.Length = 17
      self.Type = 0x0003
      self.Name="VehicleIdentificationRequestEID"
   def __str__ (self):
      return "VehicleIdentificationRequestEID[" + self.VIN + "]"
   def serialize (self):
      return bytearray(self.VIN)
class VehicleAnnouncement:
   def __init__ (self, stream):
      self.VIN = binascii.hexlify(stream[0:17])# [17]byte
      self.LogicalAddress = int(stream[17] << 8 | stream[18])#uint16
      self.EID = binascii.hexlify(stream[19:25])#[6]byte
      self.GID = binascii.hexlify(stream[25:31])#[6]byte
      self.FurtherActionRequired = int(stream[31])#byte
      self.VINGIDSyncStatus = int(stream[32])#byte
      self.Length = 33
      self.Type = 0x0004
      self.Name="VehicleAnnouncement"
   def __str__ (self):
      return "VehicleAnnouncement[" + hex(self.LogicalAddress) + "," + str(self.VIN)\
          + "," + str(self.EID) + "," + str(self.GID) +  "]"
   def visit (self, visitor, address):
      visitor.vehicleAnnouncement(self, address)
class RoutingActivationRequest:
   def __init__ (self, SourceAddress, ActivationType, OemSpecific):
      self.SourceAddress = SourceAddress
      self.ActivationType = ActivationType
      self.Reserved = bytearray(4)
      self.OemSpecific = OemSpecific[0:3] #limit any input to 4 bytes
#      self.Length = 11
      self.Length = 7
      self.Type = 0x0005
      self.Name="RoutingActivationRequest"
   def __str__ (self):
      return "RoutingActivationRequest[" + str(self.SourceAddress) + "," + self.ActivationType + "]";
   def serialize (self):
      array = bytearray(self.Length)
      array[0] = (self.SourceAddress >> 8) & 0xFF
      array[1] = (self.SourceAddress >> 0) & 0xFF
      array[2] = self.ActivationType
      #array[3:6] = [0]
      if (self.Length > 7):
         array[7:10] = self.OemSpecific
      return array
class RoutingActivationResponse:
   def __init__ (self, stream):
      self.ExternalAddress = int(stream[0] << 8 | stream[1])#uint16
      self.LogicalAddress = int(stream[2] << 8 | stream[3])#uint16
      self.ResponseType = stream[4]#uint8
      self.Reserved = stream[5:8]#[4]byte
      self.OemSpecific = stream[9:12]#[4]byte
      self.Length = 13
      self.Type = 0x0006
      self.Name="RoutingActivationResponse"
   def __str__ (self):
      return "RoutingActivationResponse[" + str(self.ExternalAddress) + "," + str(self.LogicalAddress) + "," + str(self.ResponseType) + "]"
   def visit (self, visitor, address):
      visitor.activationResponse(self, address)
actRespType2Str = {
   0x00 : "0x00: Unknown source address",
   0x01 : "0x01: All sockets in use",
   0x02 : "0x02: Wrong source address for connection",
   0x03 : "0x03: Source address used by other connection",
   0x04 : "0x04: Missing authentication",
   0x05 : "0x05: Rejected confirmation",
   0x06 : "0x06: Routing activation type not supported",
   0x10 : "0x10: Successful",
   0x11 : "0x11: Activation pending - confirmation required",
}
nackRespType2Str = {
   0x02 : "Invalid source address",
   0x03 : "Unknown target address",
   0x04 : "Message too large",
   0x05 : "out of memory",
   0x06 : "Target address unreachable",
   0x07 : "Unknown network",
   0x08 : "TP error",
}
class AliveCheckRequest:
   def __init__ (self, stream):
      self.Length = 0
      self.Type = 0x0007
      self.Name="AliveCheckRequest"
   def __str__ (self):
      return "AliveCheckRequest"
   def visit (self, visitor, address):
      visitor.aliveCheckReq(self, address)
class AliveCheckResponse:
   def __init__ (self, SourceAddress):
      self.LogicalAddress = SourceAddress
      self.Length = 2
      self.Type = 0x0008
      self.Name="AliveCheckResponse"
   def __str__ (self):
      return "AliveCheckResponse[" + str(self.LogicalAddress) + "]"
   def serialize (self):
      return bytearray()
class PowerModeRequest:
   def __init__ (self):
      self.Length = 0
      self.Type = 0x4003
      self.Name="PowerModeRequest"
   def __str__ (self):
      return "PowerModeRequest"
   def serialize (self):
      return bytearray()
class PowerModeResponse:
   def __init__ (self, stream):
      self.mode = int(stream[0])
      self.Length = 1
      self.Type = 0x4004
      self.Name="PowerModeResponse"
   def __str__ (self):
      return "PowerModeResponse[" + str(self.mode) + "]"
   def visit (self, visitor, address):
      visitor.powerModeResp(self, address)
class EntityStatusRequest:
   def __init__ (self):
      self.Length = 0
      self.Type = 0x4001
      self.Name="EntityStatusRequest"
   def __str__ (self):
      return "EntityStatusRequest"
   def serialize (self):
      return bytearray()
class EntityStatusResponse:
   def __init__ (self, stream):
      self.nodeType = int(stream[0])
      self.maxTcpSockets = int(stream[1])
      self.currTcpSockets = int(stream[2])
      self.maxDataSize = -1
      if len(stream) > 3:
         self.maxDataSize = int(stream[3] << 24 | stream[4] << 16 | stream[5] << 8 | stream[6])
      self.Length = len(stream)
      self.Type = 0x4002
      self.Name="EntityStatusResponse"
   def __str__ (self):
      return "EntityStatusResponse[" + str(self.nodeType) + "," + str(self.maxTcpSockets) + "," + str(self.currTcpSockets) + "," + str(self.maxDataSize) + "]"
   def visit (self, visitor, address):
      visitor.entityStatusResp(self, address)
class DiagnosticMessage:
   def __init__ (self, data, LogicalAddress=None, TargetAddress=None):
      self.Length = 4
      self.Type = 0x8001
      self.Name="DiagnosticMessage"
      Trace("parseMessage: DiagnosticMessage START")
      if LogicalAddress == None and TargetAddress == None:
         # hit when parsing an incoming message
         self.LogicalAddress = int(data[0] << 8 | data[1]) #TesterAddress
         self.TargetAddress  = int(data[2] << 8 | data[3])
         self.data = data[4:len(data)]
         self.Length += len(data)-4
         Trace("parseMessage: DiagnosticMessage len=" + str(self.Length))
      else:
         # used to construct a request
         self.LogicalAddress = LogicalAddress #TesterAddress
         self.TargetAddress  = TargetAddress
         self.data = data
         self.Length += len(data)
   def __str__ (self):
      return "DiagnosticMessage[" + binascii.hexlify(self.data) + "]"
   def visit (self, visitor, address):
      visitor.diagnosticResponse(self, address)
   def serialize (self):
      array = bytearray(self.Length)
      array[0] = (self.LogicalAddress >> 8) & 0xFF
      array[1] = (self.LogicalAddress >> 0) & 0xFF
      array[2] = (self.TargetAddress  >> 8) & 0xFF
      array[3] = (self.TargetAddress  >> 0) & 0xFF
      array[4:len(array)] = self.data
      return array
class DiagnosticMessageAck:
   def __init__ (self, stream):
      self.TargetAddress  = int(stream[0] << 8 | stream[1])
      self.LogicalAddress = int(stream[2] << 8 | stream[3]) #TesterAddress
      self.ACK = int(stream[4])
      self.Length = 5
      self.Type = 0x8002
      self.Name="DiagnosticMessageAck"
   def __str__ (self):
      return "DiagnosticMessageAck[" + str(self.LogicalAddress) + "," + str(self.TargetAddress) + "," + str(self.ACK) + "]"
   def visit (self, visitor, address):
      visitor.diagnosticAck(self, address)
class DiagnosticMessageNack:
   def __init__ (self, stream):
      self.TargetAddress  = int(stream[0] << 8 | stream[1])
      self.LogicalAddress = int(stream[2] << 8 | stream[3]) #TesterAddress
      self.NACK = int(stream[4])
      self.Length = 5
      self.Type = 0x8003
      self.Name="DiagnosticMessageNack"
   def __str__ (self):
      return "DiagnosticMessageNack[" + str(self.LogicalAddress) + "," + str(self.TargetAddress) + "," + str(self.NACK) + "]"
   def visit (self, visitor, address):
      visitor.diagnosticNack(self, address)
# pseudo-message to let the user know that the server is disconnected
class Disconnect:
   def __init__ (self):
      self.Type = 0xFFFF
      self.Length = 0
      self.Name="Disconnect"
      self.data=bytearray();
   def __str__ (self):
      return "Disconnect[]"
   def visit (self, visitor, address):
      return
   def getDefaultData(self):
      return bytearray([0x02, 0xFD, 0xFF, 0xFF, 0, 0, 0, 0])
# pseudo-message to let the user know that we ran into a timeout
class Timeout:
   def __init__ (self):
      self.Type = 0xFFFD
      self.Length = 0
      self.Name="Timeout"
   def __str__ (self):
      return "Timeout[]"
   def visit (self, visitor, address):
      return
   def getDefaultData(self):
      return bytearray([0x02, 0xFD, 0xFF, 0xFD, 0, 0, 0, 0])
messagemap = {
   0x0000 : GenericNack,
   0x0001 : VehicleIdentificationRequest,
   0x0002 : VehicleIdentificationRequestEID,
   0x0003 : VehicleIdentificationRequestVIN,
   0x0004 : VehicleAnnouncement,
   0x0005 : RoutingActivationRequest,
   0x0006 : RoutingActivationResponse,
   0x0007 : AliveCheckRequest,
   0x0008 : AliveCheckResponse,
   0x4001 : EntityStatusRequest,
   0x4002 : EntityStatusResponse,
   0x4003 : PowerModeRequest,
   0x4004 : PowerModeResponse,
   0x8001 : DiagnosticMessage,
   0x8002 : DiagnosticMessageAck,
   0x8003 : DiagnosticMessageNack,
   0xFFFF : Disconnect,
}
class Message:
   def __init__ (self, payload):
      self.ProtocolVersion = 0x02
      self.payload = payload
      self.Length = 8 + payload.Length #overall message length
   def __str__ (self):
      return str(self.payload)
   def name(self):
      return str(self.payload)
   def serialize (self):
      array = bytearray(self.Length)
      array[0] = self.ProtocolVersion
      array[1] = (~self.ProtocolVersion) & 0xFF
      array[2] = (self.payload.Type >> 8) & 0xFF
      array[3] = (self.payload.Type >> 0) & 0xFF
      array[4] = (self.payload.Length >> 24) & 0xFF
      array[5] = (self.payload.Length >> 16) & 0xFF
      array[6] = (self.payload.Length >> 8) & 0xFF
      array[7] = (self.payload.Length >> 0) & 0xFF
      array[8:len(array)] = self.payload.serialize()
      #Trace array
      return array
def parseMessage (stream):
   # parse header
   ProtocolVersion = stream[0]  #byte
   InverseProtocolVersion = stream[1]#byte
   PayloadType = int(stream[2] << 8 | stream[3]) #PayloadType
   Length = int(stream[4] << 24 | stream[5] << 16 | stream[6] << 8 | stream[7]) #uint32
   Trace("parseMessage: ProtocolVersion " + str(ProtocolVersion))
   Trace("parseMessage: PayloadType " + str(PayloadType))
   Trace("parseMessage: Length " + str(Length))
   #Trace hex(ProtocolVersion) + " " + hex(InverseProtocolVersion) + " " + hex(PayloadType) + " " + str(Length)
   
   # switch payload type
   payload = GenericNack(bytearray(1))
   if ProtocolVersion == (~InverseProtocolVersion & 0xFF):
      Trace("parseMessage: Inverse OK")
      if PayloadType in messagemap:
         payload = messagemap[PayloadType]
   Trace("parseMessage: found " + str(payload))
   
   return (Message(payload(stream[8:8+Length])), stream[8+Length:len(stream)])