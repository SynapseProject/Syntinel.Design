from __future__ import print_function

import json
import boto3

print('Loading function')


def lambda_handler(event, context):
    client = boto3.client('ses')

    record = json.loads(event['Records'][0]['Sns']['Message'])
    id = record['Keys']['_id']['S']
    
    body = '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Email Reply</title></head><body><h1>CPU Montior</h1><p>Your EC2 Instance is Running Hot (CPU > 80% over an hour)<hr><h2>Resize</h2><p>Resize your EC2 instance to a bigger size in the same class.<form id="form1" action="https://iveplpzxtk.execute-api.us-east-1.amazonaws.com/syntinel-poc/cue" method="POST"><div style="margin-bottom:10px"><label for="size">Size</label><br><select id="size" name="size"><option value="t2.nano" selected>t2.nano</option><option value="t2.micro">t2.micro</option><option value="t2.small">t2.small</option></select></div><div style="margin-bottom:10px"><input type="checkbox" id="restart" name="restart" value="checkbox value" checked><label for="restart">Restart</label></div><div style="margin-bottom:10px"><label for="textarea">Comment</label><br><textarea cols="60" rows="5" name="comment" id="textarea">When they go low, we go lower.</textarea></div><input type="hidden" id="instanceid" name="instanceid" value="i-06a81abcd8caa4843"><input type="hidden" id="_id" name="_id" value="' + id + '"><input type="hidden" id="_cue" name="_cue" value="1"><div><button type="submit" name="Submit">Submit</button></div></form><hr><h2>Ignore</h2><p>Ignore the alert.<form id="form1" action="https://iveplpzxtk.execute-api.us-east-1.amazonaws.com/syntinel-poc/cue" method="POST"><div style="margin-bottom:10px"><label for="duration">Duration</label><br><input required type="text" id="duration" name="duration" value="7"></div><input type="hidden" id="instanceid" name="instanceid" value="i-06a81abcd8caa4843"><input type="hidden" id="_id" name="_id" value="' + id + '"><input type="hidden" id="_cue" name="_cue" value="2"><div><button type="submit" name="Submit">Submit</button></div></form><hr><h2>Disable</h2><p>Disable CPU Monitoring For This Instance.<form id="form1" action="https://iveplpzxtk.execute-api.us-east-1.amazonaws.com/syntinel-poc/cue" method="POST"><input type="hidden" id="instanceid" name="instanceid" value="i-06a81abcd8caa4843"><input type="hidden" id="duration" name="duration" value="-1"><input type="hidden" id="_id" name="_id" value="' + id + '"><input type="hidden" id="_cue" name="_cue" value="3"><div><button type="submit" name="Submit">Submit</button></div></form></body></html>'
    print(body)
    
    source = 'test@craigandguy.com'
    destination = { 'ToAddresses' : ['guy.waguespack@gmail.com'],
                    'CcAddresses' : [],
                    'BccAddresses' : []}
    message = {'Subject': {'Data': 'Signal [' + id + '] Received.'}, 'Body': {'Html': {'Data': body}}}
    client.send_email(Source = source, Destination = destination, Message = message)
    
    return message
