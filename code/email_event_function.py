import json
import boto3
from botocore.exceptions import ClientError
import re

def lambda_handler(event, context):
    print("Lambda function is triggered by EventBridge.")
    print(event['detail']['eventName'])
    eventName = event['detail']['eventName']
    my_session = boto3.session.Session()
    my_region = my_session.region_name
    resource_config = event['ResourceProperties']

    if eventName == 'CreateUserProfile':
        recipient_email = event['detail']['requestParameters']['singleSignOnUserValue']
        print("recipient_email: ", recipient_email)
        
        subject = "Congratulations! Amazon SageMaker Studio access granted."
        body_text = ("Congratulations!)\r\n"
             "You have been granted access to Amazon SageMaker Studio "
             "You can login using your AWS SSO credentials."
            )
        body_html = """<html>
            <head></head>
            <body>
              <h3> Congratulations! You have been granted access to Amazon SageMaker Studio. </h3>
              <p> You can login using your AWS SSO credentials. </p>
            </body>
            </html>
                        """  
        send_email(recipient_email, subject, body_text, body_html, my_region, resource_config)
    else: 
        principalId = event['detail']['userIdentity']['principalId']
        print("full string: ", principalId)
        pattern = re.compile(":")
        result = re.split(pattern, principalId)
        recipient_email = result[1]
        print("recipient_email: ", recipient_email)
        subject = "Your Amazon SageMaker Studio access has been revoked."
        body_text = ("Amazon SageMaker Studio)\r\n"
             "Access has been revoked. "
             "You will no longer be able to login using your AWS SSO credentials."
            )
        body_html = """<html>
            <head></head>
            <body>
              <h3> Amazon SageMaker Studio access has been revoked. </h3>
              <p> You will no longed be able to login using your AWS SSO credentials. </p>
            </body>
            </html>
                        """  
        send_email(recipient_email, subject, body_text, body_html, my_region, resource_config)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Email sent successfully!')
    }

def send_email(recipient_email, subject, body_text, body_html, my_region,config ):
    # Change the items with: ######Change Me#######
    SENDER = config['email'] ######Change Me#######
    print("email address: ", SENDER)
    RECIPIENT = recipient_email
    AWS_REGION = my_region  ######Change Me#######
    print('Region: ',AWS_REGION)
    
    SUBJECT = subject
    BODY_TEXT = body_text
    BODY_HTML = body_html
    CHARSET = "UTF-8"
    client = boto3.client('ses',region_name=AWS_REGION)
    try:
    #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        
    return response['MessageId']
