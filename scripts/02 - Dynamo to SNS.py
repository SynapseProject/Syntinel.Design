from __future__ import print_function
import boto3
import json

client = boto3.client('sns')
topic_arn = 'arn:aws:sns:us-east-1:121808128646:syntinel-alerts'

def lambda_handler(event, context):
    for record in event['Records']:
        eventName = record['eventName']
        if eventName == 'INSERT':
            id = record['dynamodb']['Keys']['_id']['S']
            record = json.dumps(record['dynamodb'])
            client.publish(TopicArn=topic_arn, Message=record, Subject='Syntinel Signal Received')
