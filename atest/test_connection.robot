*** Test Cases ***

# Test case 1: Connect to ECU with explicit IP address and port
Connect to ECU with Target IP and Port
    [Tags]    Connect
    Connect To ECU     192.168.108.1      ${12288}

# Test case 2: Connect to ECU with explicit IP address and port and client
Connect To ECU with Target and Client 
    Connect To ECU     192.168.108.1      ${12288}    client_ip_address=192.168.108.1    client_logical_address=${3584}


    

