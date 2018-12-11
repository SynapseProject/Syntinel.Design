from __future__ import print_function # Python 2/3 compatibility
from urllib import parse
import json
import boto3
import time

def lambda_handler(event, context):
    
    queryString = event.get('_qs')

    # Values came in on the query string, parse them into the json structure
    if queryString :
        qs = parse.parse_qs(queryString)
        variables = []
        for key in qs:
            values = qs.get(key)
            if key == '_id':
                id = values[0]
            elif key == '_cue':
                cue = values[0]
            else :
                variable = { "name" : key, "values" : values }
                variables.append(variable)
        event = {
            "_id" : id,
            "_cue" : cue,
            "variables": variables
        }
                
    # Process Cue Json Structure
    id = event.get('_id')
    cue = event.get('_cue')
    variables = event.get('variables')
    ts = str(time.time())
    
    event.pop("_id")
    event.update({ "_ts": ts })
    
    # Update Signal Record in DynamoDB
    db = boto3.resource('dynamodb', region_name='us-east-1')
    table = db.Table('Syntinel')
    record = table.get_item(Key={'_id': id})
    item = record.get('Item')
    
    if item:
        cues = item.get('Cues')
        if cues :
            cues.append(event)
        else :
            cues = [ event ] 
        
        updateInfo = { '_status': 'Received', 'Cues': cues }
        item.update(updateInfo)
        table.put_item(Item=item)
        
        # Mock Call To "Resolver Lambda"
        lam = boto3.client('lambda')
        lam.invoke(FunctionName='MyTestResolver', InvocationType='RequestResponse', Payload=json.dumps(event))

    else :
        raise ValueError('Signal [' + id + '] Not Found.')

    reply = {
        'statusCode': 200,
        'id': id,
        'ts': ts
    }
    
    return json.dumps(reply)
