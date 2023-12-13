from abc import ABC, abstractmethod
import socket
import threading
from enum import Enum
from doipclient.messages import AliveCheckResponse
import struct
from ecu_factory import AbstractECU
from doipclient.messages import AliveCheckResponse, DiagnosticPowerModeResponse, RoutingActivationResponse

POSITIVE_ECU_IP = "172.17.0.5"
POSITIVE_TCP_PORT = 13400
POSITIVE_UDP_PORT = 13400

NEGATIVE_ECU_IP = "172.17.0.5"
NEGATIVE_TCP_PORT = 12346
NEGATIVE_UDP_PORT = 12347

class ECUType(Enum):
    POSITIVE_ECU = 0,
    NEGATIVE_ECU = 1

class PositiveECU(AbstractECU):
    def __init__(self, ecu_type, ip_address, tcp_port, udp_port):
        super().__init__(ecu_type, ip_address, tcp_port, udp_port)
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

    positive_ecu.start()
    negative_ecu.start()
