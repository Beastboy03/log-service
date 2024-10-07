import json
import uuid
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key 

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('LogEntriess')

def save_logs(event, context):
    try:
        # Check if the event has 'body', as it would with API Gateway, or if it is a direct invocation
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event  # For direct invocation (like in test events)

        log_id = body.get('LogID', str(uuid.uuid4()))
        timestamp = body.get('DateTime', datetime.utcnow().isoformat())
        severity = body.get('Severity')
        message = body.get('Message')

        # Validating severity
        if severity not in ["info", "warning", "error"]:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Invalid severity level. Must be one of: info, warning, error'})
            }

        # Creating the log entry
        log_entry = {
            'LogID': log_id,
            'DateTime': timestamp,
            'Severity': severity,
            'Message': message
        }

        # Save to DynamoDB
        table.put_item(Item=log_entry)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Log entry created successfully', 'LogID': log_id})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }




def get_logs(event, context):
    try:
        # Query the 100 most recent entries, sorted by DateTime in descending order
        response = table.scan(Limit=100)
        items = response.get('Items', [])

        # Sort the items by DateTime in descending order
        sorted_items = sorted(items, key=lambda x: x['DateTime'], reverse=True)

        return {
            'statusCode': 200,
            'body': json.dumps(sorted_items)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }
