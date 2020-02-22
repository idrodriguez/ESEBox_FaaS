import datetime
import json
import logging
import os

import bson.objectid
import pymongo

# DB Connection and Definitions
db_client = pymongo.MongoClient(os.environ['MONGODB_URI'])
db = db_client[os.environ['MONGODB_DB']]
db_col_records = db[os.environ['MONGODB_CL_HR']] 

# Logger definition
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Lambda function to get the migrated box from DB
def get_hr_merged_box(event, context):
    # Check QueryStringParameters
    try: 
        logger.info('Look for the queryStringParameters')
        queryjson = (event["queryStringParameters"])
    except:
        return {'statusCode' : 400, 'body' : 'Invalid JSON for the Function'}

    # Query setup
    logger.info('Create mongo db query with the boxes passed')
    boxes = [str(box) for box in queryjson.values()]
    query = { 'Box' : {"$in": boxes} }
        
    # Fetch from DB
    try:
        logger.info('Fetch from mongo db using query: ' + str(query))
        medical_records = list(db_col_records.find(query))
    except Exception as e:
        return {'statusCode' :  400, 'body': e.args[0]}

    return {
        'statusCode' : 200,
        'body': json.dumps(medical_records, default=objectid_handler),
    }

# MongoDB ObjectId Handler
def objectid_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    elif isinstance(x, bson.objectid.ObjectId):
        return str(x)
    else:
        raise TypeError(x)