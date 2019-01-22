from __future__ import print_function # Python 2/3 compatibility
from urllib import parse
import json
import boto3
import time
import random

def lambda_handler(event, context):

    print("Event:", event)
    
    # Process Signal Json Structure
    id = event.get('id')
    actionId = event.get('actionId')
    status = event.get('status')
    closeSignal = event.get('closeSignal')
    isValidReply = event.get('isValidReply')
    data = event.get('data')
    updateDatabase = False
    
    # Update Signal Record in DynamoDB
    db = boto3.resource('dynamodb', region_name='us-east-1')
    table = db.Table('syntinel-signals')
    record = table.get_item(Key={'_id': id})
    item = record.get('Item')

    if item:
        signal = item.get("signal")
        actions = item.get("actions")
        action = item.get("actions", {}).get(actionId)
        ts = str(time.time())
        if action:
            if status:
                action.update( { "_status": status } )
            if isValidReply == False:
                action.update( { '_isValid': False } )
            if data:
                trace = action.get('_trace',{})
                trace.update( { ts : data } )
                action.update( { '_trace': trace } )
        else :
            # This is a signal-level status update, log request in signal trace logs
            trace = item.get('_trace', {})
            trace.update( { ts : { 'STATUS': event } } )
            item.update( { '_trace': trace } )

        if status:
            # TODO : Update Overall Status Based On Heirarchy
            item.update( { '_status': status } )

        if closeSignal:
            item.update( { '_isActive': False } )
            
        table.put_item(Item=item)

    else :
        raise ValueError('Signal [' + id + '] Not Found.')

    reply = {
        'statusCode': 200
    }
    
    print("Reply:", reply)
    return reply
