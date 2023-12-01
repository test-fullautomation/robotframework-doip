*** Settings ***
Library    DoipKeywords.py

*** Variables ***


*** Test Cases ***
Test Get Entity Gateway
    ${resp}=    Get Entity
    Log     ${resp}
Test Await Vehicle Annoucement
    ${resp}=   Await Vehicle Annoucement
    Log     ${resp}
Test Request Vehicle Identification
    ${resp}=   Request Vehicle Identification 
    Log     ${resp}

Test Request Vehicle Identification with EID
    Request Vehicle Identification    eid="0x123456789abc"
  