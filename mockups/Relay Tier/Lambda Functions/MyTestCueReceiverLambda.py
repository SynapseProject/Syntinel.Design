from __future__ import print_function # Python 2/3 compatibility
from urllib import parse
import json
import boto3

def lambda_handler(event, context):
    
    queryString = event['body']
    qs = parse.parse_qs(queryString)
    
    id = qs['_id'][0]
    cue = qs['_cue'][0]
    
    # Update Signal Record in DynamoDB
    db = boto3.resource('dynamodb', region_name='us-east-1')
    table = db.Table('Syntinel')
    record = table.get_item(Key={'_id': id})
    item = record['Item']
    
    updateInfo = { '_status': 'Received', '_cue': cue }
    item.update(updateInfo)
    table.put_item(Item=item)
    
    # Mock Call To "Resolver Lambda"
    lam = boto3.client('lambda')
    lam.invoke(FunctionName='MyTestResolver', InvocationType='RequestResponse', Payload=json.dumps(qs))

    # TODO implement
    return {
        'statusCode': 200,
        'body': 'Resolved'
    }

