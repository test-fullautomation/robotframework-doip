from abc import ABC, abstractmethod
import socket
import threading
from enum import Enum, auto

POSITIVE_ECU_IP = "172.17.0.5"
POSITIVE_TCP_PORT = 12344
POSITIVE_UDP_PORT = 12345

NEGATIVE_ECU_IP = "172.17.0.5"
NEGATIVE_TCP_PORT = 12346
NEGATIVE_UDP_PORT = 12347

class ECUType(Enum):
    POSITIVE_ECU = 0,
    NEGATIVE_ECU = 1

class AbstractECU(ABC):
    def __init__(self, ecu_type, ip_address, tcp_port, udp_port):
        self.ecu_type = ecu_type
        self.ip_address = ip_address
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.tcp_socket = None
        self.udp_socket = None

    @abstractmethod
    def process_data(self, data):
        pass

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
        print(f'TCP Server {self.ip_address} listening on port {self.tcp_port}')
        while True:
            client_socket, addr = self.tcp_socket.accept()
            print(f'Accepted connection from {addr}')
            thread = threading.Thread(target=self.handle_tcp_client, args=(client_socket,))
            thread.start()

    def handle_tcp_client(self, client_socket):
        data = client_socket.recv(1024)
        while data:
            print(f'TCP Data received: {data}')
            response_data = self.process_data(data)
            client_socket.sendall(response_data)  # Send response through the TCP socket
            data = client_socket.recv(1024)
        client_socket.close()

    def listen_udp(self):
        print(f'UDP Server {self.ip_address} listening on port {self.udp_port}')
        while True:
            data, addr = self.udp_socket.recvfrom(1024)
            print(f'UDP Data received from {addr}: {data}')
            response_data = self.process_data(data)
            self.udp_socket.sendto(response_data, addr)  # Send response through the UDP socket

    def is_request_entity_status(self, data):
        # Check if the received data represents a Entity Status
        return data == b'\x02\xfd@\x01\x00\x00\x00\x00'

    def is_alive_check_request(self, data):
        # Check if the received data represents an Alive Check Request
        return data == b'\x02\xfd\x00\x07\x00\x00\x00\x00'

    def is_activation_default_request(self, data):
        # Check if the received data represents Activation Default Request
        return data == b'\x02\xfd\x00\x05\x00\x00\x00\x07\x0e\x00\x01\x00\x00\x00\x00'

    def is_request_diagnostic_power_mode(self, data):
        return data == b'\x02\xfd@\x03\x00\x00\x00\x00'

class PositiveECU(AbstractECU):
    def process_data(self, data):
        if self.is_alive_check_request(data):
            return self.generate_alive_check_response()
        elif self.is_activation_default_request(data):
            return self.generate_activation_default_response()
        elif self.is_request_diagnostic_power_mode(data):
            return self.generate_diagnostic_power_mode_response()
        elif self.is_request_entity_status(data):
            return self.generate_entity_status_responde()

    def generate_diagnostic_power_mode_response(self):
        # Generate an Diagnostic Power Mode Response
        return bytearray([int(x, 16) for x in "02 fd 40 04 00 00 00 01 01".split(" ")])

    def generate_alive_check_response(self):
        # Generate an Alive Check Response
        return bytearray([int(x, 16) for x in "02 fd 00 08 00 00 00 02 0e 00".split(" ")])

    def generate_activation_default_response(self):
        # Generate an Activation Default Response
        return bytearray([int(x, 16) for x in "02 fd 00 06 00 00 00 09 0e 00 00 37 10 00 00 00 00".split(" ")])

    def generate_entity_status_responde(self):
        # Generate an Entity Status Response
        return bytearray([int(x, 16) for x in "02 fd 40 02 00 00 00 03 01 10 1".split(" ")])

class NegativeECU(AbstractECU):
    def process_data(self, data):
        if self.is_alive_check_request(data):
            return bytearray([int(x, 16) for x in "02 fd 00 12 00 00 00 00 00 00".split(" ")])
        elif self.is_activation_default_request(data):
            return bytearray([int(x, 16) for x in "02 fd 00 06 00 00 00 09 0e 00 00 37 00 00 00 00 00".split(" ")])


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
