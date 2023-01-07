import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

queueURL = "https://sqs.us-east-1.amazonaws.com/436831233028/info" 

senderEmailId = "rp3111@columbia.edu" 

def lambda_handler(event, context):
    cuisine, emailID, phoneNumber, receiptHandle = pollSQS() 
    if cuisine == None or emailID == None:
        return None
    restaurantIds = fetchRestaurantFromES(event, cuisine)
    restaurantDetails = fetchRestaurantFromDynamo(restaurantIds) 
    response = sendEmailUsingSES(restaurantDetails, emailID, receiptHandle)
    return response

def pollSQS():
    sqsClient = boto3.client('sqs')
    response = sqsClient.receive_message(
        QueueUrl=queueURL,
        AttributeNames = ['All'],
        MessageAttributeNames = ['All'],
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20
    )
    #print("SQS Response:", response)
    if "Messages" not in response:
        print("No messages to poll. Retry")
        return None, None, None, None
    
    receiptHandle = response['Messages'][0]['ReceiptHandle']
    sqsClient.delete_message(QueueUrl=queueURL, ReceiptHandle=receiptHandle)
    
    cuisine = response['Messages'][0]['MessageAttributes']['Cuisine']['StringValue']
    phoneNumber = response['Messages'][0]['MessageAttributes']['Phone_Number']['StringValue']
    emailID = response['Messages'][0]['MessageAttributes']['Email']['StringValue']
    return cuisine, emailID, phoneNumber, receiptHandle


def fetchRestaurantFromES(event, cuisine):
    # print(cuisine)
    region = 'us-east-1' 
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    host = 'https://search-finalrestaurants-syz5r6acw2zmj3gblcras3xdru.us-east-1.es.amazonaws.com/' 
    index = 'restaurants'
    url = host + index + '/_search'
    query = {
        "size": 2,
        "query": {
            "match": {"cuisine_tags": cuisine}
        }
    }
    #print(query)
    headers = { "Content-Type": "application/json" }
    r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }
    response['body'] = r.text
    response['body'] = json.loads(response['body'])
    #print("responese body",response['body'])
    matches = response['body']['hits']['hits']
    #print(matches)
    restaurantIds = [restaurant['_id'] for restaurant in matches]
    #print(restaurantIds)
    return restaurantIds 
    
def fetchRestaurantFromDynamo(restaurantIds):
    """
    Fetches all the restaurant details by restaurantID from dynamo DB.
    """
    dynamoClient = boto3.client('dynamodb')
    restaurantList = []
    print(restaurantIds)
    for restaurantId in restaurantIds:
        response = dynamoClient.get_item(
            TableName="Yelp-Restaurants",
            Key={
                "id": {
                    "S": restaurantId #s means string and restaurantID is the value of id
                }
            }
        )
        
        print(response['Item'])
        restaurantList.append(response['Item'])
    return restaurantList
   
def sendEmailUsingSES(restaurantDetailsSet, emailID, receiptHandle):

    sesClient = boto3.client('ses')
    sqsClient = boto3.client('sqs')
    
    message = "Hi, We have found a restaurant we know you'll like!:\n"
    message_restaurant = ""
    count = 1
    for restaurant in restaurantDetailsSet:
        restaurantName = restaurant['name']['S']
        restaurantAddress = ""
        for address in restaurant['location']['M']['display_address']['L']:
            restaurantAddress += address['S']
            restaurantAddress += ", "
        reviewCount = restaurant['review_count']['N']
        ratings = restaurant['rating']['N']
        cuisine = restaurant['cuisine_tags']['L'][0]['S']
        print(cuisine)
        message_restaurant += str(count)+" RestaurantName: {}, Address: {}, Ratings: {}, Reviews: {}, Cuisine: {} \n".format(restaurantName, restaurantAddress, ratings, reviewCount, cuisine)
        count += 1

    mailResponse = sesClient.send_email(
        Source=senderEmailId,
        Destination={'ToAddresses': [emailID]},
        Message={
            'Subject': {
                'Data': "Dining Conceirge Chatbot's personalized suggestion for you!",
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': message+message_restaurant,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': message+message_restaurant,
                    'Charset': 'UTF-8'
                }
            }
        }
    )

    print("deleting the message from queue")
    sqsClient.delete_message(QueueUrl=queueURL, ReceiptHandle=receiptHandle)
    return mailResponse