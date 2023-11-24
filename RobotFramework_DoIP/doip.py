from doipclient import DoIPClient
from doipclient.messages import *
from doipclient.constants import *
from enum import Enum
from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import keyword

class DoIP():
    def __init__(self, tcp_port, udp_port, _activation_type = RoutingActivationRequest.ActivationType.Default, protocol_version = 0x02, use_secure = False, auto_reconnect_tcp = False):
        self._tcp_port = tcp_port
        self._udp_port = udp_port
        self._activation_type = activation_type
        self._protocol_version = protocol_version
        self._use_secure = use_secure
        self._auto_reconnect_tcp = auto_reconnect_tcp
        self.doip = None

    @keyword
    def connect(self, ecu_ip_address, ecu_logical_address, activation_type):
        try:
            self.doip = DoIPClient(ecu_ip_address, ecu_logical_address, self._tcp_port, self._udp_port, self._activation_type, self._protocol_version, client_ip_address, self._use_secure)
        except Exception as ex:
            raise AssertionError("Unable to create conection. Exception: %s" % ex)

    @keyword
    def reconnect(self, close_delay=A_PROCESSING_TIME):
        try:
            self.doip.reconnect(close_delay)
        except Exception as ex:
            raise AssertionError("Failed to reconnect. Exception: %s" %ex)

    @keyword
    def disconnect(self):
        self.doip.close()
        self.doip = None


    @keyword
    def request_activation(self, vm_specific = None, disable_retry = False):
        try:
            result = self.doip.request_activation(self._activation_type, vm_specific, disable_retry)
        except Exception as ex:
            raise AssertionError("Failed to request activation. Exception: %s" %ex)

    @keyword
    def request_vehicle_identification(self, eid=None, vin=None):
        try:
            result = self.doip.request_vehicle_identification(eid, vin)
        except Exception as ex:
            raise AssertionError("Failed to request vehicle identification. Exception: %s" %ex)

    @keyword
    def request_alive_check(self):
        try:
            result = self.doip.request_alive_check()
        except Exception as ex:
            raise AssertionError("Failed to request alive check. Exception: %s" %ex)

    @keyword
    def request_diagnostic_power_mode(self):
        try:
            result = self.doip.request_diagnostic_power_mode()
        except Exception as ex:
            raise AssertionError("Failed to request diagnostic power mode. Exception: %s" %ex)

    @keyword
    def request_entity_status(self):
        try: 
            result = self.doip.request_entity_status()
        except Exception as ex:
            raise AssertionError("Failed to request entity status. Exception: %s" %ex)

    @keyword
    def send_diagnostic(self, diagnostic_payload, timeout=A_PROCESSING_TIME):
        try:
            result = self.doip.send_diagnostic()
        except Exception as ex:
            raise AssertionError("Failed to send diagnostic message. Exception: %s" %ex)

    @keyword
    def receive_diagnostic(self, timeout=None):
        try:
            result = self.doip.receive_diagnostic(timeout)
        except Exception as ex:
            raise AssertionError("Failed to receive diagnostic message. Exception: %s" %ex)


class ECU():
    def __init__(self, ecu_ip_address, ecu_logical_address, _activation_type = RoutingActivationRequest.ActivationType.Default):
        self._ecu_ip_address = ecu_ip_address
        self._ecu_logical_address = ecu_logical_address
        self._activation_type = _activation_type

class Client():
    def __init__(self, client_ip_address, client_logical_address):
        self._client_ip_address = client_ip_address
        self._client_logical_address = client_logical_address