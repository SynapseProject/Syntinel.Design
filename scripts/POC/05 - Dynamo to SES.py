from __future__ import print_function # Python 2/3 compatibility
import json
import boto3

def lambda_handler(event, context):
    
    print(event)
    
    id = event['_id'][0]
    
    # Pretend to do something here
    

    # Update Signal Record in DynamoDB
    db = boto3.resource('dynamodb', region_name='us-east-1')
    table = db.Table('Syntinel')
    record = table.get_item(Key={'_id': id})
    item = record['Item']
    

    # "Resolve" Issue By Sending Email (Mockup)    
    client = boto3.client('ses')

    body = '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Email Reply</title></head><body><table>'

    for key in event :
        body = body + '<tr><td>' + key + '</td><td>' + json.dumps(event[key]) + '</tr>'
        print('>> Key : ' + key + ' : ' + json.dumps(event[key]))

    body = body + '</table></body></html>'
    print(body)
    
    source = 'test@craigandguy.com'
    destination = { 'ToAddresses' : ['guy.waguespack@gmail.com'],
                    'CcAddresses' : [],
                    'BccAddresses' : []}
    subject = 'Signal [' + id + "] Resolved."
    message = {'Subject': {'Data': subject}, 'Body': {'Html': {'Data': body}}}
    client.send_email(Source = source, Destination = destination, Message = message)

    
    
    updateInfo = { '_status': 'Resolved' }
    item.update(updateInfo)
    table.put_item(Item=item)

    
    return {
        'statusCode': 200,
        'body': 'Signal ' + id + ' Resolved.'
    }
