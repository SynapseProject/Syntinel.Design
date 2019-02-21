from __future__ import print_function # Python 2/3 compatibility
from botocore.vendored import requests
import json
import uuid
import os

def lambda_handler(event, context):

    print("Event:", event)

    signal = event.get('signal', {})
    channel = event.get('channel')
    if channel:
        webhook = channel.get('target')
        signalId = event.get('id')
        body = CreateSlackMessage(signalId, signal)
        sendMessage(webhook, body)
    else:
        raise Exception ("Channel Information Was Not Provided.")

    reply = {
        'statusCode': 200
    }
    
    print("Reply:", reply)
    return reply

def sendMessage(webhook, body):
    content = None
    headers = {
        "Content-Type": "application/json"
    }

    msgResponse = requests.post(webhook, headers=headers, data=json.dumps(body))
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
    if type == 'Choice':
        newAction.update( { 'type': 'select' } )
        options = []
        for value in values:
            options.append( { 'text': values.get(value), 'value': value } )
        newAction.update( { 'options': options } )

    elif type == 'Button':
        newAction.update( { 'type': 'button' } )
        newAction.update( { 'text': description } )
    
    if defaultValue:
        newAction.update( { 'value': defaultValue } )

    return newAction