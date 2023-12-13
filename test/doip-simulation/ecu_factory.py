#  Copyright 2020-2023 Robert Bosch GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# *******************************************************************************
#
# File: ecu_factory.py
#
# Initially created by Tri Mai (RBVH/ECM51) / December 2023.
#
# Description:
#
#
# History:
#
# 13.12.2023 / V 0.1 / Tri Mai
# - Initialize
#
# *******************************************************************************

from abc import ABC, abstractmethod
import socket
import threading
import doipclient.messages as doip_message
from doipclient.client import Parser

import struct

class AbstractECU(ABC):
   def __init__(self, ecu_type, ip_address, tcp_port, udp_port):
      # Initialize ECU attributes with default values
      self.ecu_type = ecu_type
      self.ip_address = ip_address
      self.tcp_port = tcp_port
      self.udp_port = udp_port
      self.tcp_socket = None
      self.udp_socket = None
      # Set default values for various ECU properties
      # These values might be placeholders and can be updated based on your actual requirements
      self._ecu_logical_address = 3584
      self._client_logical_address = 3584
      self._logical_address = 55
      self._response_code = doip_message.RoutingActivationResponse.ResponseCode.Success
      self._diagnostic_power_mode = doip_message.DiagnosticPowerModeResponse.DiagnosticPowerMode.Ready
      self._node_type = 1
      self._max_concurrent_sockets = 16
      self._currently_open_sockets = 1
      self._max_data_size = None
      self._vin = '19676527011956855057'
      self._eid = b'11111'
      self._gid = b'222222'
      self._further_action_required = doip_message.VehicleIdentificationResponse.FurtherActionCodes.NoFurtherActionRequired
      self._vin_sync_status = doip_message.VehicleIdentificationResponse.SynchronizationStatusCodes.Synchronized

   def process_data(self, data):
      # Process DoIP messages received from clients
      parser = Parser()
      response = parser.read_message(data)
      print("Received DoIP Message. Type: 0x{:X}, Payload Size: {} bytes, Payload: {}".format(
                     parser.payload_type,
                     parser.payload_size,
                     " ".join(f"{byte:02X}" for byte in parser.payload),
            ))
      data = bytearray()
      # Handle different types of DoIP messages and generate appropriate responses
      if type(response) == doip_message.GenericDoIPNegativeAcknowledge:
         raise IOError(
            f"DoIP Negative Acknowledge. NACK Code: {response.nack_code}"
         )
      elif type(response) == doip_message.AliveCheckRequest:
         return self.generate_alive_check_response(self._ecu_logical_address)
      elif type(response) == doip_message.DiagnosticPowerModeRequest:
         return self.generate_diagnostic_power_mode_response(self._diagnostic_power_mode)
      elif type(response) == doip_message.DoipEntityStatusRequest:
         return self.generate_entity_status_response(self._node_type, self._max_concurrent_sockets, self._currently_open_sockets, self._max_data_size)
      elif type(response) == doip_message.RoutingActivationRequest:
         return self.generate_routing_activation_response(self._client_logical_address, self._logical_address, self._response_code)
      elif type(response) == doip_message.VehicleIdentificationRequest \
         or type(response) == doip_message.VehicleIdentificationRequestWithEID \
         or type(response) == doip_message.VehicleIdentificationRequestWithVIN:
         return self.generate_vehicle_idenfication_response(self._vin, self._ecu_logical_address, self._eid, self._gid, self._further_action_required, self._vin_sync_status)

   def start(self):
      # Create TCP socket
      self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.tcp_socket.bind((self.ip_address, self.tcp_port))
      self.tcp_socket.listen(5)

      # Create UDP socket
      self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.udp_socket.bind((self.ip_address, self.udp_port))

      # Start listening on separate threads
      tcp_thread = threading.Thread(target=self.listen_tcp)
      udp_thread = threading.Thread(target=self.listen_udp)

      tcp_thread.start()
      udp_thread.start()

   def listen_tcp(self):
      # Listen for incoming TCP connections
      print(f'TCP Server {self.ip_address} listening on port {self.tcp_port}')
      while True:
         client_socket, addr = self.tcp_socket.accept()
         print(f'Accepted connection from {addr}')
         thread = threading.Thread(target=self.handle_tcp_client, args=(client_socket,))
         thread.start()

   def handle_tcp_client(self, client_socket):
      # Handle communication with a TCP client
      data = client_socket.recv(1024)
      while data:
         print(f'TCP Data received: {data}')
         # Process received data and generate a response
         response_data = self.process_data(data)
         thread = threading.Thread(target=self.handle_tcp_client, args=(client_socket,))
         thread.start()
         client_socket.sendall(response_data)  # Send response through the TCP socket
         data = client_socket.recv(1024)
      client_socket.close()

   def listen_udp(self):
      # Listen for incoming UDP messages
      print(f'UDP Server {self.ip_address} listening on port {self.udp_port}')
      while True:
         data, addr = self.udp_socket.recvfrom(1024)
         print(f'UDP Data received from {addr}: {data}')
         # Process received data and generate a response
         response_data = self.process_data(data)
         self.udp_socket.sendto(response_data, addr)  # Send response through the UDP socket

   def generate_doip_message(self, response, protocol_version = 0x02):
      # Generate a DoIP message from a given response
      payload_type = response.payload_type
      payload_data = response.pack()
      doip_message = struct.pack(
         "!BBHL",
         protocol_version,
         0xFF ^ protocol_version,
         payload_type,
         len(payload_data),
      )
      doip_message += payload_data
      return doip_message

   def generate_alive_check_response(self, source_address, protocol_version = 0x02):
      # Generate an Alive Check Response
      response = doip_message.AliveCheckResponse(source_address)
      return self.generate_doip_message(response, protocol_version)

   def generate_diagnostic_power_mode_response(self, diagnostic_power_mode = doip_message.DiagnosticPowerModeResponse.DiagnosticPowerMode.Ready, protocol_version = 0x02):
      # Generate a Diagnostic Power Mode Response
      response = doip_message.DiagnosticPowerModeResponse(diagnostic_power_mode)
      return self.generate_doip_message(response, protocol_version)

   def generate_entity_status_response(self, node_type, max_concurrent_sockets, currently_open_sockets, max_data_size, protocol_version = 0x02):
      # Generate an Entity Status Response
      response = doip_message.EntityStatusResponse(node_type, max_concurrent_sockets, currently_open_sockets, max_data_size)
      return self.generate_doip_message(response, protocol_version)

   def generate_routing_activation_response(self, client_logical_address, logical_address, response_code, reserved = 0, vm_specific = None, protocol_version = 0x02):
      # Generate a Routing Activation Response
      response = doip_message.RoutingActivationResponse(client_logical_address, logical_address, response_code, reserved, vm_specific)
      return self.generate_doip_message(response, protocol_version)

   def generate_vehicle_idenfication_response(self, vin, logical_address, eid, gid, further_action_required, vin_sync_status, protocol_version = 0x02):
      # Generate a Vehicle Identification Response
      response = doip_message.VehicleIdentificationResponse(vin, logical_address, eid, gid, further_action_required, vin_sync_status)
      return self.generate_doip_message(response, protocol_version)


