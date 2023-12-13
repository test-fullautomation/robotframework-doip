from doipclient import DoIPClient
import doipclient.messages
ip = '172.17.0.5'

doip = DoIPClient(ip, 57344, activation_type=None)
print(doip.request_diagnostic_power_mode())
print(doip.request_entity_status())
print(doip.request_alive_check())
print(doip.request_activation(1))
print(doip.get_entity())
print(doip.request_vehicle_identification(vin="1" * 17))
print(doip.request_vehicle_identification(eid=b"1" * 6))

doip_ne = DoIPClient(ip, 57344, tcp_port=12346, udp_port=12347, activation_type=None)
print(doip_ne.request_diagnostic_power_mode())
print(doip_ne.request_entity_status())
print(doip_ne.request_alive_check())
print(doip_ne.request_activation(1))
