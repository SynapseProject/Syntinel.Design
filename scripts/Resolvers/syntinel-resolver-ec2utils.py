from __future__ import print_function # Python 2/3 compatibility
import json
import boto3

def lambda_handler(event, context):
    
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
            print (">>> Instances :", instances)
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

    return {
        'statusCode': 200,
        'body': rc,
        'statusMessage': "Success"
    }

def array2dictionary(array, indexBy):
    retDict = {}
    for node in array:
        key = node.get(indexBy)
        if key:
            retDict[key] = node

    return retDict
