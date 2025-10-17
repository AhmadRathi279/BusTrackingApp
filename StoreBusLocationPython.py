import json
import boto3
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BusLocation')  # ✅ Correct table name

def lambda_handler(event, context):
    try:
        print(f"Received event: {event}")

        body_raw = event.get('body')

        # Parse body correctly
        if isinstance(body_raw, str):
            body = json.loads(body_raw)
        else:
            body = body_raw

        bus_id = body.get('busId')
        latitude = body.get('latitude')
        longitude = body.get('longitude')

        if not bus_id or latitude is None or longitude is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing busId, latitude, or longitude"})
            }

        timestamp = datetime.utcnow().isoformat()

        # ✅ Make sure attribute name matches your key (BusID)
        table.put_item(Item={
            'BusID': str(bus_id),
            'Latitude': Decimal(str(latitude)),
            'Longitude': Decimal(str(longitude)),
            'Timestamp': timestamp
        })

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Location stored successfully"})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }