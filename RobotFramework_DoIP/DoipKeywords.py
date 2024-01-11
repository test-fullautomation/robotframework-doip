from robot.api.deco import keyword
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from constants import (
    A_DOIP_CTRL,
    TCP_DATA_UNSECURED,
    UDP_DISCOVERY,
    A_PROCESSING_TIME,
    LINK_LOCAL_MULTICAST_ADDRESS,
    ActivationTypeDefault,
)

from doipclient import DoIPClient

class DoipKeywords(object):

    def __init__(self):
        self.debug = 0
        self.client = None

    @keyword("Connect To ECU")
    def connect_to_ecu(
        self,
        ecu_ip_address,
        ecu_logical_address,
        tcp_port=TCP_DATA_UNSECURED,
        udp_port=UDP_DISCOVERY,
        activation_type=ActivationTypeDefault,
        protocol_version=0x02,
        client_logical_address=0x0E00,
        client_ip_address=None,
        use_secure=False,
        auto_reconnect_tcp=False,
    ):
        """
        **Description:**

            Establishing a connection to an (ECU) within the context of automotive communication. 
       
        **Parameters:**

            * param ``ecu_ip_address`` (required): The IP address of the ECU to establish a connection. This should be a string representing an IPv4
                    address like "192.168.1.1" or an IPv6 address like "2001:db8::".
            * type ``ecu_ip_address``: str
            * param ``ecu_logical_address`` (required): The logical address of the ECU.
            * type ``ecu_logical_address``: int
            * param ``tcp_port`` (optional): The TCP port used for unsecured data communication (default is **TCP_DATA_UNSECURED**).
            * type ``tcp_port``: int
            * param ``udp_port`` (optional): The UDP port used for ECU discovery (default is **UDP_DISCOVERY**).
            * type ``udp_port``: int
            * param ``activation_type`` (optional): The type of activation, which can be the default value (ActivationTypeDefault) or a specific value based on application-specific settings.
            * type ``activation_type``: RoutingActivationRequest.ActivationType,
            * param ``protocol_version`` (optional): The version of the protocol used for the connection (default is 0x02).
            * type ``protocol_version``: int
            * param ``client_logical_address`` (optional): The logical address that this DoIP client will use to identify itself. Per the spec,
                    this should be 0x0E00 to 0x0FFF. Can typically be left as default.
            * type ``client_logical_address``: int   
            * param ``client_ip_address`` (optional): If specified, attempts to bind to this IP as the source for both UDP and TCP communication.
                    Useful if you have multiple network adapters. Can be an IPv4 or IPv6 address just like `ecu_ip_address`, though
                    the type should match.
            * type ``client_ip_address``: str
            * param ``use_secure`` (optional): Enables TLS. If set to True, a default SSL context is used. For more control, a preconfigured
                    SSL context can be passed directly. Untested. Should be combined with changing tcp_port to 3496.
            * type ``use_secure``: Union[bool,ssl.SSLContext]
            * param ``auto_reconnect_tcp`` (optional): Attempt to automatically reconnect TCP sockets that were closed by peer
            * type ``auto_reconnect_tcp``: bool
        
        **Return:**

            None
        
        **Usage:**
            
            # Explicitly specifies all establishing a connection 

            * Connect To ECU | 172.17.0.111 | ${1863} |
            * Connect To ECU | 172.17.0.111 | ${1863} | client_ip_address=172.17.0.5 | client_logical_address=${1895} |
            * Connect To ECU | 172.17.0.111 | ${1863} | client_ip_address=172.17.0.5 | client_logical_address=${1895} | activation_type=${0} |
        """
        try:
            self.client = DoIPClient(
                ecu_ip_address,
                ecu_logical_address,
                tcp_port=tcp_port,
                udp_port=udp_port,
                activation_type=activation_type,
                protocol_version=protocol_version,
                client_logical_address=client_logical_address,
                client_ip_address=client_ip_address,
                use_secure=use_secure,
                auto_reconnect_tcp=auto_reconnect_tcp,
            )

            logger.info(f"Connection established successfully. Target ECU: {ecu_ip_address} | Client: {client_logical_address}")
                
        except Exception as e:
            logger.error(f"An error occurred while connecting: {e}")
        
    
    @keyword("Send Diagnostic Message")
    def send_diagnostic_message(self, diagnostic_payload, timeout=A_PROCESSING_TIME):
        """
        **Description:**

            Send a raw diagnostic payload (ie: UDS) to the ECU.

        **Parameters:**

            * param ``diagnostic_payload``: UDS payload to transmit to the ECU
            * type ``diagnostic_payload``: bytearray
            * param ``timeout``: send diagnostic time out (default: A_PROCESSING_TIME)
            * type ``timeout``: int (s)

        **Return:**

            None

        **Exception:**

            raises IOError: DoIP negative acknowledgement received

        **Usage:**

            # Explicitly specifies all diagnostic message properties

            * Send Diagnostic Message | 1040 |
            * Send Diagnostic Message | 1040 | timeout=10 |
        """
        if self.client is not None:
            self.client.send_diagnostic(diagnostic_payload, timeout)
            logger.info(f"Send diagnostic message: {diagnostic_payload}")
        else:
            logger.warning(f"No active DoIP connection. Unable to send diagnostic message.")


    @keyword("Receive Diagnostic Message")
    def receive_diagnostic_message(self, timeout):
        """
        **Description:**

            Receive a raw diagnostic payload (ie: UDS) from the ECU.

        **Parameters:**

            * param ``timeout``: time waiting diagnostic message (default: None)
            * type ``timeout``: int (s)

        **Return:**

            None

        **Exception:**

            raises IOError: DoIP negative acknowledgement received

        **Usage:**

            # Explicitly specifies all diagnostic message properties

            * Receive Diagnostic Message |
            * Receive Diagnostic Message | timeout=10 |
        """
        if self.client is not None:
            resp = self.client.receive_diagnostic(timeout)
            logger.info(f"Receive diagnostic message: {resp}")
        else:
            logger.warning(f"No active DoIP connection. Unable to receive diagnostic message.")

    
    @keyword("Reconnect To Ecu")
    def reconnect_to_ecu(self, close_delay=A_PROCESSING_TIME):
        """
        **Description:**

            Attempts to re-establish the connection. Useful after an ECU reset

        **Parameters:**

            * param ``close_delay``: Time to wait between closing and re-opening socket (default: **A_PROCESSING_TIME**)
            * type ``close_delay``: int (s)

        **Return:**
            None

        **Exception:**

            raises ConnectionRefusedError: DoIP negative acknowledgement received

        **Usage:**

            # Explicitly specifies all diagnostic message properties 

            * Reconnect To Ecu |
            * Receive Diagnostic Message | timeout=10 |
        """
        if self.client is not None:
            self.client.reconnect(close_delay)
        else:
            logger.warning(f"No active DoIP connection. Unable to close connection.")

    @keyword("Disconnect")
    def disconnect(self):
        """
        **Description:**

            Close the DoIP client

        **Parameters:**

            None

        **Return:**

            None

        **Exception:**

            None

        **Usage:**

            # Explicitly specifies all diagnostic message properties

            * Disconnect 
        """
        if self.client is not None:
            self.client.close() 
        else:
            logger.warning(f"No active DoIP connection. Unable to close connection.")
        


    @keyword("Await Vehicle Annoucement")
    def await_vehicle_announcement(
        self,
        udp_port=UDP_DISCOVERY,
        timeout=None,
        ipv6=False,
        source_interface=None,
        sock=None,
    ):
        """
        **Description:**

            When an ECU first turns on, it's supposed to broadcast a Vehicle Announcement Message over UDP 3 times
            to assist DoIP clients in determining ECU IP's and Logical Addresses. Will use an IPv4 socket by default,
            though this can be overridden with the `ipv6` parameter.

        **Parameters:**

            * param ``udp_port``: The UDP port to listen on. Per the spec this should be 13400, but some VM's use a custom
            * one.
            * type ``udp_port``: int, optional
            * param ``timeout``: Maximum amount of time to wait for message
            * type ``timeout``: float, optional
            * param ``ipv6``: Bool forcing IPV6 socket instead of IPV4 socket
            * type ``ipv6``: bool, optional
            * param ``source_interface``: Interface name (like "eth0") to bind to for use with IPv6. Defaults to None which
                will use the default interface (which may not be the one connected to the ECU). Does nothing for IPv4,
                which will bind to all interfaces uses INADDR_ANY.
            * type ``source_interface``: str, optional

        **Return:**

            * return: IP Address of ECU and VehicleAnnouncementMessage object
            * rtype: tuple

        **Exception:**

            raises TimeoutError: If vehicle announcement not received in time

        **Usage:**

            # Explicitly specifies all diagnostic message properties

            * Await Vehicle Annoucement 
            * Await Vehicle Annoucement | timeout=10
        """
        try:
            address, announcement = DoIPClient.await_vehicle_announcement(udp_port, timeout, ipv6, source_interface, sock)
            logical_address = announcement.logical_address
            ip, port = address
            logger.info(f"Target ECU IP: {ip}, Logical ECU Address: {logical_address}")
            return ip, port, logical_address
        except Exception as e:
            logger.error(f"An error occurred while sending a VehicleIdentificationRequest: {e}")
        

    @keyword("Get Entity")
    def get_entity(
        self,
        ecu_ip_address="255.255.255.255", 
        protocol_version=0x02, 
        eid=None, 
        vin=None,
    ):
        """
        **Description:**

            Sends a VehicleIdentificationRequest and awaits a VehicleIdentificationResponse from the ECU,
            either with a specified VIN, EIN, or nothing. Equivalent to the request_vehicle_identification() method
            but can be called without instantiation

        **Parameters:**

            * param ``udp_port``: The UDP port to listen on. Per the spec this should be 13400, but some VM's use a custom
            * one.
            * type ``udp_port``: int, optional
            * param ``timeout``: Maximum amount of time to wait for message
            * type ``timeout``: float, optional
            * param ``ipv6``: Bool forcing IPV6 socket instead of IPV4 socket
            * type ``ipv6``: bool, optional
            * param ``source_interface``: Interface name (like "eth0") to bind to for use with IPv6. Defaults to None which
                will use the default interface (which may not be the one connected to the ECU). Does nothing for IPv4,
                which will bind to all interfaces uses INADDR_ANY.
            * type ``source_interface``: str, optional

        **Return:**

            * return: IP Address of ECU and VehicleAnnouncementMessage object
            * rtype: tuple

        **Exception:**

            raises TimeoutError: If vehicle announcement not received in time

        **Usage:**

            * Get Entity |
            * Get Entity | ecu_ip_address=172.17.0.111 |
            * Get Entity | ecu_ip_address=172.17.0.111 | protocol_version=0x02
        """
        try:
            address, announcement = DoIPClient.get_entity(ecu_ip_address, protocol_version, eid, vin)
            logical_address = announcement.logical_address
            ip, port = address
            logger.info(f"Target ECU IP: {ip}, Logical ECU Address: {logical_address}, port: {port}")
        except Exception as e:
            logger.error(f"An error occurred while get entity: {e}")

    @keyword("Request Entity Status")
    def request_entity_status(self):
        """
        **Description:**

            Request that the ECU send a DoIP Entity Status Response

        **Parameters:**

            None

        **Return:**

            None

        **Exception:**

            None

        **Usage:**

            * Request Entity Status 
        """
        if self.client is not None:
            resp = self.client.request_entity_status()
            logger.info(f"Entity response payload_type: {resp.payload_type}")
        else:
            logger.warning(f"No active DoIP connection. Unable to request entity status.")
    
    @keyword("Request Vehicle Identification")
    def request_vehicle_identification(
        self, 
        eid=None,
        vin=None,
    ):
        """
        **Description:**

            Sends a VehicleIdentificationRequest and awaits a VehicleIdentificationResponse from the ECU, either with a specified VIN, EIN,
            or nothing

        **Parameters:**

            :param eid: EID of the Vehicle
            :type eid: bytes, optional
            :param vin: VIN of the Vehicle
            :type vin: str, optional

        **Return:**

            None

        **Exception:**

            None

        **Usage:**

            * Request Vehicle Identification 
            * Request Vehicle Identification | eid=0x123456789abc
            * Request Vehicle Identification | vin=0x123456789abc
        """
        if self.client is not None:
            if eid is not None:
                resp = self.client.request_vehicle_identification(eid)
            elif vin is not None:
                resp = self.client.request_vehicle_identification(vin)
            else:
                resp = self.client.request_vehicle_identification()

            logger.info(f"eid: {resp.eid}")
            logger.info(f"vin: {resp.vin}")
            logger.info(f"gid: {resp.gid}")
            logger.info(f"logical_address: {resp.logical_address}")
            logger.info(f"vin_sync_status: {resp.vin_sync_status}")
        else:
            logger.warning(f"No active DoIP connection. Unable to request vehicle identification.")


    @keyword("Request Alive Check")
    def request_alive_check(self):
        """
        **Description:**

            Request that the ECU send an alive check response

        **Parameters:**

           None

        **Return:**

            None

        **Exception:**

            None

        **Usage:**

            * Request Vehicle Identification 
            * Request Vehicle Identification | eid=0x123456789abc
            * Request Vehicle Identification | vin=0x123456789abc
        """
        if self.client is not None:
            resp = self.client.request_alive_check()
            logger.info(f"source_address: {resp.source_address}")
        else:
            logger.warning(f"No active DoIP connection. Unable to request alive.")

    @keyword("Request Routing Activation")
    def request_activation(
        self,
        activation_type, 
        vm_specific=None,
        disable_retry=False,
    ):
        """
        **Description:**

            Requests a given activation type from the ECU for this connection using payload type 0x0005

        **Parameters:**

            * param ``activation_type`` (required): The type of activation to request - see Table 47 ("Routing
                                        activation request activation types") of ISO-13400, but should generally be 0 (default)
                                        or 1 (regulatory diagnostics)
            * type ``activation_type``: RoutingActivationRequest.ActivationType
            * param ``vm_specific`` (optional): 4 byte long int
            * type ``vm_specific``: int, optional
            * param ``disable_retry``: Disables retry regardless of auto_reconnect_tcp flag. This is used by activation
                                        requests during connect/reconnect.
            * type ``disable_retry``: bool, optional
 
        **Return:**

            None

        **Exception:**

            None

        **Usage:**

            * Request Routing Activation | ${0x02}
            * Request Routing Activation | vm_specific=
            * Request Routing Activation | vin=0x123456789abc
        """
        if self.client is not None:
            resp = self.client.request_activation(self, activation_type, vm_specific, disable_retry)
            logger.info(f"client_logical_address: {resp.client_logical_address}")
            logger.info(f"logical_address: {resp.logical_address}")
        else:
            logger.warning(f"No active DoIP connection. Unable to request routing activation.")

    @keyword("Request Diagnostic Power Mode")
    def request_diagnostic_power_mode(self):
        """
        **Description:**

            Request that the ECU send a Diagnostic Power Mode response

        **Parameters:**

           None

        **Return:**

            None

        **Exception:**

            None

        **Usage:**

            * Request Diagnostic Power Mode
        """
        if self.client is not None:
            resp = self.client.request_diagnostic_power_mode()
            logger.info(f"diagnostic_power_mode: {resp.diagnostic_power_mode}")
        else:
            logger.warning(f"No active DoIP connection. Unable to request diagnostic power mode.")