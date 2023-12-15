from doipclient import DoIPClient

def test_positive_ecu_simulator():
      try:
         ip = '172.17.0.5'
         ecu_logical_address = 57344

         # Create a DoIPClient instance for positive ECU simulator
         doip = DoIPClient(ip, ecu_logical_address, activation_type=None)

         # Test various interactions
         print(doip.request_diagnostic_power_mode())
         print(doip.request_entity_status())
         print(doip.request_alive_check())
         print(doip.request_activation(1))
         print(doip.get_entity())
         print(doip.request_vehicle_identification(vin="1" * 17))
         print(doip.request_vehicle_identification(eid=b"1" * 6))

      except Exception as e:
         print(f"Error during positive ECU simulation: {e}")

def test_negative_ecu_simulator():
      try:
         ip = '172.17.0.5'
         tcp_port = 12346
         udp_port = 12347
         ecu_logical_address = 57344
         # Create a DoIPClient instance for negative ECU simulator
         doip_ne = DoIPClient(ip, ecu_logical_address, tcp_port=tcp_port, udp_port=udp_port, activation_type=None)

         # Test various interactions
         print(doip_ne.request_diagnostic_power_mode())
         print(doip_ne.request_entity_status())
         print(doip_ne.request_alive_check())
         print(doip_ne.request_activation(1))

      except Exception as e:
         print(f"Error during negative ECU simulation: {e}")

if __name__ == "__main__":
   test_positive_ecu_simulator()
   test_negative_ecu_simulator()
