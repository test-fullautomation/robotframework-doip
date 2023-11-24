*** Settings ***
Resource    ../import.resource

*** Variables ***


*** Keywords ***
# ***************************************************************************************************
prj.testbench.doip: Request Message
    [Arguments]    ${targetIP}
    ...            ${lMsg}
    ...            ${testerIP}=${dTESTBENCH.doip.testerIP}
    ...            ${route}=${0}
    ${sResponse}    run DoIP    ${targetIP}    ${testerIP}    ${lMsg}    ${route}
    [Return]    ${sResponse}

prj.testbench.doip: DoIP Get Build Version Label on CTS
    Log To Console    Send Request Message: BuildVersionLabel
    ${lMsg}    Create List    ${dTESTBENCH.doip.CTSSentMsgDefault}    ${dTESTBENCH.doip.CTSSentMsgExtendedDiagnostic}    ${dTESTBENCH.doip.CTSSentMsgBuildVersionLabel}
    ${bAck}    ${sMsg}    prj.testbench.doip: Request Message    ${dTESTBENCH.doip.CTSTargetIP}    ${lMsg}
    Return From Keyword If    ${bAck} == ${False}    ${False}    No Response    ${sMsg}
    ${bAck}    Run Keyword And Return Status    Should Contain    ${sMsg}    ${dTESTBENCH.doip.CTSRespMsgBuildVersionLabel}
    Return From Keyword If    ${bAck} == ${False}    ${False}    Negative Response    ${sMsg}
    ${sCTSVersion}    Get Build Version Label    ${sMsg}
    [Return]    ${True}    Positive Response    ${sCTSVersion}

prj.testbench.doip: DoIP Get Software Version on CTS
    Log To Console    Send Request Message: SoftwareVersion
    ${lMsg}    Create List    ${dTESTBENCH.doip.CTSSentMsgDefault}    ${dTESTBENCH.doip.CTSSentMsgExtendedDiagnostic}    ${dTESTBENCH.doip.CTSSentMsgSoftwareVersion}
    ${bAck}    ${sMsg}    prj.testbench.doip: Request Message    ${dTESTBENCH.doip.CTSTargetIP}    ${lMsg}
    Return From Keyword If    ${bAck} == ${False}    ${False}    No Response    ${sMsg}
    ${bAck}    Run Keyword And Return Status    Should Contain    ${sMsg}    ${dTESTBENCH.doip.CTSRespMsgSoftwareVersion}
    Return From Keyword If    ${bAck} == ${False}    ${False}    Negative Response    ${sMsg}
    ${sCTSSWVersion}    Get Software Version    ${sMsg}
    [Return]    ${True}    Positive Response    ${sCTSSWVersion}

prj.testbench.doip: DoIP Get Build Version Label on CSB
    Log To Console    Send Request Message: BuildVersionLabel
    ${lMsg}    Create List    ${dTESTBENCH.doip.CSBSentMsgDefault}    ${dTESTBENCH.doip.CSBSentMsgCMProduction}    ${dTESTBENCH.doip.CSBSentMsgECUSWBuildVersionLabel}
    ${bAck}    ${sMsg}    prj.testbench.doip: Request Message    ${dTESTBENCH.doip.CSBTargetIP}    ${lMsg}
    Return From Keyword If    ${bAck} == ${False}    ${False}    No Response    ${sMsg}
    ${bAck}    Run Keyword And Return Status    Should Contain    ${sMsg}    ${dTESTBENCH.doip.CSBRespMsgECUSWBuildVersionLabel}
    Return From Keyword If    ${bAck} == ${False}    ${False}    Negative Response    ${sMsg}
    ${sCSBVersion}    Get Build Version Label    ${sMsg}
    [Return]    ${True}    Positive Response    ${sCSBVersion}

prj.testbench.doip: DoIP Verify Build Version Label on CTS
    [Arguments]    ${sPackagePath}    ${sHeader}
    [Documentation]    Verify built version label after flashing
    Set Local Variable    ${bAck}    ${False}
    Log To Console    DoIP on CTS
    ${bAck}    ${sResp}    ${sMsg}    prj.testbench.doip: DoIP Get Build Version Label on CTS
    IF    ${bAck} == ${False}
        IF    "${sResp}" == "Negative Response"
            Log To Console    Negative response code [${sMsg}] --> Service has a failure
        ELSE
            Log To Console    Flashing failed due to no connection to SuT.
        END
        Return From Keyword    ${False}
    ELSE
        Log To Console    Build Version Label: ${sMsg}
            ${sPackageVersion}    Get Package Version Label    ${sPackagePath}    ${sHeader}
            IF    ${sPackageVersion}[0] == ${True}
                IF    ${sPackageVersion}[1] == ${sMsg}
                    Log To Console    Both versions are the same --> Flashing successfull
                ELSE
                    Log To Console    Both versions are not the same --> Flashing failed
                END
            END
        Return From Keyword    ${True}
    END