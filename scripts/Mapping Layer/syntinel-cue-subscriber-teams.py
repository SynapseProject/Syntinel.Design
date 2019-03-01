import json
import boto3
import time
from urllib.parse import unquote
import html

def lambda_handler(event, context):
    
    print("Event:", event)
    teamsReply = event
    
    ts = str(int(time.time()))
    fileName = "Reply-" + ts + "-TeamsMessage.log"
    rawFileName = "Reply-" + ts + "-TeamsRaw.log"
    s3 = boto3.client('s3')
    
    s3.put_object(Body=json.dumps(event), 
        Bucket='guywaguespack-public', 
        Key=rawFileName)

    callbackId = teamsReply.get('callback_id')
    if '|' in callbackId:
        callbackId = callbackId.split("|")
        signalId = html.unescape(callbackId[0])
        cueId = html.unescape(callbackId[1])
    else:
        raise Exception("Unable To Parse SignalId From CallbackId [" + callbackId + "].")

    event.pop('callback_id')
    cue = {
        'id': signalId,
        'cue': cueId,
        'variables': []
    }
    
    #TODO : Will Probably Have To Split Value By Commas For Multi-Value Field Types.
    for key in event:
        cue.get('variables').append({ 'name': key, 'values': [ event.get(key) ] })
    
    s3.put_object(Body=json.dumps(cue), 
        Bucket='guywaguespack-public', 
        Key=fileName)
        
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