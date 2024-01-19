*** Settings ***
Library    RobotFramework_DoIP

*** Test Cases ***

Test Get Entity Gateway
    Get Entity

Test Await Vehicle Annoucement
    Await Vehicle Annoucement

Test Request Vehicle Identification
    Connect To ECU     192.168.108.1      ${12288}
    Request Vehicle Identification 

Test Request Vehicle Identification with VIN
    Connect To ECU     192.168.108.1      ${12288}
    Request Vehicle Identification    vin=TESTVIN0000012345
  
Test Request Diagnostic Power Mode
    Connect To ECU     192.168.108.1      ${12288}
    Request Diagnostic Power Mode

