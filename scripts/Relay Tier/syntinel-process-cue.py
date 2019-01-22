from __future__ import print_function # Python 2/3 compatibility
from urllib import parse
import json
import boto3
import time
import random

def lambda_handler(event, context):
    
    print("Event:", event)
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
    actionId = getResponseId()
    
    event.pop("id")
    event.update({ "_ts": ts, "_status": "New", "_isValid": True })

    # Update Signal Record in DynamoDB
    db = boto3.resource('dynamodb', region_name='us-east-1')
    table = db.Table('syntinel-signals')
    record = table.get_item(Key={'_id': id})
    item = record.get('Item')
    
    if item:
        signal = item.get("signal")

        validateCue(event, item)
        
        dbAction = { actionId: event }
        actions = item.get('actions')
        if actions :
            actions.update(dbAction)
        else :
            actions = dbAction  
        
        updateInfo = { '_status': 'Received', 'actions': actions }
        item.update(updateInfo)
        table.put_item(Item=item)
        
        try:
            cueId = event.get("cue")
            cue = signal.get("cues", {}).get(cueId)
            resolver = cue.get("resolver")
            function = resolver.get("function")
            config = resolver.get("config")
        except:
            raise Exception("Unable To Find Resolver For Cue [" + cueId + "]")
            
        request = {
            'id': id,
            'actionId': actionId,
            'cue': cueId,
            'variables': event.get('variables', []),
            'config': config
        }
        
        # Call Lambda Function (Resolver)
        lam = boto3.client('lambda')
        rc = lam.invoke(FunctionName=function, InvocationType='Event', Payload=json.dumps(request))
        
        # Update Action Status To "Sent"
        action = item.get('actions').get(actionId)
        action.update( {'_status': 'Sent' } )
        table.put_item(Item=item)
    
    else :
        raise ValueError('Signal [' + id + '] Not Found.')

    reply = {
        'statusCode': rc.get('StatusCode', 0),
        'id': id,
        'actionId': actionId,
        'ts': ts
    }
    
    print("Reply:", reply)
    return reply

# Generate Random Response Id and Check It Doesn't Already Exist
def getResponseId():
    id = None
    id = getId()
    id = "CUE-"+id

    if (not id):
        raise Exception('Unable To Generate Unique Id.')
    
    return id

# Creates a 9 character, Base36 Encoded Id.
#   Based on curernt time and random numbers, this funciton will produce 9 character 
#   ids for over 67 years from epochOffset, after which it will generate 10 character ids.
def getId():
    id = None
    ephocOffset = 1546300800    # 1-JAN-2019 00:00:00 GMT
    now = int(time.time())
    t = base36encode(str(now - ephocOffset))            
    r = base36encode(str(random.randint(0, 46655)))     # Create Random 3-Char Trailer For Uniqueness Within Same Second
    
    id = t.zfill(6) + r.zfill(3)
    return id

# https://stackoverflow.com/questions/2104884/how-does-python-manage-int-and-long
def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    number = int(number)
    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36

def base36decode(number):
    return int(number, 36)
    
def validateCue(event, item):
    id = item.get('_id')
    
    # Check if Signal Message Is Still Active
    isActive = item.get('_isActive')
    if (isActive != True):
        raise Exception("Signal [" + id + "] Is Not Active.")
        
    # Check to see if maximum number of valid replies has been exceeded.
    maxReplies = item.get('signal',{}).get('maxReplies', 0)
    if maxReplies > 0:
        actions = item.get("actions", {})
        validActionCount = 0
        for action in actions:
            if (actions.get(action,{}).get('_isValid', True)):
                validActionCount += 1
        
        if (validActionCount >= maxReplies):
            raise Exception("Signal [" + str(id) + "] Has Exceeded the Maximum Valid Replies Allowed.")
