from robot.api.deco import keyword
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from doipclient import DoIPClient

class DoipKeywords(object):

    def __init__(self):
        address, announcement = DoIPClient.get_entity()
        logical_address = announcement.logical_address
        ip, port = address
        print(ip, port, logical_address)

        self.ip = ip
        self.logical_address = logical_address
        logger.info(f"IP: {ip} ")

    @keyword
    def connect(self):
        pass
    
    @keyword
    def send_diagnostic(self):
        pass
    
    @keyword
    def receive_diagnostic(self):
        pass

    @keyword
    def reconnect(self):
        pass

    @keyword
    def disconnect(self):
        pass

    @keyword("Await Vehicle Annoucement")
    def await_vehicle_announcement(self):
        address, announcement = DoIPClient.await_vehicle_announcement()
        print(address)
        logical_address = announcement.logical_address
        ip, port = address
        print(ip, port, logical_address)
        return ip, port, logical_address

    @keyword("Get Entity")
    def get_entity(self):

        address, announcement = DoIPClient.get_entity()
        ip, port = address
        logical_address = announcement.logical_address
        client = DoIPClient(ip, logical_address)
        
        return client

    @keyword("Request Entity Status")
    def request_entity_status(self):
        client = DoIPClient(self.ip, self.logical_address)
        resp = client.request_entity_status()
        return resp
    
    @keyword("Request Vehicle Identification")
    def request_vehicle_identification(self, eid=None, vin=None):
        client = DoIPClient(self.ip, self.logical_address)
        resp = client.request_vehicle_identification(eid, vin)
        return resp

    @keyword("Request Alive Check")
    def request_alive_check(self):
        client = DoIPClient(self.ip, self.logical_address)
        resp = client.request_alive_check()
        return resp
    
    @keyword("Request Routing Activation")
    def request_activation(self, activation_type, vm_specific, disable_retry):
        client = DoIPClient(self.ip, self.logical_address)
        resp = client.request_activation(self, activation_type, vm_specific, disable_retry)
        return resp

    @keyword("Diagnostic Message")
    def send_diagnostic(self, diagnostic_payload, timeout):
        client = DoIPClient(self.ip, self.logical_address)
        resp = client.send_diagnostic(self, diagnostic_payload, timeout)
        return resp

    @keyword("Request Diagnostic Power Mode")
    def request_diagnostic_power_mode(self):
        client = DoIPClient(self.ip, self.logical_address)
        resp = client.request_diagnostic_power_mode()
        return resp