from __future__ import print_function # Python 2/3 compatibility
from botocore.exceptions import ClientError
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
    dbRecord = { '_id': messageId, '_status': 'New', '_ts': ts, "signal": event }
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
    
    reply = {
        'statusCode': 200,
        'id': messageId,
        'ts': ts
    }

    return reply


# Generate Random Record Id and Check It Doesn't Already Exist
def getSignalId(table, tries = 5):
    id = None
    while tries > 0 :
        id = getId()
        try:
            table.put_item(Item={ '_id': id }, ExpressionAttributeNames={ '#id': '_id' }, ConditionExpression="attribute_not_exists(#id)")
            tries = 0   # Unique Id Found, Stop Looking
        except ClientError as e:
            code = e.response['Error']['Code']
            if (code == "ConditionalCheckFailedException"):
                print("WARNING : Id [",id,"] Already Exists.")
            else:
                print("ERROR :",e)
            tries -= 1
            id = None

    if (not id):
        raise Exception('Unable To Generate Unique Id.')
    
    return id

# Creates a 9 character, Base36 Encoded Id.
#   Based on curernt time and random numbers, this funciton will produce 9 character 
#   ids for over 67 years from epochOffset, after which it will generate 10 character ids.
def getId():
    id = None
    ephocOffset = 1546300800    # 1-JAN-2019 00:00:00 GMT
    now = int(time.time())
    t = base36encode(str(now - ephocOffset))            
    r = base36encode(str(random.randint(0, 46655)))     # Create Random 3-Char Trailer For Uniqueness Within Same Second
    
    id = t.zfill(6) + r.zfill(3)
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