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
        signalId = event.get('id')
        token = channel.get('config', {}).get('bearerToken')
        target = channel.get('target')
        conversationId = getConversationId(token)
        body = CreateSlackMessage(signalId, signal, target)
        botReply = sendMessage(conversationId, token, body)

    reply = {
        'statusCode': 200,
        'reply': botReply
    }
    
    print("Reply:", reply)
    return reply

def getConversationId(token):
    conversationId = None
    url = 'https://directline.botframework.com/v3/directline/conversations'
    headers = {
        "Authorization": "Bearer " + token
    }

    response = requests.post(url, headers=headers)

    if (response.ok) :
        status = response.status_code
        content = json.loads(response.content)
        conversationId = content.get('conversationId')
        
    return conversationId

def sendMessage(conversationId, token, body):
    content = None
    url = 'https://directline.botframework.com/v3/directline/conversations/' + conversationId + '/activities'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }

    msgResponse = requests.post(url, headers=headers, data=json.dumps(body))
    if (msgResponse.ok) :
        status = msgResponse.status_code
        content = json.loads(msgResponse.content)

    return content
    
def CreateSlackMessage(signalId, signal, recipient):
    mainTitle = signal.get('name', "Alert") + " : " + signal.get('description')
    
    message = {
        "type": "message",
        "from": {
            "id": signalId
        },
        "text": "notify " + recipient,
        "value": {
            "text": mainTitle,
            "attachments": [],
            "valueType": "application/json"
        }
    }
    
    cues = signal.get('cues', {})
    attachments = message.get('value').get('attachments')
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
        'actions': []
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