*** Settings ***
Library    Collections
Library           RPA.Email.ImapSmtp    smtp_server=smtp.gmail.com    smtp_port=587
Variables   env.py

*** Variables ***    
 
${PASSWORD}   ${env_password} 
${USERNAME}   ${env_username}

*** Tasks ***
Send Email Task
    [Documentation]    Send an Email


    Authorize    account=${USERNAME}    password=${PASSWORD}
    Send Message    sender=${USERNAME}
    ...    recipients=${email}
    ...    subject=${subject}
    ...    body=${body}