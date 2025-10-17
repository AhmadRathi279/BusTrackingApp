import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
BUS_LOCATIONS_TABLE = 'BusLocation'
USERS_TABLE = 'Users'
BUSES_TABLE = 'Buses'

def lambda_handler(event, context):
    print("Event:", event)

    try:
        # Fetch all bus locations
        locations_table = dynamodb.Table(BUS_LOCATIONS_TABLE)
        locations_response = locations_table.scan()
        locations = locations_response.get('Items', [])

        if not locations:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No bus locations found'})
            }

        result = []
        users_table = dynamodb.Table(USERS_TABLE)
        buses_table = dynamodb.Table(BUSES_TABLE)

        for location in locations:
            bus_id_str = location.get('BusID')
            print(f"Processing BusID (string): {bus_id_str}")

            # ✅ Convert BusID to number for comparison with Users table
            try:
                bus_id_num = int(bus_id_str)
            except (TypeError, ValueError):
                bus_id_num = None

            # ✅ Fetch bus details using ID as primary key in Buses
            bus_response = buses_table.get_item(Key={'ID': bus_id_str})
            bus = bus_response.get('Item', {})
            bus_name = bus.get('Name', 'Unknown')

            # ✅ Fetch driver details (BusID = numeric match)
            driver_name = 'Unknown'
            if bus_id_num is not None:
                user_response = users_table.scan(
                    FilterExpression=Attr('BusID').eq(bus_id_num)
                )
                user_items = user_response.get('Items', [])
                if user_items:
                    user = user_items[0]
                    first_name = user.get('First Name', '')
                    last_name = user.get('Last Name', '')
                    driver_name = f"{first_name} {last_name}".strip() or 'Unknown'

            # ✅ Append combined info
            result.append({
                'BusID': bus_id_str,
                'Latitude': float(location.get('Latitude', 0)),
                'Longitude': float(location.get('Longitude', 0)),
                'Timestamp': location.get('Timestamp', ''),
                'DriverName': driver_name,
                'BusName': bus_name
            })

        return {
            'statusCode': 200,
            'body': json.dumps(result, default=str)
        }

    except Exception as e:
        print("General error:", str(e))
        import traceback; traceback.print_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }