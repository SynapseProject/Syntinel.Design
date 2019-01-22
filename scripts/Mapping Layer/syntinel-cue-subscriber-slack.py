import json
import boto3
import time
from urllib.parse import unquote
import html

def lambda_handler(event, context):
    
    print("Event:", event)
    
    slackReply = event.get('body-json')
    azureBotReply = event.get('Payload')
    if slackReply:
        if slackReply.startswith("payload="):
            print("SlackBot Reply")
            slackReply = slackReply.replace("payload=", "")
            slackReply = slackReply.replace("+", " ")
            slackReply = unquote(slackReply)
            slackReply = json.loads(slackReply)
    elif azureBotReply:
        print("AzureBot Service Reply")
        slackReply = azureBotReply
    else:
        print("Unknown Reply")
        slackReply = event

#    ts = str(int(time.time()))
#    fileName = "Reply-" + ts + "-SlackMessage.log"
#    rawFileName = "Reply-" + ts + "-SlackRaw.log"
    
#    s3 = boto3.client('s3')
#    s3.put_object(Body=json.dumps(slackReply), 
#        Bucket='guywaguespack-public', 
#        Key=fileName)
        
#    s3.put_object(Body=json.dumps(event), 
#        Bucket='guywaguespack-public', 
#        Key=rawFileName)
        
    callbackId = slackReply.get('callback_id')
    if '|' in callbackId:
        callbackId = callbackId.split("|")
        signalId = html.unescape(callbackId[0])
        cueId = html.unescape(callbackId[1])
    else:
        raise Exception("Unable To Parse SignalId From CallbackId [" + callbackId + "].")

    replyActions = slackReply.get("actions", [])
    
    cue = {
        'id': signalId,
        'cue': cueId,
        'variables': [
            {
                'name': 'action',
                'values': []
            }
        ]
    }
    
    values = cue.get('variables')[0].get('values')
    for replyAction in replyActions:
        replyType = replyAction.get('type')
        if replyType == 'button':
            action = replyAction.get('value')
            values.append(action)
        elif replyType == 'select':
            for option in replyAction.get('selected_options', []) :
                action = option.get('value')
                values.append(action)
        
    # Call Cue Processor
    function = "syntinel-process-cue"
    lam = boto3.client('lambda')
    rc = lam.invoke(FunctionName=function, InvocationType='RequestResponse', Payload=json.dumps(cue))

    payload = json.loads(rc['Payload'].read().decode("utf-8"))
    errorMessage = payload.get('errorMessage')
    replyId = payload.get("id", signalId)
    replyActionId = payload.get('actionId', "Unknown")

    if errorMessage:
        retStr = "Error Occured! - " + errorMessage + "- SignalId: [" + replyId + "], ActionId: [" + replyActionId + "]." 
    else:
        retStr = "Cue Received! - SignalId: [" + replyId + "], ActionId: [" + replyActionId + "]." 
        
    print("Reply:", retStr)
    return retStr