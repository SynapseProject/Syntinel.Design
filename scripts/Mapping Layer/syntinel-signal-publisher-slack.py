from __future__ import print_function # Python 2/3 compatibility
from botocore.vendored import requests
import json
import os

def lambda_handler(event, context):

    conversationId = getConversationId()
    print(">> Conversation Id : ", conversationId)
    
    body = {
        "type": "message",
        "from": {
            "id": "eb571575-0d05-424d-b854-ff7edc4ee388"
        },
        "text": "notify #syntinel@slack",
        "value": {
            "text": "Your EC2 Instance \"i-06a81abcd8caa4843\" in \"WU2-P1-0390\" Is Running Hot (CPU > 80% over an hour).",
            "attachments": [{
                "text": "Resize your EC2 instance to the next biggest size in the same class.",
                "callback_id": "0813785c-35d7-4579-ac89-5f09b7be78f2",
                "color": "good",
                "actions": [{
                        "name": "Resize",
                        "type": "select",
                        "options": [{
                                "text": "t2.nano",
                                "value": "t2.nano"
                            },
                            {
                                "text": "t2.micro",
                                "value": "t2.micro"
                            },
                            {
                                "text": "t2.medium",
                                "value": "t2.medium"
                            }
                        ],
                        "value": "1"
                    },
                    {
                        "name": "Ignore",
                        "text": "Ignore this alert",
                        "type": "button",
                        "value": "2"
                    },
                    {
                        "name": "Disable",
                        "type": "button",
                        "text": "Disable CPU Monitoring",
                        "value": "3"
                    }
                ]
            }]
        }
    }
    
    reply = sendMessage(conversationId, body)
    
    return {
        'statusCode': 200,
        'body': json.dumps(reply)
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
    if (msgResponse.ok) :
        status = msgResponse.status_code
        content = json.loads(msgResponse.content)

    return content