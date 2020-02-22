import os
import json
import logging
import boto3
from botocore.exceptions import ClientError
import datetime
import traceback
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Setup and Configure DynamoDB
    if os.environ['AWSENV'] == "AWS_SAM_LOCAL":
        merged_boxes_table = boto3.resource('dynamodb', endpoint_url="http://dynamodb:8000").Table('mergedboxes')
    else:
        merged_boxes_table = boto3.resource('dynamodb', region_name=os.environ['REGION']).Table(os.environ['TABLE'])

    # GET Method
    if event['httpMethod'] == 'GET':
        logger.info('GET Method')
        # Check QueryStringParameters
        try: 
            logger.info('Look for the queryStringParameters')
            queryjson = (event["queryStringParameters"])
        except:
            return {'statusCode' : 400, 'body' : 'Invalid JSON for the Function'}

        # Lambda Function to get the migrated box from DynamoDB table
        if 'Id' in queryjson:
            try:
                logger.info('Fetching data from DynamoDB')
                response = merged_boxes_table.get_item(Key = {'Id' : queryjson['Id']})
            except ClientError as e:
                logger.info('Error fetching the data: ' + e.response['Error']['Message'])
                return {'statusCode' : 400, 'body' : e.response['Error']['Message']}
            else:
                item = response['Item']
                logger.info('Item fetched')
                
                return {'statusCode' : 200, 'headers': { 'Content-Type': 'application/json' }, 'body' : json.dumps(item, cls=CustomJsonEncoder)}
        else:
            logger.info('Id key was not provided')
            return {'statusCode' : 400, 'body' : 'Necesary Key not Provided'}
    # POST Method
    elif event['httpMethod'] == 'POST':
        logger.info('POST Method')
        # Check body JSON
        try: 
            logger.info('Load body as JSON')
            bodyjson = json.loads(event['body'])
        except:
            return {'statusCode' : 400, 'body' : 'Invalid JSON for the Function'}

        # Update item in the DynamoDB table with DateTime
        try:
            logger.info('Update Item in DynamoDB')
            response = merged_boxes_table.update_item(
                Key={'Id': bodyjson['Id']},
                UpdateExpression = 'SET Processed_time = :Processed_datetime',
                ExpressionAttributeValues={':Processed_datetime' : datetime.datetime.utcnow().isoformat()}
            )
        except:
            logger.info('Error updating Item in DynamoDB')
            traceback.print_exc()
            return {'statusCode': 400, 'body': 'Error updating item.'}
        else:
            logger.info('Return of the modified record in DynamoDB')
            get_response = merged_boxes_table.get_item(Key = {'Id' : bodyjson['Id']})
            item = get_response['Item']
            return {'statusCode': 200, 'body': json.dumps(item, cls=CustomJsonEncoder)}
            
class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return super(CustomJsonEncoder, self).default(obj)