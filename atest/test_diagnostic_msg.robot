*** Settings ***
Library    RobotFramework_DoIP

*** Test Cases ***
# Test case 1: Connect to ECU and send diagnostic message
Connect To ECU with Target and Client and Send Diagnostic Message
    Connect To ECU     192.168.108.1      ${12288}    client_ip_address=192.168.108.1    client_logical_address=${3584}     activation_type=${0}
    Send Diagnostic Message    1001
    ${resp}=    Receive Diagnostic Message
    Log To Console    ${resp}