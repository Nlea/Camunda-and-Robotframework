import time

from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

import robot


def handle_task(task: ExternalTask) -> TaskResult:
    
    # get Variables from the process
    emailAddress = task.get_variable("email")
    body = task.get_variable("body")
    subject = task.get_variable("subject")
    
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