*** Settings ***
Documentation     Signup automatically to the Camunda Community Newsletter

Library           RPA.Browser.Selenium

Library    CamundaLibrary   ${CAMUNDA_HOST}
Library    Collections

*** Variables ***
${CAMUNDA_HOST}    http://localhost:8080
${existing_topic}    SubscribeToNewsletter



*** Tasks ***
Execute Service Task
    [Documentation]    Camunda Service task to Subscribe to the Camunda Community Newsletter

    ${existing_topic}    Fetch workload    SubscribeToNewsletter
    ${recent_task}    Get fetch response
    log    \t${recent_task}

    #get Variables from response body

    ${firstname}=   Set variable   ${recent_task}[variables][firstname][value]
    ${lastname}=    Set variable    ${recent_task}[variables][lastname][value]
    ${email}=    Set variable    ${recent_task}[variables][email][value]



    #Input Data to sign up for Community Newsletter
    Open Available Browser    https://camunda.com/developers/developer-community-updates/
    Title Should Be    Developer Community Updates - Camunda

    
    Wait Until Element Is Visible   //button[@class="osano-cm-save osano-cm-buttons__button osano-cm-button osano-cm-button--type_save"] 
    
    Click Button       //button[@class="osano-cm-save osano-cm-buttons__button osano-cm-button osano-cm-button--type_save"]


    Wait Until Element Is Visible    tag:iframe
    Select Frame    tag:iframe
    Input Text When Element Is Visible    name:email    ${email}
    Input Text When Element Is Visible    name:firstname    ${firstname}
    Input Text When Element Is Visible    name:lastname    ${lastname}

    Click Element      //*[@class ="hs-button primary large"]

    
 # create result and return workload to Camunda
    ${my_result}    Create Dictionary    Newsletter=True
    complete task   ${my_result}
