import boto3
# Define the client to interact with Lex
client = boto3.client('lexv2-runtime')

def lambda_handler(event, context):
    print(event)
    msg_from_user = event['messages'][0]['unstructured']['text']
    print(f"Message from frontend: {msg_from_user}")
    # Initiate conversation with Lex
    response = client.recognize_text(
            botId='WGVD0CEH7G', # MODIFY HERE
            botAliasId='PR9GJSTYOB', # MODIFY HERE
            localeId='en_US',
            sessionId='testuser',
            text=msg_from_user)
    
    msg_from_lex = response.get('messages', [])
    if msg_from_lex:
        print(f"Message from Chatbot: {msg_from_lex[0]['content']}")
        print(response)
        resp = {
    "messages": [
      {
        "type": "unstructured",
        "unstructured": {
          "id": 1,
          "text":  msg_from_lex[0]['content'],
          "timestamp": "11-10-2022"
        }
      }
    ]
  }
        # modify resp to send back the next question Lex would ask from the user
        
        # format resp in a way that is understood by the frontend
        # HINT: refer to function insertMessage() in chat.js that you uploaded
        # to the S3 bucket
        return resp