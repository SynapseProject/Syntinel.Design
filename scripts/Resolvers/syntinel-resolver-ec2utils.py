from __future__ import print_function # Python 2/3 compatibility
import json
import boto3
from botocore.vendored import requests
import os

def lambda_handler(event, context):
    
    print("Event:", event)
    signalId = event.get('id')
    actionId = event.get('actionId')

    variables = event.get("variables")
    if (variables):
        variables = array2dictionary(variables, "name")

        action = None
        try:
            action = variables.get("action").get("values")[0]
        except:
            print("ERROR : Required variable [action] not found.")
            
        try:
            cueId = event.get("cue")
            config = event.get("config")
        except:
            print("ERROR : Required variable [action] not found.")
            
        try:
            instances = config.get("instances")
        except:
            instances = None

        ec2 = boto3.client('ec2', region_name='us-east-1')
        rc = None
        if (action == "stop"):
            if (instances):
                rc = ec2.stop_instances(InstanceIds=instances)
                print(rc)
                print("Instances", instances, "stopped.")
            else:
                print("No Instances Specified.")
        elif (action == "start"):
            if (instances):
                rc = ec2.start_instances(InstanceIds=instances)
                print(rc)
                print("Instances", instances, "started.")
            else:
                print("No Instances Specified.")
        elif (action == "reboot"):
            if (instances):
                rc = ec2.reboot_instances(InstanceIds=instances)
                print(rc)
                print("Instances", instances, "rebooted.")
            else:
                print("No Instances Specified.")
        elif (action == "terminate"):
            if (instances):
                rc = ec2.terminate_instances(InstanceIds=instances)
                print(rc)
                print("Instances", instances, "terminated.")
            else:
                print("No Instances Specified.")
        elif (action == "hibernate"):
            if (instances):
                rc = ec2.hibernate_instances(InstanceIds=instances)
                print(rc)
                print("Instances", instances, "hibernated.")
            else:
                print("No Instances Specified.")
                
    setStatus(signalId, actionId, 'Completed', False, True, None)

    reply = {
        'statusCode': 200,
        'body': rc,
        'statusMessage': "Success"
    }
    
    print("Reply:", reply)
    return reply

def array2dictionary(array, indexBy):
    retDict = {}
    for node in array:
        key = node.get(indexBy)
        if key:
            retDict[key] = node

    return retDict

def setStatus(signalId, actionId, status, closeSignal, isValid, data):

    message = { "id": signalId }
    if actionId:
        message.update( { "actionId": actionId } )
    if status:
        message.update( { "status": status } )
    if closeSignal:
        message.update( { "closeSignal": closeSignal } )
    if isValid:
        message.update( { "isValidReply": isValid } )
    if data:
        message.update( { "data": data } )
        
    response = requests.post(os.environ['StatusUrl'], data=json.dumps(message))
