import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
USERS_TABLE = 'Users'
BUSES_TABLE = 'Buses'

def lambda_handler(event, context):
    print("Event:", event)

    email = event.get('queryStringParameters', {}).get('email')

    if not email:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Email is required'})
        }

    try:
        users_table = dynamodb.Table(USERS_TABLE)

        # ✅ Search user by email (email is not the partition key)
        response = users_table.scan(
            FilterExpression=Attr('email').eq(email)
        )

        items = response.get('Items', [])
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'User not found'})
            }

        user = items[0]
        bus_id = user.get('BusID')

        if not bus_id:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No bus assigned to this user'})
            }

        # ✅ Try both possible key names for bus lookup
        buses_table = dynamodb.Table(BUSES_TABLE)

        # Try with BusId
        try:
            bus_response = buses_table.get_item(Key={'ID': str(bus_id)})
            bus = bus_response.get('Item')
        except Exception as e:
            print("BusId key failed:", str(e))
            bus = None

        # # If not found, try with BusID (capital D)
        # if not bus:
        #     try:
        #         bus_response = buses_table.get_item(Key={'bID': str(bus_id)})
        #         bus = bus_response.get('Item')
        #     except Exception as e:
        #         print("BusID key failed:", str(e))

        if not bus:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Bus not found for BusID={bus_id}'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'bus_ID': bus.get('ID') or bus.get('BusID'),
                'name': bus.get('Name', 'Unnamed Bus')
            })
        }

    except Exception as e:
        print("Error occurred:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }