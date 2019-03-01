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
        body = CreateAzureBotMessage(signalId, signal, target)
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
    
def CreateAzureBotMessage(signalId, signal, recipient):
    message = {
        "type": "message",
        "from": {
            "id": signalId
        },
        "text": "notify " + recipient,
        "valueType": "application/json"
    }

    targetArray = recipient.partition("@")
    if len(targetArray) == 3:
        channelType = targetArray[2].lower()
    else:
        raise Exception("Unable To Determine Channel Type For Azure Bot Service Recipient [" + recipient + "].") 

    if channelType == 'slack':
        value = CreateSlackMessage(signalId, signal, recipient)
    elif channelType == 'msteams':
        value = CreateTeamsMessage(signalId, signal, recipient)
    else:
        raise Exception("Unknown Channel Type [" + channelType + "].")

    message.update( { 'value': value } )

    return message
    
#########################################
# Slack Methods
#########################################

def CreateSlackMessage(signalId, signal, recipient):
    mainTitle = signal.get('name', "Alert") + " : " + signal.get('description')
    
    value = {
        "text": mainTitle,
        "attachments": []
    }
    
    cues = signal.get('cues', {})
    attachments = value.get('attachments')
    for cue in cues:
        attachment = CreateSlackAttachment(signalId, cue, cues.get(cue))
        attachments.append(attachment)

    return value
    
def CreateSlackAttachment(signalId, cueId, cue):
    cueTitle = cue.get('name', "Alert") + " : " + cue.get('description')
    
    attachment = {
        'text': cueTitle,
        'callback_id': signalId + "|" + cueId,
        'color': 'good',
        'actions': []
    }
    
    for action in cue.get('actions'):
        attAction = CreateSlackAction(action)
        if attAction:
            attachment.get('actions').append(attAction)
    
    return attachment

def CreateSlackAction(action):
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
            options.append( { 'text': values[value], 'value': value } )
        newAction.update( { 'options': options } )

    elif type == 'button':
        newAction.update( { 'type': 'button' } )
        newAction.update( { 'text': description } )
    
    if defaultValue:
        newAction.update( { 'value': defaultValue } )

    return newAction
    
#########################################
# Microsoft Teams Methods
#########################################
    
def CreateTeamsMessage(signalId, signal, recipient):
    mainTitle = signal.get('name', "Alert") + " : " + signal.get('description')
    
    value = {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "Container",
                "separator": False,
                "items": [
                    {
                        "type": "TextBlock",
                        "size": "Medium",
                        "weight": "Bolder",
                        "text": signal.get('name', "Syntinel Signal Received.")
                    },
                    {
                        "type": "TextBlock",
                        "size": "Medium",
                        "text": signal.get('description')
                    }
                ]
            }
        ],
        "actions": [],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.0",
        "fallbackText": "Version Not Supported."
    }
    
    cues = signal.get('cues', {})
    actions = value.get('actions')
    for cue in cues:
        card = CreateTeamsCard(signalId, cue, cues.get(cue))
        if len(cues) == 1:
            # Create Single Cue In Main Body of Message
            cardBody = card.get('body', [])
            for cardBodyItem in cardBody:
                value.get('body').append(cardBodyItem)
                
            cardActions = card.get('actions', [])
            for cardActionItem in cardActions:
                value.get('actions').append(cardActionItem)
        else:
            # Create Each Cue As An Action.ShowCard Button
            newAction = {
                "type": "Action.ShowCard",
                "title": cue,
                "card": card
            }
            value.get('actions').append(newAction)

    return value
    
def CreateTeamsCard(signalId, cueId, cue):
    card = {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "Container",
                "separator": True,
                "items": [
                    {
                        "type": "TextBlock",
                        "size": "Medium",
                        "weight": "Bolder",
                        "text": cue.get('name'),
                        "wrap": True
                    },
                    {
                        "type": "TextBlock",
                        "size": "Medium",
                        "text": cue.get('description'),
                        "wrap": True
                    }
                ]
            }
        ],
        "actions": []
    }
    
    actions = cue.get('actions', {})
    for action in actions:
        type = action.get('type')
        if type == "button":
            myAction = {
                "type": "Action.Submit",
                "id": "action",
                "title": action.get('name'),
                "data": {
                    "callback_id": signalId + "|" + cueId,
                    "action": action.get('defaultValue')
                }
            }
            card.get('actions').append(myAction)
        elif type == "choice":
            myAction = {
                "type": "Action.ShowCard",
                "title": action.get('name'),
                "card": {
                    "type": "AdaptiveCard",
                    "body": [],
                    "actions": [
                        {
                            "type": "Action.Submit",
                            "title": "Submit",
                            "data": {
                                "callback_id": signalId + "|" + cueId
                            }
                        }
                    ]
                }
            }

            myBody = {
                "type": "Container",
                "separator": True,
                "items": [
                    {
                        "type": "Input.ChoiceSet",
                        "id": "action",
                        "choices": []
                    }
                ]
            }
            
            for choice in action.get('values', {}):
                myChoice = {
                    "title": action.get('values').get(choice),
                    "value": choice
                }
                myBody.get('items')[0].get('choices').append(myChoice)

            myAction.get('card').get('body').append(myBody)
            card.get('actions').append(myAction)
            
    return card