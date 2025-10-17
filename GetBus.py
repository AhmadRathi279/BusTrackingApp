import json
import boto3

dynamodb = boto3.resource('dynamodb')
BUSES_TABLE = 'Buses'

def lambda_handler(event, context):
    print("Event:", event)

    try:
        buses_table = dynamodb.Table(BUSES_TABLE)
        response = buses_table.scan()

        buses = response.get('Items', [])
        print(f"Retrieved {len(buses)} buses")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'buses': buses
            }, default=str)
        }

    except Exception as e:
        print("Error occurred:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }