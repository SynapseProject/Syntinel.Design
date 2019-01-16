from __future__ import print_function # Python 2/3 compatibility
from botocore.vendored import requests
import json
import uuid
import os

def lambda_handler(event, context):

    signal = event.get('signal', {})
    signalId = event.get('_id')
    print(">> SignalId :", signalId)
    conversationId = getConversationId()
    print(">> Conversation Id :", conversationId)
    
#    body = {"from": {"id": "eb571575-0d05-424d-b854-ff7edc4ee388"}, "valueType": "application/json", "type": "message", "value": {"text": "Your EC2 Instance \"i-06a81abcd8caa4843\" in \"WU2-P1-0390\" Is Running Hot (CPU > 80% over an hour).", "attachments": [{"callback_id": "0813785c-35d7-4579-ac89-5f09b7be78f2", "text": "Resize your EC2 instance to the next biggest size in the same class.", "actions": [{"type": "select", "name": "Resize", "value": "1", "options": [{"text": "t2.nano", "value": "t2.nano"}, {"text": "t2.micro", "value": "t2.micro"}, {"text": "t2.medium", "value": "t2.medium"}]}, {"text": "Ignore this alert", "type": "button", "name": "Ignore", "value": "2"}, {"text": "Disable CPU Monitoring", "type": "button", "name": "Disable", "value": "3"}], "color": "good"}]}, "text": "notify #syntinel@slack"}
    
    body = CreateSlackMessage(signalId, signal, "#syntinel@slack")
    
    print(body)

#    reply = sendMessage(conversationId, body)
    
    return {
        'statusCode': 200,
        'body': body
    }

def getConversationId():
    conversationId = None
    url = 'https://directline.botframework.com/v3/directline/conversations'
    headers = {
        "Authorization": "Bearer " + os.environ['BearerToken']
    }

    response = requests.post(url, headers=headers)

    if (response.ok) :
        status = response.status_code
        content = json.loads(response.content)
        conversationId = content.get('conversationId')
        
    return conversationId

def sendMessage(conversationId, body):
    content = None
    url = 'https://directline.botframework.com/v3/directline/conversations/' + conversationId + '/activities'
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.environ['BearerToken']
    }

    msgResponse = requests.post(url, headers=headers, data=json.dumps(body))
    print(msgResponse.json())
    if (msgResponse.ok) :
        status = msgResponse.status_code
        content = json.loads(msgResponse.content)
        print(json.dumps(content))
    
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
    print(">> Attachments :", attachments)
    for cue in cues:
        attachment = CreateAttachment(cue, cues.get(cue))
        attachments.append(attachment)

    return message
    
def CreateAttachment(cueId, cue):
    cueTitle = cue.get('name', "Alert") + " : " + cue.get('description')
    
    attachment = {
        'text': cueTitle,
        'callback_id': "1234567890",
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
        newAction.update( { 'actions': options } )
        newAction.update( { 'actions': options } )
        
    elif type == 'button':
        newAction.update( { 'type': 'button' } )
        newAction.update( { 'text': description } )
    
    if defaultValue:
        newAction.update( { 'value': defaultValue } )
        

        
    print(">>> Action:", action)
    return newAction