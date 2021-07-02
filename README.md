# Camunda-and-Robot-framework
This project shows how to integrate [Robot framework (RF)](https://robotframework.org/) with [Camunda Platform](https://docs.camunda.org/manual/7.15/).

The project contains a BPMN diagram and the implementation of the service tasks with Robot framework. The service tasks in Camunda are implemented as [External Task](https://docs.camunda.org/manual/latest/user-guide/process-engine/external-tasks/) .

A full list with other projects that integrate Camunda and Robot framework can be found [here](https://github.com/camunda-community-hub/awesome-Camunda-and-Robotframework-projects)


## The process
Becoming part of the Camunda Community is related with various sign ups. This process automates the sign up for the [Camunda Platform Forum](https://forum.camunda.org/) and the [Camunda Community Newsletter](https://camunda.com/developers/developer-community-updates/). At the start  you can decide what you want to register for and provide the details. 

![Camunda Community Sign up Process](/img/Robotframework-process.png)

After the registration an email is sent to the user to inform them about the new accounts. The following provides more detail on the different RF Service Task implementations, and the different architecture they use in order to integrate with Camunda:


## Robot Framework Tasks

### Robot framework for User Interface (UI) Automation
[RPA](https://en.wikipedia.org/wiki/Robotic_process_automation) Tools automate User interfaces and therefore can bring together systems that were not designed to interact with each other (for example some systems miss APIs to integrate with others).

In this example user interface automation is shown at two service tasks implementations. The Service tasks "Signup for community newsletter" and "Signup for forum" uses the [Selinium library](https://robotframework.org/SeleniumLibrary/), which makes it easy to automate browser interactions. 

### Robot framework beyond UI Automation
Robot framework is not just about UI Automation. Coming from test automation it provides other functionalities too. Hence a Robot Framework Task can be used beyond UI automation. In this example a RF task [sends an email from a gmail account](https://robocorp.com/docs/development-guide/email/sending-emails-with-gmail-smtp). To send the email the RF task uses the [rpaframework library](https://rpaframework.org/), which is provided by Robocorp. Robocorp provides a Cloud environment to run your Bots. Further it provides a lot of additional open source tooling and libraries for Robot framework.

## Architecture
Robot framework is python based. It is possible to integrate various python libraries into Robot framework files. Therefore it is possible to call Camunda directly from a Robot framework Task. Within the community there is the [Robotframework-camunda library](https://pypi.org/project/robotframework-camunda/), which allows connecting Camunda directly from RF. As RF tasks normally terminate and are not designed to run constantly, there is a gap when it comes to polling. Polling on the other hand is needed for the concept of [External Task](https://docs.camunda.org/manual/latest/user-guide/process-engine/external-tasks/) within Camunda.

In this example the three Service tasks implemented in Robot Framework use a different architecture to achieve polling.

### Robotframework-camunda library
![Architecture with Robotframework-camunda library](/img/a2.png)

The "Subscribe to community newsletter" Service task uses mainly the [Robotframework-camunda library](https://pypi.org/project/robotframework-camunda/). Hence, business logic and communication with Camunda happens within the Robotframework Task. The library defines Keywords which can be used within the RF task to connect to Camunda:

```

*** Tasks ***
Execute Service Task
    [Documentation]    Camunda Service task to Subscribe to the Camunda Community Newsletter

#Fetch and Lock the task and get variables from the process

    ${existing_topic}    Fetch workload    SubscribeToNewsletter
    ${recent_task}    Get fetch response
    log    \t${recent_task}

    #get Variables from response body

    ${firstname}=   Set variable   ${recent_task}[variables][firstname][value]
    ${lastname}=    Set variable    ${recent_task}[variables][lastname][value]
    ${email}=    Set variable    ${recent_task}[variables][email][value]

#Business logic

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



    
 # create process variables and complete task
    ${my_result}    Create Dictionary    Newsletter=True
    complete task   ${my_result}


```

Polling is not supported within the library. In this example the External Task Client in Python is used for the polling.

:exclamation: **Attention:**
 With this pattern you have to make sure that the locktime for the Polling handler is short. If it is too long the RF task can't fetch and lock the task afterwards. A better way would be to write a client that just polls without locking available external tasks.

 :grey_exclamation:
Failure and BPMN Error are not available in the Robotframework-Camunda library at the moment
(This means when some steps in the RF task fail, the complete won't be triggered. Hence in Cockpit there is no indication that the RF task has failed)


### Camunda-external-task-client-python3

![Architecture with Robotframework-camunda library](/img/a1.png)

Within this pattern, the Robot framework task does not interact with Camunda. The interaction with Camunda happens within the [Camunda external task client](https://pypi.org/project/camunda-external-task-client-python3/). The external task handler takes care to get variables from the process and converts them into the format that is need to hand them into the RF task. In this example the “Send Mail” Service task uses this pattern.


```python
 # get Variables from the process
    emailAddress = task.get_variable("email")
    newsletter = task.get_variable("newsletter")
    forum = task.get_variable("forum")
    username = task.get_variable("usernameForum")
    subject = "Welcome to the Camunda Community"
...    

# Put variables into a list for the RF-task
    email = 'email:'+ emailAddress
    body = 'body:'+ body
    subject= 'subject:'+ subject
    
    variables =[email, body, subject]  

```

From there the RF is started. The output of the started RF contains a number. If it is not a 0, that means that the RF task has failed at one point. In this case the external task client sends back a failure, which creates an incident within the Camunda Engine.


```python
#start RF-task
    robotOutput = robot.run("mailing.robot", variable=variables)
    
    # send failure if RF does not completed successfully
    if(robotOutput!= 0):        
        return task.failure(error_message="RF-task failed",  error_details="The RF task was not completed successfully. For more information open the log.html from the RF task ",
                            max_retries=0, retry_timeout=5000)
        
    
    # complete task, if RF task completed successfully    
    return task.complete({"emailSent": True})

```


 :grey_exclamation:
The output number from the RF task can be further differentiated for fine-granular handling (e.g certain numbers can lead to a BPMN error instead of a failure).

 :grey_exclamation:
If variables from the RF task have to return, the Listener API can be used.  


### Robocorp


**Remark:** At the moment this architecture is not implemented. Instead the implementation of the “Sign up for forum”- task follows the approach with the [Camunda-external-task-client-python3](## Camunda-external-task-client-python3).

![Architecture with Robotframework-camunda library](/img/a3.png)

**Idea about the architecture (will be implemented in the future)**:
Within this architecture, our Robot Framework Bot runs within the Robocorp Cloud. The External-Task-handler controls the communication between Camunda and Robocorp In order to so, you need to create an account at [Robocorp](https://robocorp.com/).

In this example we want to start our Robot using the [Robocorp Process API](https://robocorp.com/docs/robocorp-cloud/api/process-api).

:exclamation:**Attention**:
Unfortunately, within the free account option it is not possible to use the API to start a Robot. In order to do so the **Flex Account** is needed.

If you have the access to "trigger-process" from the Robocorp API, you can upload a Robot to the Robocloud. This can be done via the command line, link to the github repo of your Robot or via file upload. The RF-Forum-Bot follows the basic [structure guidelines](https://robocorp.com/docs/setup/robot-structure) of Robocorp. Therefore it contains attionally a robot.yaml and a conda.yaml. You can upload the compressed file directly to your Robocorp Cloud.

Within the Cloud under the tab workforce you can define processes. Create a new process and configure the process. Within the configuration you can add steps. Here you can now select from your uploaded Robots.

In order to use the Robocorp API you need to create an API Key. More information and a detailed instruction video is [here](https://robocorp.com/docs/robocorp-cloud/api).

Please be aware that you need to have a payment plan where the "triggering process" is enabled.


## Run the project
1. Start Camunda (you can use [Docker](https://github.com/camunda/docker-camunda-bpm-platform) or [Camundarun](https://docs.camunda.org/manual/7.15/installation/camunda-bpm-run/))
2. Deploy the process Diagramm to Camunda
3. Start a process instance
4. Install needed Python modules for each RF-Worker. Run ```pip install -r install/requirements.txt```
5. Make sure to include your credentials RF-Mailing-Bot/env.py
5. Start the External-task-handler or the Polling-handler in each RF Worker folder ```python3 External-task-handler.py```
6. Observer your results in Cockpit, the log.hmtl and Robocorp of each RF Worker

## To do for the project:
- At the moment there is no validation if the forum sign up and the registration for the newsletter have been successful (need to be added)
- Hand back variables to Camunda with [Camunda-external-task-client-python3](## Camunda-external-task-client-python3).
- Error Handling (BPMN Error)
- Implement architecture with Robocorp
