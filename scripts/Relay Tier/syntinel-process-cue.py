from __future__ import print_function # Python 2/3 compatibility
from urllib import parse
import json
import boto3
import time
import uuid

def lambda_handler(event, context):
    
    queryString = event.get('_qs')

    # Values came in on the query string, parse them into the json structure
    if queryString :
        qs = parse.parse_qs(queryString)
        variables = []
        for key in qs:
            values = qs.get(key)
            if key == 'id':
                id = values[0]
            elif key == 'cue':
                cue = values[0]
            else :
                variable = { "name" : key, "values" : values }
                variables.append(variable)
        event = {
            "id" : id,
            "cue" : cue,
            "variables": variables
        }
                
    # Process Cue Json Structure
    id = event.get('id')
    cue = event.get('cue')
    variables = event.get('variables')
    ts = str(time.time())
    actionId = str(uuid.uuid4())
    
    event.pop("id")
    event.update({ "_ts": ts, "_status": "New" })

    # Update Signal Record in DynamoDB
    db = boto3.resource('dynamodb', region_name='us-east-1')
    table = db.Table('syntinel-signals')
    record = table.get_item(Key={'_id': id})
    item = record.get('Item')
    
    if item:
        dbAction = { actionId: event }
        actions = item.get('actions')
        if actions :
            actions.update(dbAction)
        else :
            actions = dbAction  
        
        updateInfo = { '_status': 'Received', 'actions': actions }
        item.update(updateInfo)
        table.put_item(Item=item)
        
        #TODO : Call Resolver From Signal Message
        
        # Mock Call To "Resolver Lambda"
        lam = boto3.client('lambda')
        lam.invoke(FunctionName='MyTestResolver', InvocationType='RequestResponse', Payload=json.dumps(event))

        # Update Action Status To "Sent"
        action = item.get('actions').get(actionId)
        action.update( {'_status': 'Sent' } )
        table.put_item(Item=item)
    
    else :
        raise ValueError('Signal [' + id + '] Not Found.')

    reply = {
        'statusCode': 200,
        'id': id,
        'actionId': actionId,
        'ts': ts
    }
    
    return json.dumps(reply)
