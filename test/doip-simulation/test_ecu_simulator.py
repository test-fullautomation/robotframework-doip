doip = DoIPClient('172.17.0.5', 57344, tcp_port=12344, udp_port=12345, activation_type=None)
print(doip.request_diagnostic_power_mode())
print(doip.request_entity_status())
print(doip.request_alive_check())
print(doip.request_activation(1))

doip_ne = DoIPClient('172.17.0.5', 57344, tcp_port=12346, udp_port=12347, activation_type=None)
print(doip_ne.request_activation(1))