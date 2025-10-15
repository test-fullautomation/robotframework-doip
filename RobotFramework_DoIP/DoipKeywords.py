from robot.api.deco import keyword
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from RobotFramework_DoIP.constants import (
    A_DOIP_CTRL,
    TCP_DATA_UNSECURED,
    UDP_DISCOVERY,
    A_PROCESSING_TIME,
    LINK_LOCAL_MULTICAST_ADDRESS,
    ActivationTypeDefault,
)

from doipclient import DoIPClient
from doipclient import messages
import binascii

class DoipDeviceManager(object):
    def __init__(self):
        self.doip_device = {}

    def is_device_exist(self, name):
        if name in self.doip_device:
            return True
        return False

class DoipDevice(object):
    def __init__(self):
        self.name = None
        self.client = None
        self.debug = 0

class DoipKeywords(object):

    ROBOT_LIBRARY_DOC_FORMAT = 'reST'
    ROBOT_AUTO_KEYWORDS      = False # only decorated methods are keywords
    ROBOT_LIBRARY_VERSION    = "0.1.6" # TODO: get this from version.py
    # ROBOT_LIBRARY_SCOPE    = to be defined

    def __init__(self):
        self.doip_device_manager = DoipDeviceManager()

    def __device_check(self, device_name):
        if self.doip_device_manager.is_device_exist(device_name):
            doip_device = self.doip_device_manager.doip_device[device_name]
            return doip_device
        else:
            raise ValueError(f"Device with name '{device_name}' does not exists. Please use keyword \"Connect To ECU\" to create a new one.")

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
        device_name = "default"
    ):
        """
**Description:**

Establishing a **DoIP** connection to an (ECU) within the context of automotive communication.

**Parameters:**

* ``ecu_ip_address`` (required, type: ``str``): The IP address of the ECU to establish a connection.
  This should be a string representing an IPv4 address like ``192.168.1.1`` or an IPv6 address like ``2001:db8::``.
* ``ecu_logical_address`` (required, type: *any*): The logical address of the ECU.
* ``tcp_port`` (optional, default: ``TCP_DATA_UNSECURED``, type: ``int``): The TCP port used for unsecured data communication.
* ``udp_port`` (optional, default: ``UDP_DISCOVERY``, type: ``int``): The UDP port used for ECU discovery.
* ``activation_type`` (optional, type: ``RoutingActivationRequest.ActivationType``): The type of activation, which can be
  the default value (``ActivationTypeDefault``) or a specific value based on application-specific settings.
* ``protocol_version`` (optional, default: ``0x02``, type: ``int``): The version of the protocol used for the connection.
* ``client_logical_address`` (optional, type: ``int``): The logical address that this **DoIP** client will use to identify itself. Per the spec,
  this should be ``0x0E00`` to ``0x0FFF``. Can typically be left as default.
* ``client_ip_address`` (optional, type: ``str``): If specified, attempts to bind to this IP as the source for both
  UDP and TCP communication. Useful if you have multiple network adapters. Can be an **IPv4** or **IPv6** address just like
  ``ecu_ip_address``, though the type should match.
* ``use_secure`` (optional, type: ``Union[bool,ssl.SSLContext]``): Enables **TLS**. If set to ``True``, a default SSL context is used. For more control, a preconfigured
  SSL context can be passed directly. Untested. Should be combined with changing tcp_port to 3496.
* ``auto_reconnect_tcp`` (optional, type: ``bool``): Attempt to automatically reconnect TCP sockets that were closed by peer.
* ``device_name`` (optional, type: ``str``): Name of **DoIP** device.

**Return:**

None

**Exception:**

raises ``ConnectionError: Failed to establish a DoIP connection``

**Usage:**

Explicitly specifies all establishing a connection

* ``Connect To ECU | 172.17.0.111 | 1863 |``
* ``Connect To ECU | 172.17.0.111 | 1863 | client_ip_address=172.17.0.5 | client_logical_address=1895 |``
* ``Connect To ECU | 172.17.0.111 | 1863 | client_ip_address=172.17.0.5 | client_logical_address=1895 | activation_type=0 |``
        """
        try:
            if self.doip_device_manager.is_device_exist(device_name):
                raise ValueError(f"Device with name '{device_name}' already exists.")

            if isinstance(ecu_logical_address, str):
                ecu_logical_address = int(ecu_logical_address)

            if isinstance(client_logical_address, str):
                client_logical_address = int(client_logical_address)

            if isinstance(ecu_ip_address, str):
                ecu_ip_address = ecu_ip_address.strip()

            if isinstance(client_ip_address, str):
                client_ip_address = client_ip_address.strip()

            client = DoIPClient(
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
            doip_device = DoipDevice()
            doip_device.client = client
            self.doip_device_manager.doip_device[device_name] = doip_device

            logger.info(f"Connection established successfully. Device: {device_name} | Target ECU: {ecu_ip_address} | Client: {client_logical_address}")
                
        except Exception as e:
            error_message = f"An error occurred while connecting: {e}"
            raise ConnectionError(error_message)

    @keyword("Send Diagnostic Message")
    def send_diagnostic_message(self, diagnostic_payload, timeout=A_PROCESSING_TIME, device_name = "default", suppress_exceptions=False):
        """
**Description:**

Send a raw diagnostic payload (ie: **UDS**) to the ECU.

**Parameters:**

* ``diagnostic_payload`` (type: ``str``): UDS payload to transmit to the ECU
* ``timeout`` (type: ``int`` (s)): send diagnostic time out (default: ``A_PROCESSING_TIME``)
* ``device_name`` (optional, type: ``str``): Name of **DoIP** device

**Return:**

None

**Exception:**

* raises ``ConnectionRefusedError: DoIP connection attempt failed``
* raises ``IOError: DoIP negative acknowledgement received``

**Usage:**

Explicitly specifies all diagnostic message properties

* ``Send Diagnostic Message | 1040 |``
* ``Send Diagnostic Message | 1040 | timeout=10 |``
        """
        doip_device = self.__device_check(device_name)

        if doip_device.client is None:
            error_message = f"No active DoIP connection. Unable to send diagnostic message."
            logger.error(error_message)
            raise ConnectionRefusedError(error_message)
            
        try:
            # Convert string to byte array
            msg = bytes.fromhex(diagnostic_payload)
            doip_device.client.send_diagnostic(msg, timeout)
            logger.info(f"Send diagnostic message: {diagnostic_payload}")
        except Exception as e:
            error_message = f"An error occurred while sending diagnostic message: {e}"
            logger.error(error_message)
            if not suppress_exceptions:
                raise IOError(error_message)

    @keyword("Receive Diagnostic Message")
    def receive_diagnostic_message(self, timeout=None, device_name = "default"):
        """
**Description:**

Receive a raw diagnostic payload (ie: **UDS**) from the ECU.

**Parameters:**

* ``timeout`` (optional, default: ``None``, type: ``int`` (s)): time waiting diagnostic message.
* ``device_name`` (optional, type: ``str``): Name of DoIP device

**Return:**

None

**Exception:**

* raises ``ConnectionRefusedError: DoIP connection attempt failed``
* raises ``IOError: DoIP negative acknowledgement received``

**Usage:**

Explicitly specifies all diagnostic message properties

* ``Receive Diagnostic Message |``
* ``Receive Diagnostic Message | timeout=10 |``
        """
        doip_device = self.__device_check(device_name)

        if doip_device.client is None:
            error_message = f"No active DoIP connection. Unable to receive diagnostic message."
            logger.error(error_message)
            raise ConnectionRefusedError(error_message)
        
        try:
            resp = doip_device.client.receive_diagnostic(timeout)
            # Convert the received byte data to a hexadecimal string
            hex_string_data = binascii.hexlify(resp).decode('utf-8')
            logger.info(f"Receive diagnostic message: {hex_string_data}")
            return hex_string_data
        except Exception as e:
            error_message = f"An error occurred while receiving diagnostic message: {e}"
            raise IOError(error_message)
    
    @keyword("Reconnect To Ecu")
    def reconnect_to_ecu(self, close_delay=A_PROCESSING_TIME, device_name = "default"):
        """
**Description:**

Attempts to re-establish the connection. Useful after an ECU reset

**Parameters:**

* ``close_delay`` (type: ``int`` (s), default: ``A_PROCESSING_TIME``): Time to wait between closing and re-opening socket.
* ``device_name`` (optional, type: ``str``): Name of DoIP device

**Return:**

None

**Exception:**

raises ``ConnectionRefusedError: DoIP connection attempt failed``

**Usage:**

Explicitly specifies all diagnostic message properties

* ``Reconnect To Ecu |``
* ``Reconnect To Ecu | close_delay=10 |``
        """
        doip_device = self.__device_check(device_name)

        if doip_device.client is None:
            error_message = f"No active DoIP connection. Unable to reconnect connection."
            logger.error(error_message)
            raise ConnectionRefusedError(error_message)
        
        try:
            doip_device.client.reconnect(close_delay)
        except Exception as e:
            error_message = f"Unable to reconnect connection: {e}"
            raise ConnectionRefusedError(error_message)

    @keyword("Disconnect")
    def disconnect(self, device_name = "default"):
        """
**Description:**

Close the **DoIP** client

**Parameters:**

* param ``device_name`` (optional, type: ``str``): Name of **DoIP** device

**Return:**

None

**Exception:**

* raises ``ConnectionRefusedError: DoIP connection attempt failed``
* raises ``ConnectionAbortedError: close DoIP connection aborted``

**Usage:**

Explicitly specifies all diagnostic message properties

* ``Disconnect``
        """
        doip_device = self.__device_check(device_name)

        if doip_device.client is None:
            error_message = f"No active DoIP connection. Unable to close connection."
            logger.error(error_message)
            raise ConnectionRefusedError(error_message)

        try:
            doip_device.client.close() 
        except Exception as e:
            error_message = f"Unable to clone connection: {e}"
            raise ConnectionAbortedError(error_message)

        
    @keyword("Await Vehicle Annoucement")
    def await_vehicle_announcement(
        self,
        udp_port=UDP_DISCOVERY,
        timeout=None,
        ipv6=False,
        source_interface=None,
        sock=None,
        device_name = "default"
    ):
        """
**Description:**

When an ECU first turns on, it's supposed to broadcast a Vehicle Announcement Message over UDP 3 times
to assist **DoIP** clients in determining ECU IP's and Logical Addresses. Will use an IPv4 socket by default,
though this can be overridden with the ``ipv6`` parameter.

**Parameters:**

* ``udp_port`` (optional, type: ``int``): The UDP port to listen on. Per the spec this should be ``13400``, but some VM's use a custom one.
* ``timeout`` (optional, type: ``float``): Maximum amount of time to wait for message
* ``ipv6`` (optional, type: ``bool``): Bool forcing IPV6 socket instead of IPV4 socket
* ``source_interface`` (optional, defaul: ``None``, type: ``str``): Interface name (like "``eth0``") to bind to for use with IPv6.
  Defaults to ``None`` which will use the default interface (which may not be the one connected to the ECU). Does nothing for IPv4,
  which will bind to all interfaces uses ``INADDR_ANY``.
* ``device_name`` (optional, type: ``str``): Name of DoIP device

**Return:**

* return: IP Address of ECU and VehicleAnnouncementMessage object
* rtype: tuple

**Exception:**

* raises ``TimeoutError: If vehicle announcement not received in time``

**Usage:**

Explicitly specifies all diagnostic message properties

* ``Await Vehicle Annoucement``
* ``Await Vehicle Annoucement | timeout=10``
        """
        try:
            self.__device_check(device_name)
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
        doip_device = "default"
    ):
        """
**Description:**

Sends a ``VehicleIdentificationRequest`` and awaits a ``VehicleIdentificationResponse`` from the ECU,
either with a specified VIN, EIN, or nothing. Equivalent to the ``request_vehicle_identification()`` method
but can be called without instantiation.

**Parameters:**

* ``udp_port`` (optional, type: ``int``): The UDP port to listen on. Per the spec this should be 13400,
  but some VM's use a custom one.
* ``timeout`` (optional, type: ``float``): Maximum amount of time to wait for message
* ``ipv6`` (optional, type: ``bool``): Bool forcing IPV6 socket instead of IPV4 socket
* ``source_interface`` (optional, default: ``None``, type: ``str``): Interface name (like "eth0") to bind to for use with IPv6.
  Defaults to ``None`` which will use the default interface (which may not be the one connected to the ECU). Does nothing for IPv4,
  which will bind to all interfaces uses ``INADDR_ANY``.
* ``device_name`` (optional, type: ``str``): Name of DoIP device

**Return:**

* return: IP Address of ECU and VehicleAnnouncementMessage object
* rtype: tuple

**Exception:**

raises ``TimeoutError: If vehicle announcement not received in time``

**Usage:**

* ``Get Entity |``
* ``Get Entity | ecu_ip_address=172.17.0.111 |``
* ``Get Entity | ecu_ip_address=172.17.0.111 | protocol_version=0x02``
        """
        try:
            doip_device = self.__device_check(device_name)
            address, announcement = DoIPClient.get_entity(ecu_ip_address, protocol_version, eid, vin)
            logical_address = announcement.logical_address
            ip, port = address
            logger.info(f"Target ECU IP: {ip}, Logical ECU Address: {logical_address}, port: {port}")
        except Exception as e:
            logger.error(f"An error occurred while get entity: {e}")

    @keyword("Request Entity Status")
    def request_entity_status(self, device_name = "default"):
        """
**Description:**

Request that the ECU send a **DoIP** Entity Status Response

**Parameters:**

* param ``device_name`` (optional, type: ``str``): Name of DoIP device

**Return:**

None

**Exception:**

None

**Usage:**

* ``Request Entity Status``
        """
        doip_device = self.__device_check(device_name)
        if doip_device.client is not None:
            resp = doip_device.client.request_entity_status()
            logger.info(f"Entity response payload_type: {resp.payload_type}")
        else:
            logger.warn(f"No active DoIP connection. Unable to request entity status.")
    
    @keyword("Request Vehicle Identification")
    def request_vehicle_identification(
        self, 
        eid=None,
        vin=None,
        device_name = "default"
    ):
        """
**Description:**

Sends a ``VehicleIdentificationRequest`` and awaits a ``VehicleIdentificationResponse`` from the ECU,
either with a specified VIN, EIN, or nothing.

**Parameters:**

* ``eid`` (optional, type: ``bytes``): EID of the Vehicle
* ``vin`` (optional, type: ``str``): VIN of the Vehicle
* ``device_name`` (optional, type: ``str``): Name of DoIP device

**Return:**

None

**Exception:**

None

**Usage:**

* ``Request Vehicle Identification``
* ``Request Vehicle Identification | eid=0x123456789abc``
* ``Request Vehicle Identification | vin=0x123456789abc``
        """
        doip_device = self.__device_check(device_name)
        if doip_device.client is not None:
            if eid is not None:
                resp = doip_device.client.request_vehicle_identification(eid)
            elif vin is not None:
                resp = doip_device.client.request_vehicle_identification(vin)
            else:
                resp = doip_device.client.request_vehicle_identification()

            logger.info(f"eid: {resp.eid}")
            logger.info(f"vin: {resp.vin}")
            logger.info(f"gid: {resp.gid}")
            logger.info(f"logical_address: {resp.logical_address}")
            logger.info(f"vin_sync_status: {resp.vin_sync_status}")
        else:
            logger.warn(f"No active DoIP connection. Unable to request vehicle identification.")


    @keyword("Request Alive Check")
    def request_alive_check(self, device_name = "default"):
        """
**Description:**

Request that the ECU send an alive check response.

**Parameters:**

* ``device_name`` (optional, type. ``str``): Name of DoIP device

**Return:**

None

**Exception:**

None

**Usage:**

* ``Request Vehicle Identification``
* ``Request Vehicle Identification | eid=0x123456789abc``
* ``Request Vehicle Identification | vin=0x123456789abc``
        """
        doip_device = self.__device_check(device_name)
        if doip_device.client is not None:
            resp = doip_device.client.request_alive_check()
            logger.info(f"source_address: {resp.source_address}")
        else:
            logger.warn(f"No active DoIP connection. Unable to request alive.")

    @keyword("Request Routing Activation")
    def request_activation(
        self,
        activation_type, 
        vm_specific=None,
        disable_retry=False,
        device_name = "default"
    ):
        """
**Description:**

Requests a given activation type from the ECU for this connection using payload type ``0x0005``.

**Parameters:**

* ``activation_type`` (required, type: ``RoutingActivationRequest.ActivationType``): The type of activation to request - see Table 47
  ("Routing activation request activation types") of ISO-13400, but should generally be 0 (default) or 1 (regulatory diagnostics).
* ``vm_specific`` (optional, type: ``int``): 4 byte long int
* param ``disable_retry`` (optional, type: ``bool``): Disables retry regardless of ``auto_reconnect_tcp`` flag.
  This is used by activation requests during connect/reconnect.
* ``device_name`` (optional, type: ``str``): Name of DoIP device

**Return:**

None

**Exception:**

None

**Usage:**

* ``Request Routing Activation | ${0x02}``
* ``Request Routing Activation | vm_specific=``
* ``Request Routing Activation | vin=0x123456789abc``
        """
        doip_device = self.__device_check(device_name)
        if doip_device.client is not None:
            resp = doip_device.client.request_activation(self, activation_type, vm_specific, disable_retry)
            logger.info(f"client_logical_address: {resp.client_logical_address}")
            logger.info(f"logical_address: {resp.logical_address}")
        else:
            logger.warn(f"No active DoIP connection. Unable to request routing activation.")

    @keyword("Request Diagnostic Power Mode")
    def request_diagnostic_power_mode(self, device_name = "default"):
        """
**Description:**

Request that the ECU send a Diagnostic Power Mode response

**Parameters:**

* ``device_name`` (optional, type: ``str``): Name of DoIP device

**Return:**

None

**Exception:**

None

**Usage:**

* ``Request Diagnostic Power Mode``
        """
        doip_device = self.__device_check(device_name)
        if doip_device.client is not None:
            resp = doip_device.client.request_diagnostic_power_mode()
            logger.info(f"diagnostic_power_mode: {resp.diagnostic_power_mode}")
        else:
            logger.warn(f"No active DoIP connection. Unable to request diagnostic power mode.")

    @keyword("Build payload")
    def build_payload(self, request, device_name = "default"):
        """
**Description:**

Build payload

**Parameters:**

* ``request`` (required, type: ``hex``): hex data
* ``device_name`` (optional, type: ``str``): Name of **DoIP** device

**Return:**

return bytes data of the request

**Exception:**

* raise ``ValueError: if request is None``

**Usage:**

* ``Build payload by protocol version | ${request}``
* ``Build payload by protocol version | hex_value``
        """
        doip_device = self.__device_check(device_name)
        if request is None:
            raise ValueError("The request cannot be None.")

        msg = bytes.fromhex(request)
        message = messages.DiagnosticMessage(doip_device.client._client_logical_address, doip_device.client._ecu_logical_address, msg)
        rtype = messages.payload_message_to_type[type(message)]
        rdata = message.pack()
        data_bytes = doip_device.client._pack_doip(doip_device.client._protocol_version, rtype, rdata)

        return bytes(data_bytes)
