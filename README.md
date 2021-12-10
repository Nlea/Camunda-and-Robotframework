# Camunda-and-Robot-framework

This project demonstrates how to integrate [Robot framework (RF)](https://robotframework.org/) with [Camunda Platform](https://docs.camunda.org/manual/7.15/).

This repo contains a BPMN diagram and the implementation of the service tasks with RF. The service tasks in Camunda are implemented as [External Tasks](https://docs.camunda.org/manual/latest/user-guide/process-engine/external-tasks/).

Find a full list of projects that integrate Camunda and RF [here](https://github.com/camunda-community-hub/awesome-Camunda-and-Robotframework-projects).

## Table of content
[The process](##The process)
[Robot framework task](##Robot)


## The process

Joining the Camunda Community is related to various sign ups. This process automates the sign up for the [Camunda Platform Forum](https://forum.camunda.org/) and the [Camunda Community Newsletter](https://camunda.com/developers/developer-community-updates/). From the start, you can decide what you want to register for and provide the details. 

![Camunda Community Sign up Process](/img/Robotframework-process.png)

After registration, an email is sent to the user to inform them about the new accounts. The following document provides more detail on the different RF Service Task implementations, and the different architecture they use to integrate with Camunda:

## Robot framework tasks

### Robot framework for user interface (UI) automation

[RPA](https://en.wikipedia.org/wiki/Robotic_process_automation) Tools automate UI. Therefore, the tools can bring together systems that were not designed to interact with each other (for example, some systems miss APIs to integrate with others.)

In this example, UI automation is shown at two service task implementations. The service tasks "Signup for community newsletter" and "Signup for forum" uses the [Selinium library](https://robotframework.org/SeleniumLibrary/), which makes it easy to automate browser interactions. 

### Robot framework beyond UI Automation

Robot framework is not just about UI automation. Coming from test automation, it provides additional functionalities. Hence, a RF task can be used beyond UI automation. In this example, a RF task [sends an email from a Gmail account](https://robocorp.com/docs/development-guide/email/sending-emails-with-gmail-smtp). To send the email, the RF task uses the [rpaframework library](https://rpaframework.org/), which is provided by Robocorp. Robocorp provides a Cloud environment to run your Bots. Additionally, Robocorp provides a signifitant amount of additional open-source tooling and libraries for Robot framework.

## Architecture

Robot framework is Python-based. It is possible to integrate various Python libraries into Robot framework files. Therefore, it is possible to call Camunda directly from a Robot framework task. Within the community, the [Robotframework-camunda library](https://pypi.org/project/robotframework-camunda/) allows connecting Camunda directly from RF. As RF tasks normally terminate and are not designed to run constantly, there is a gap in polling. However, polling is needed for the concept of [External Task](https://docs.camunda.org/manual/latest/user-guide/process-engine/external-tasks/) within Camunda.

In this example, the three service tasks implemented in Robot Framework use a different architecture to achieve polling.

### Robotframework-camunda library

![Architecture with Robotframework-camunda library](/img/a2.png)

The **Subscribe to community newsletter** service task mainly uses the [Robotframework-camunda library](https://pypi.org/project/robotframework-camunda/). Hence, business logic and communication with Camunda happens within the Robot framework task. The library defines **Keywords**, which can be used within the RF task to connect to Camunda:

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

Polling is not supported within the library. In this example, the External Task Client in Python is used for the polling.

:exclamation: **Attention:**
With this pattern, you must ensure the locktime for the polling handler is short. If it is too long, the RF task won't fetch and lock the task afterwards. A better option is to write a client that polls without locking available external tasks.

 :grey_exclamation:
Failure and BPMN Error are not available in the RF Camunda library currently. Therefore, when some steps in the RF task fail, the complete won't be triggered. Hence, in Cockpit, there is no indication the RF task has failed.


### Camunda-external-task-client-python3

![Architecture with Robotframework-camunda library](/img/a1.png)

Within this pattern, the Robot framework task does not interact with Camunda. The interaction with Camunda happens within the [Camunda external task client](https://pypi.org/project/camunda-external-task-client-python3/). The external task handler takes care to get variables from the process and converts them into the format needed to hand them into the RF task. In this example, the **Send Mail** service task uses this pattern:


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

From here, the RF is started. The output of the started RF contains a number. If it is not a **0**, the RF task has failed at one point. In this case, the external task client sends back a failure, which creates an incident within the Camunda Engine.


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
The output number from the RF task can be further differentiated for fine-granular handling (e.g. certain numbers can lead to a BPMN error instead of a failure.)

 :grey_exclamation:
If variables from the RF task have to return, the Listener API can be used.  


### Robocorp


**Remark:** Currently, this architecture is not implemented. Instead, the implementation of the **Sign up for forum** task follows the approach with the [Camunda-external-task-client-python3](## Camunda-external-task-client-python3).

![Architecture with Robotframework-camunda library](/img/a3.png)

**Idea about the architecture (will be implemented in the future)**:
Within this architecture, our RF Bot runs within the Robocorp Cloud. The **External-Task-handler** controls the communication between Camunda and Robocorp. To do so, create an account at [Robocorp](https://robocorp.com/).

In this example, we want to start our Robot using the [Robocorp Process API](https://robocorp.com/docs/robocorp-cloud/api/process-api).

:exclamation:**Attention**:
Unfortunately, it is not possible to use the API to start a Robot within the free account option. To accomplish this, the **Flex Account** is needed.

If you have the access to "trigger-process" from the Robocorp API, you can upload a Robot to the Robocloud. This can be done via the command line. Link to the GitHub repo of your Robot or via file upload. The **RF-Forum-Bot** follows the basic [structure guidelines](https://robocorp.com/docs/setup/robot-structure) of Robocorp. Therefore, it contains a robot.yaml and a conda.yaml. You can upload the compressed file directly to your Robocorp Cloud.

You can define processes within the Cloud, under the tab workforce. Create a new process and configure the process. Within the configuration, you can add steps. Here, you can now select from your uploaded Robots.

To use the Robocorp API, create an API Key. More information and a detailed instruction video is [here](https://robocorp.com/docs/robocorp-cloud/api).

Note that you must have a payment plan where the **triggering process** is enabled.


## Run the project

1. Start Camunda (you can use [Docker](https://github.com/camunda/docker-camunda-bpm-platform) or [Camundarun](https://docs.camunda.org/manual/7.15/installation/camunda-bpm-run/)).
2. Deploy the process Diagram to Camunda.
3. Start a process instance.
4. Install necessary Python modules for each RF-Worker. Run ```pip install -r install/requirements.txt```.
5. Make sure to include your credentials `RF-Mailing-Bot/env.py`.
5. Start the **External-task-handler** or the **Polling-handler** in each RF Worker folder ```python3 External-task-handler.py```.
6. Observe your results in Cockpit, the log.hmtl, and Robocorp of each RF Worker.

## To do for the project

- Currently, there is no validation if the forum, sign up, and the registration for the newsletter have been successful (need to be added.)
- Hand back variables to Camunda with [Camunda-external-task-client-python3](## Camunda-external-task-client-python3).
- Error Handling (BPMN Error.)
- Implement architecture with Robocorp.
