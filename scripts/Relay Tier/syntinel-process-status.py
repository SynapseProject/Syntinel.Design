from __future__ import print_function # Python 2/3 compatibility
from urllib import parse
import json
import boto3
import time
import random

def lambda_handler(event, context):
    
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
        if action:
            if status:
                action.update( { "_status": status } )
            if isValidReply == False:
                action.update( { '_isValid': False } )
            if data:
                ts = str(time.time())
                trace = action.get('_trace',{})
                trace.update( { ts : data } )
                action.update( { '_trace': trace } )

        if status:
            item.update( { '_status': status } )

        if closeSignal:
            item.update( { '_isActive': False } )
            
        table.put_item(Item=item)

    else :
        raise ValueError('Signal [' + id + '] Not Found.')

    reply = {
        'statusCode': 200
    }
    
    return reply
