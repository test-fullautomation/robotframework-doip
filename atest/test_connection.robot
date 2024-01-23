*** Settings ***
Library    RobotFramework_DoIP

*** Test Cases ***
# Test case 1: Connect to ECU with explicit IP address and port
Connect to ECU with Target IP and Port specified as integer
    [Tags]    Connect
    Connect To ECU     192.168.108.1      ${12288}
    Disconnect

Connect to ECU with Target IP and Port specified as string
    [Tags]    Connect
    Connect To ECU     192.168.108.1      12288
    Disconnect

# Test case 2: Connect to ECU with explicit IP address and port and client
Connect To ECU with Target and Client 
    [Tags]    Connect
    Connect To ECU     192.168.108.1      ${12288}    client_ip_address=192.168.108.1    client_logical_address=${3584}
    Disconnect

Connect To ECU with Target and Client specified as string
    [Tags]    Connect
    Connect To ECU     192.168.108.1      12288    client_ip_address=192.168.108.1    client_logical_address=3584
    Disconnect

# Test case 3: Connect to ECU with client and activation ECU
Connect To ECU with Target and Client and enable active ECU
    [Tags]    Connect
    Connect To ECU     192.168.108.1      ${12288}    client_ip_address=192.168.108.1    client_logical_address=${3584}    activation_type=${0}
    Disconnect

Connect To ECU with Target and Client and enable active ECU specified as string
    [Tags]    Connect
    Connect To ECU     192.168.108.1      12288    client_ip_address=192.168.108.1    client_logical_address=3584    activation_type=0
    Disconnect