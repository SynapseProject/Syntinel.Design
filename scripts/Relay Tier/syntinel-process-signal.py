from __future__ import print_function # Python 2/3 compatibility
import json
import boto3
import time
import random

def lambda_handler(event, context):

    # Setup Database Client
    db = boto3.resource('dynamodb', region_name='us-east-1')
    table = db.Table('syntinel-signals')

    # Create Random Message Id
    ts = str(time.time())
    messageId = getSignalId(table)
    
    if not messageId:
        raise Exception("Unable To Generate Unique Message Id.")
    
    # Write Signal To Dynamo Database
    dbRecord = { '_id': messageId, '_status': 'New', '_ts': ts, "Signal": event }
    table.put_item(Item=dbRecord)

    # Put Signal Onto SNS Topic
    sns = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-east-1:121808128646:syntinel-alerts'
    snsReply = sns.publish(TopicArn=topic_arn, Message=json.dumps(dbRecord), Subject='Syntinel Signal Received')

    snsMessageId = snsReply['MessageId']
    snsRequestId = snsReply['ResponseMetadata']['RequestId']

    # Update Signal Record With SNS Info
    addlInfo = { '_status': 'Sent', '_trace': { 'SNS': { 'MessageId': snsMessageId, 'RequestID': snsRequestId } } }
    dbRecord.update(addlInfo)
    table.put_item(Item=dbRecord)
    
    return {
        'statusCode': 200,
        'id': messageId,
        'ts': ts
    }

# Generate Random Record Id and Check It Doesn't Already Exist
def getSignalId(table, tries = 5):
    id = None
    while tries > 0 :
        # Generate 8 Digit Base36 Encoded String
        id = random.randint(78364164096, 2821109907455)
        id = base36encode(id)
        record = table.get_item(Key={'_id': id})
        item = record.get('Item')
        if (item):
            tries -= 1
            id = None
        else:
            tries = 0   # Unique Id Found, Stop Looking
    
    return id

# https://stackoverflow.com/questions/2104884/how-does-python-manage-int-and-long
def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    number = int(number)
    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36

def base36decode(number):
    return int(number, 36)