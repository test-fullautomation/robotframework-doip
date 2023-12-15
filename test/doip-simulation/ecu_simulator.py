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
# File: ecu_simulator.py
#
# Initially created by Tri Mai (RBVH/ECM51) / December 2023.
#
# Description:
#
# Defines a simple implementation of ECUs for vehicle communication using the DoIP
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
from enum import Enum
from doipclient.messages import AliveCheckResponse
import struct
from ecu_factory import AbstractECU
from doipclient.messages import AliveCheckResponse, DiagnosticPowerModeResponse, RoutingActivationResponse

# Define IP and port information for positive and negative ECUs
POSITIVE_ECU_IP = "172.17.0.5"
POSITIVE_TCP_PORT = 13400
POSITIVE_UDP_PORT = 13400

NEGATIVE_ECU_IP = "172.17.0.5"
NEGATIVE_TCP_PORT = 12346
NEGATIVE_UDP_PORT = 12347

class ECUType(Enum):
    POSITIVE_ECU = 0,
    NEGATIVE_ECU = 1

# Positive ECU class, inheriting from AbstractECU
class PositiveECU(AbstractECU):
    def __init__(self, ecu_type, ip_address, tcp_port, udp_port):
        super().__init__(ecu_type, ip_address, tcp_port, udp_port)
        # Initialize specific attributes for positive ECU 
        self._ecu_logical_address = 3584
        self._client_logical_address = 3584
        self._logical_address = 55
        self._response_code = RoutingActivationResponse.ResponseCode.Success
        self._diagnostic_power_mode = DiagnosticPowerModeResponse.DiagnosticPowerMode.Ready
        self._node_type = 1
        self._max_concurrent_sockets = 16
        self._currently_open_sockets = 1
        self._max_data_size = None

class NegativeECU(AbstractECU):
    def __init__(self, ecu_type, ip_address, tcp_port, udp_port):
        super().__init__(ecu_type, ip_address, tcp_port, udp_port)
        # Initialize specific attributes for negative ECU
        self._ecu_logical_address = 0
        self._client_logical_address = 0
        self._logical_address = 0
        self._response_code = RoutingActivationResponse.ResponseCode.DeniedAllSocketsRegisteredActive
        self._diagnostic_power_mode = DiagnosticPowerModeResponse.DiagnosticPowerMode.NotSupported
        self._node_type = 0
        self._max_concurrent_sockets = 0
        self._currently_open_sockets = 0
        self._max_data_size = 0

class ECUFactory:
    def create_ecu(self, ecu_type, ip_address, tcp_port, udp_port):
        ecu_type = ECUType(ecu_type)
        if ecu_type == ECUType.POSITIVE_ECU:
            return PositiveECU(ecu_type, ip_address, tcp_port, udp_port)
        elif ecu_type == ECUType.NEGATIVE_ECU:
            return NegativeECU(ecu_type, ip_address, tcp_port, udp_port)
        else:
            raise ValueError("Invalid ECU type")

if __name__ == "__main__":
    # Create and start instances of different ECUs using the factory pattern and abstract class
    factory = ECUFactory()

    positive_ecu = factory.create_ecu(ECUType.POSITIVE_ECU, POSITIVE_ECU_IP, POSITIVE_TCP_PORT, POSITIVE_UDP_PORT)
    negative_ecu = factory.create_ecu(ECUType.NEGATIVE_ECU, NEGATIVE_ECU_IP, NEGATIVE_TCP_PORT, NEGATIVE_UDP_PORT)
    # Start positive and negative ECUs
    positive_ecu.start()
    negative_ecu.start()
