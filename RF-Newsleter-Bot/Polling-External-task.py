import time

from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

import robot

# configuration for the Client
default_config = {
    "maxTasks": 1,
    "lockDuration": 1,
    "asyncResponseTimeout": 5000,
    "retries": 3,
    "retryTimeout": 5000,
    "sleepSeconds": 30
}


def handle_task(task: ExternalTask) -> TaskResult:    
    
    # Put variables into a list for the RF-task
    worker_id = 'worker_id:worker1'    
    variables =[worker_id]
       
    #start RF-task
    robotOutput = robot.run("signUp.robot", variable=variables)
    print(robotOutput);     
    

ExternalTaskWorker(worker_id="worker1",config=default_config).subscribe("SignUp", handle_task)