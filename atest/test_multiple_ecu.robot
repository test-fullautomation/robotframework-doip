*** Settings ***
Library    RobotFramework_TestsuitesManagement    WITH NAME    testsuites
Library    RobotFramework_UDS
Library    RobotFramework_DoIP

*** Variables ***
${SUT_IP_ADDRESS_1}=         SUT_IP_ADDRESS_1
${SUT_LOGICAL_ADDRESS_1}=    SUT_LOGICAL_ADDRESS_1
${TB_IP_ADDRESS_1}=          TB_IP_ADDRESS_1
${TB_LOGICAL_ADDRESS_1}=     TB_LOGICAL_ADDRESS_1
${ACTIVATION_TYPE_1}=        0
${DEVICE_NAME_1}=            DoIP Connector 1

${SUT_IP_ADDRESS_2}=         SUT_IP_ADDRESS_2
${SUT_LOGICAL_ADDRESS_2}=    SUT_LOGICAL_ADDRESS_2
${TB_IP_ADDRESS_2}=          TB_IP_ADDRESS_2
${TB_LOGICAL_ADDRESS_2}=     TB_LOGICAL_ADDRESS_2
${ACTIVATION_TYPE_2}=        0
${DEVICE_NAME_2}=            DoIP Connector 2

*** Test Cases ***
Test user can connect single connection
    Log    Test user can connect single connection
    Log    If no device_name is provided, it will default to 'default'

    Create UDS Connector    ecu_ip_address= ${SUT_IP_ADDRESS_1}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS_1}
    ...                     client_ip_address= ${TB_IP_ADDRESS_1}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS_1}
    ...                     activation_type= ${ACTIVATION_TYPE_1}

    Send Diagnostic Message    1001
    ${resp}=    Receive Diagnostic Message
    Log To Console    ${resp}
    Disconnect

Test user can connect multiple connection
    Log    Connect to ECU 1

    Connect To ECU          device_name= ${DEVICE_NAME_1}
    ...                     ecu_ip_address= ${SUT_IP_ADDRESS_1}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS_1}
    ...                     client_ip_address= ${TB_IP_ADDRESS_1}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS_1}
    ...                     activation_type= ${ACTIVATION_TYPE_1}

    Send Diagnostic Message    1001    device_name= ${DEVICE_NAME_1}
    ${resp}=    Receive Diagnostic Message    device_name= ${DEVICE_NAME_1}
    Log To Console    ${resp}
    Disconnect    device_name= ${DEVICE_NAME_1}
   
    Log    Connect to ECU 2
    Connect To ECU          device_name= ${DEVICE_NAME_2}
    ...                     ecu_ip_address= ${SUT_IP_ADDRESS_2}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS_2}
    ...                     client_ip_address= ${TB_IP_ADDRESS_2}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS_2}
    ...                     activation_type= ${ACTIVATION_TYPE_2}

    Send Diagnostic Message    1001    device_name= ${DEVICE_NAME_2}
    ${resp}=    Receive Diagnostic Message    device_name= ${DEVICE_NAME_2}
    Log To Console    ${resp}
    Disconnect    device_name= ${DEVICE_NAME_2}

Test user can connect multiple connection but connect to the same ECU
    Log    Test user can connect multiple connection but connect to the same ECU
    Log    Connect to device 1

    Connect To ECU          device_name= ${DEVICE_NAME_1}
    ...                     ecu_ip_address= ${SUT_IP_ADDRESS_1}
    ...                     ecu_logical_address= ${SUT_LOGICAL_ADDRESS_1}
    ...                     client_ip_address= ${TB_IP_ADDRESS_1}
    ...                     client_logical_address= ${TB_LOGICAL_ADDRESS_1}
    ...                     activation_type= ${ACTIVATION_TYPE_1}

    Log    Connect to device 2 but same IP as device 1
    Log    The expected test case result in an error
    Run Keyword And Expect Error    TimeoutError: ECU failed to respond in time    Connect To ECU          device_name= ${DEVICE_NAME_2}
    ...                                                                                                    ecu_ip_address= ${SUT_IP_ADDRESS_1}
    ...                                                                                                    ecu_logical_address= ${SUT_LOGICAL_ADDRESS_1}
    ...                                                                                                    client_ip_address= ${TB_IP_ADDRESS_1}
    ...                                                                                                    client_logical_address= ${TB_LOGICAL_ADDRESS_1}
    ...                                                                                                    activation_type= ${ACTIVATION_TYPE_1}