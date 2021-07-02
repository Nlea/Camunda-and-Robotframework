import time

from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

import robot


def handle_task(task: ExternalTask) -> TaskResult:
    
    # get Variables from the process
    emailAddress = task.get_variable("email")
    newsletter = task.get_variable("newsletter")
    forum = task.get_variable("forum")
    username = task.get_variable("usernameForum")
    subject = "Welcome to the Camunda Community"

    if(newsletter and not forum):
        body = "You are signed up for the Camunda Community Newsletter"
    elif(forum and not newsletter):
        body = "A Forum account has been created, Your choosen username is: " + username +"Your password is: communityRocks! Make sure to change your password at your first Login."
    elif(forum and newsletter):
        body ="You are subscribed to the Camunda Community Newsletter and a Forum account has been created, Your choosen username is: " + username +"Your password is: communityRocks! Make sure to change your password at your first Login."
    else:
        body = "You have not signed up for the Forum or the Community Newsletter. You might want to do it later "

    # Put variables into a list for the RF-task
    email = 'email:'+ emailAddress
    body = 'body:'+ body
    subject= 'subject:'+ subject
    
    variables =[email, body, subject]
       
    #start RF-task
    robotOutput = robot.run("mailing.robot", variable=variables)
    
    # send failure if RF does not completed successfully
    if(robotOutput!= 0):        
        return task.failure(error_message="RF-task failed",  error_details="The RF task was not completed successfully. For more information open the log.html from the RF task ", 
                            max_retries=0, retry_timeout=5000)
        
    
    # complete task, if RF task completed successfully    
    return task.complete({"emailSent": True})

ExternalTaskWorker(worker_id="1").subscribe("SendMail", handle_task)