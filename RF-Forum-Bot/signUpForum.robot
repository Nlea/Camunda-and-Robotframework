*** Settings ***
Documentation     Signup automatically to the Camunda Forum

Library           RPA.Browser.Selenium

*** Variables ***
${email}      hello@test.de
${username}   test
${account-name}   default.test


*** Tasks ***
Sign Up to the Camunda Forum

    #Input Data to sign up for Community Newsletter
    Open Available Browser    https://forum.camunda.org/
    Title Should Be    Camunda Platform Forum - Community discussion on Camunda Platform including business process management and process automation

    Click Button      //button[@class ="widget-button btn btn-primary btn-small sign-up-button btn-text"]

    Wait Until Element Is Visible   //*[@class="create-account-form"] 

    Input Text   id:new-account-email   ${email}
    Input Text   id:new-account-username   ${username}
    Input Text   id:new-account-name   ${account-name}
    Input Text   id:new-account-password   communityRocks!

    
    Click Button      //button[@id ="ember130"]
    

