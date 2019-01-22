from __future__ import print_function # Python 2/3 compatibility
from botocore.vendored import requests
import json
import uuid
import os

def lambda_handler(event, context):

    print("Event:", event)

    for record in event.get('Records'):
        sns = record.get('Sns', {}).get('Message')
        if sns:
            sns = json.loads(sns)
            signal = sns.get('signal', {})
            signalId = sns.get('_id')
            body = CreateSlackMessage(signalId, signal)
            sendMessage(body)
            print(">>> Body :", body)

    reply = {
        'statusCode': 200
    }
    
    print("Reply:", reply)
    return reply

def sendMessage(body):
    content = None
    url = os.environ['WebHook']
    headers = {
        "Content-Type": "application/json"
    }

    msgResponse = requests.post(url, headers=headers, data=json.dumps(body))
    print(">>> MsgRsp :", msgResponse)
    print(">>> Content :", msgResponse.content)
    if (msgResponse.ok) :
        status = msgResponse.status_code

    return status
    
def CreateSlackMessage(signalId, signal):
    mainTitle = signal.get('name', "Alert") + " : " + signal.get('description')
    
    message = {
        "text": mainTitle,
        "attachments": [],
        "valueType": "application/json"
    }
    
    cues = signal.get('cues', {})
    attachments = message.get('attachments')
    for cue in cues:
        attachment = CreateAttachment(signalId, cue, cues.get(cue))
        attachments.append(attachment)

    return message
    
def CreateAttachment(signalId, cueId, cue):
    cueTitle = cue.get('name', "Alert") + " : " + cue.get('description')
    
    print(">>> SignalId:", signalId)
    print(">>> CueId :", cueId)
    
    attachment = {
        'text': cueTitle,
        'callback_id': signalId + "|" + cueId,
        'color': 'good',
        'actions': [],
    }
    
    for action in cue.get('actions'):
        attAction = CreateAction(action)
        attachment.get('actions').append(attAction)
    
    return attachment
    
def CreateAction(action):
    newAction = {}
    
    name = action.get('name')
    description = action.get('description')
    if name:
        newAction.update( { 'name': action.get('name') } )
        
    type = action.get('type')
    values = action.get('values', {})
    defaultValue = action.get('defaultValue')
    if type == 'choice':
        newAction.update( { 'type': 'select' } )
        options = []
        for value in values:
            for key in value:
                options.append( { 'text': value[key], 'value': key } )
        newAction.update( { 'options': options } )

    elif type == 'button':
        newAction.update( { 'type': 'button' } )
        newAction.update( { 'text': description } )
    
    if defaultValue:
        newAction.update( { 'value': defaultValue } )

    return newAction