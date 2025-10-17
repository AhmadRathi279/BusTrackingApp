import json
import boto3

dynamodb = boto3.resource('dynamodb')

BUSES_TABLE = 'Buses'
COUNTER_TABLE = 'Counters'

def get_next_bus_id():
    counter_table = dynamodb.Table(COUNTER_TABLE)
    response = counter_table.update_item(
        Key={'counter_name': 'bus_id'},
        UpdateExpression='SET counter_value = if_not_exists(counter_value, :start) + :inc',
        ExpressionAttributeValues={
            ':start': 0,
            ':inc': 1
        },
        ReturnValues='UPDATED_NEW'
    )
    return int(response['Attributes']['counter_value'])

def lambda_handler(event, context):
    print("Event:", event)

    # --- Parse body safely ---
    body_raw = event.get('body')
    try:
        body = json.loads(body_raw or '{}') if isinstance(body_raw, str) else body_raw
    except Exception as e:
        print("Body JSON decode error:", str(e))
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request body'})
        }

    bus_name = body.get('name')
    if not bus_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Bus name is required'})
        }

    try:
        # --- Generate new numeric ID ---
        bus_id = get_next_bus_id()

        # --- Insert into Buses table ---
        buses_table = dynamodb.Table(BUSES_TABLE)
        buses_table.put_item(
            Item={
                'ID': str(bus_id),   # ✅ Must match your DynamoDB primary key name
                'Name': bus_name
            }
        )

        print(f"Bus created successfully — ID: {bus_id}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Bus created successfully',
                'bus_id': bus_id,
                'name': bus_name
            })
        }

    except Exception as e:
        print("Error occurred:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }