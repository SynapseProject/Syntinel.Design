from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import uuid

def lambda_handler(event, context):

    recordIds = []
    for record in event['Records']:
        recordId = str(uuid.uuid4())
        messageId = record['messageId']
        senderId = record['attributes']['SenderId']
        sentTimestamp = record['attributes']['SentTimestamp']
        body = record['body']

        if isinstance(body, str):
            body = json.loads(body)
        
        addlInfo = { '_status': 'New', "_id": recordId, '_messageid': messageId, '_senderId': senderId, '_sentTimestamp': sentTimestamp }
        body.update(addlInfo)
        
        db = boto3.resource('dynamodb', region_name='us-east-1')
        table = db.Table('Syntinel')
        
        table.put_item(Item=body)
        recordIds.append(recordId)
        
    response = {
        "statusCode": 200,
        "messageId": messageId,
        "processed": len(event['Records']),
        "recordIds": recordIds
    }
    
    return response