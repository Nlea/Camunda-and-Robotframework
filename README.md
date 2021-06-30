# Camunda-and-Robot-framework
This project shows how to integrate [Robot framework (RF)](https://robotframework.org/) with Camunda.

The project contains a BPMN diagramm and the implementation of the service tasks with Robot framework. The service tasks in Camunda are implemented as External Tasks. 

A full list with other projects that integrate Camunda and Robot framework can be found [here](https://github.com/camunda-community-hub/awesome-Camunda-and-Robotframework-projects)

The following provides more detail on the different RF Service Task implementations, and the different architecture they use in order to integrate with Camunda:

##Robot Framework Tasks

### Robot framework for User Interface (UI) Automation
RPA Tools automate User interfaces and therefore can bring together system that where not designed to interact with each other (for example some systems miss APIs to integrate with others).

In this example user interface automation is shown at two service tasks implementations. The Service tasks "Signup for community newsletter" and "Signup for forum" uses the [Selinium library](https://robotframework.org/SeleniumLibrary/), which makes it easy to automate browser interaction.

### Robot framework beyond UI Automation
Robot framework is not just about UI Automation. Coming from test automation it provides other funcionalities too. Hence a Robot Framework Task can be used beyond UI automation. In this example a RF task [sends an email from a gmail account](https://robocorp.com/docs/development-guide/email/sending-emails-with-gmail-smtp). To send the email the RF task uses the rpaframework library, which is provided by Robocorp. Robocorp provides a Cloud envirorment to run your Bots. Further it provides a lot of addional open source tooling and libraries for Robot framework.

##Architecture
Robot framework is python based. It is possible to integrate various python libraries into Robot framework files. Therefore it is possible to call Camunda directly from a Robot framework Task. Within the community there is the Robotframework-camunda library, which allows to connect Camunda directly from RF. As RF task normally terminate and are not designed to run constantly there is a gap when it comes to polling. Polling on the other hand is needed for the concept of [External Task](https://docs.camunda.org/manual/latest/user-guide/process-engine/external-tasks/) within Camunda. 

In this example the three Service tasks implemented in Robot Framework all uses a different architecture to achieve polling. 

### Robotframework-camunda library
The "SignUp" Service task uses mainly the [Robotframework-camunda library](https://pypi.org/project/robotframework-camunda/). Hence business logic and communication with Camunda happens within the Robotframework Task. 

Polling is not supported within the library. In this example the External Task Client in Python is used for the polling. 

![Architecture with Robotframework-camunda library](/img/Architecture1.png)

:exclamation: **Attention:**
 With this pattern you have to make sure that the locktime for the Polling handler is short. If it is too long the RF task can't fetch and lock the task afterwards. A better way would be to write a client that just polls without locking available external tasks. 

 :grey_exclamation:
Failure and BPMN Error are not available in the Robotframework-Camunda library at the moment
(This means when some steps in the RF task fail, the complete won't be triggered. Hence )


### Camunda-external-task-client-python3
Within this pattern the Robot framework task does not interact with Camunda. The interaction with Camunda happens within the [Camunda external task client](https://pypi.org/project/camunda-external-task-client-python3/). From there the RF is started. The output of the started RF contains a number. If it is not a 0, that means that the RF task has failed at one point. In this case the external task client sends back a failure, which creates an incident within the Camunda Engine.

![Architecture with Robotframework-camunda library](/img/Architecture2.png)

 :grey_exclamation:
The output number from the RF task can be further differentiated for fine-granular handling (e.g certain numbers can lead to a BPMN error instead of a failure). 

 :grey_exclamation:
If variables from the RF task has to return, the Listener API can be used.  


### Robocorp
Within this arichtecture our Roboframework Bot runs within the Robocorp Cloud. The External-Task-handler controls the communication between Camunda and Robocorp In order to so, you need to create an account at [Robocorp](https://robocorp.com/). 

![Architecture with Robotframework-camunda library](/img/Architecture3.png)

In this example we want to start our Robot using the [Robocorp Process API](https://robocorp.com/docs/robocorp-cloud/api/process-api). 

:exclamation:**Attention**:
Unfortuntaely within the free account option it is not possible use the API to start a Robot. In order to do so the **Flex Account** is needed.

If you have the access to "trigger-process" from the Robocorp API, you can upload a Robot to the Robocloud. This can be done via commandline, link to the github repo of your Robot or via file upload. The RF-Forum-Bot follows the basic [structure guidelines](https://robocorp.com/docs/setup/robot-structure) of Robocorp. Therefore it contains attionally a robot.yaml and a conda.yaml. You can upload the compressed file directly to your Robocorp Cloud. 

Within the Cloud under the tab workforce you can define processes. Create a new process and configure the process. Within the configuration you can add steps. Here you can now select from your uploaded Robots. 

In order to use the Robocorp API you need to create an API Key. More information and a detailed instruction video is [here](https://robocorp.com/docs/robocorp-cloud/api). 

Please be aware that you need to have a paying plan where "triggering process" is enabled.

If that is true, you can include your credentials to the External-Task-handler.py. In this setup the External-Task-handler preforms a REST call in order to 



## Run the project
1. Start Camunda (you can use [Docker](https://github.com/camunda/docker-camunda-bpm-platform) or [Camundarun](https://docs.camunda.org/manual/7.15/installation/camunda-bpm-run/))
2. Deploy the process Diagramm to Camunda
3. Start a process instance
4. Install needed Python modules for each RF-Worker. Run '''pip install -r install/requirements.txt'''
5. Start the External-task-handler Python scripts in each RF Worker folder '''python3 External-task-handler.py'''
6. Observer your results in Cockpit, the log.hmtl and Robocorp of each RF Worker