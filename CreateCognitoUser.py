import boto3
import os
import json

cognito_client = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')

USER_TABLE = 'Users'
COUNTER_TABLE = 'Counters'


def get_next_user_id():
    counter_table = dynamodb.Table(COUNTER_TABLE)
    response = counter_table.update_item(
        Key={'counter_name': 'user_id'},
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

    body_raw = event.get('body')
    print("Raw body:", body_raw)

    try:
        body = json.loads(body_raw or '{}')
    except Exception as e:
        print("Body JSON decode error:", str(e))
        body = {}

    print("Parsed body:", body)

    username = body.get('username')
    email = body.get('email')
    temp_password = body.get('temp_password')
    first_name = body.get('first_name')
    last_name = body.get('last_name')
    BusID = body.get('busId')

    if not all([username, email, temp_password]):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required fields.'})
        }

    try:
        user_pool_id = os.environ['USER_POOL_ID']
        print("Using user pool:", user_pool_id)

        # Create user in Cognito
        cognito_client = boto3.client('cognito-idp')
        response = cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            TemporaryPassword=temp_password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'}
            ],
            MessageAction='SUPPRESS',
            DesiredDeliveryMediums=['EMAIL']
        )

        print ("Cognito User Created: ", response)

         # Get next user ID from DynamoDB counter
        user_id = get_next_user_id()
        print("New user ID:", user_id)

        # Insert user record into DynamoDB user table
        user_table = dynamodb.Table(USER_TABLE)
        user_table.put_item(
            Item={ 
                'Id': str(user_id), 
                'email': email, 
                'Username': username, 
                'temp_password': temp_password, 
                'First Name': first_name, 
                'Last Name': last_name, 
                'BusID': BusID
            }
        )

        print(f"User saved to DynamoDB with id {user_id}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User created successfully',
                'username': response['User']['Username'], 
                'user_id': user_id
            })
        }

    except Exception as e:
        print("Error occurred:", str(e))
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }