import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    logger.debug('I am at Elicit')
    print({
        'messages': [message],
        'sessionState' :{
                 'sessionAttributes': session_attributes,
                    'dialogAction': {
            'type': 'ElicitSlot',
            'slots': slots,
            'slotToElicit': slot_to_elicit
        },
        'intent':
            {
                'name': intent_name,
                'state': 'Failed',
                'confirmationState' :'None',
                'slots' : slots
            }
        }
    })
    return {
        'messages': [message],
        'sessionState' :{
                 'sessionAttributes': session_attributes,
                    'dialogAction': {
            'type': 'ElicitSlot',
            'slots': slots,
            'slotToElicit': slot_to_elicit
        },
        'intent':
            {
                'name': intent_name,
                'state': 'Failed',
                'confirmationState' :'None',
                'slots' : slots
            }
        }
    }


def close(messageAttributes,session_attributes, intent_name, fulfillment_state, message):
    sqsClient = boto3.client('sqs')
    sqsQueueURL = "https://sqs.us-east-1.amazonaws.com/436831233028/info"
    
    #queue = sqs.get_queue_by_name(QueueName=sqsQueueURL)

    # You can now access identifiers and attributes
    #print(queue.url)
    #print(queue.attributes.get('DelaySeconds'))

    response = sqsClient.send_message(QueueUrl=sqsQueueURL, MessageBody="Message from Lex", MessageAttributes=messageAttributes)
    return {
        'messages': [message],
        'sessionState' :{
                 'sessionAttributes': session_attributes,
                    'dialogAction': {
            'type': 'Close'
        },
        'intent':
            {
                'name': intent_name,
                'state': 'Fulfilled',
                'confirmationState' : 'None',
            }
        }
    }


def delegate(session_attributes, intent_name, slots):
    return {
        'sessionState' :{
                 'sessionAttributes': session_attributes,
                    'dialogAction': {
            'type': 'Delegate'
        },
        'intent':
            {
                'name': intent_name,
                'state': 'ReadyForFulfillment',
                'confirmationState' : 'None',
                'slots' : slots
            }
        }
    }

""" --- Helper Functions --- """


def parse_int(n):
    try:
        logger.debug(int(8))
        return int(n)
    except ValueError:
        return float('nan')


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_book_appointment(location, cuisine, date, dining_time, no_of_people, phone_number, email):
    if location['value']['interpretedValue'] != 'manhattan':
        logger.debug(f'I am checking location{location}')
        return build_validation_result(False, 'Location', 'I did not recognize that, I can only find you something in Manhattan?')

    cuisine_list = ['Afghan', 'African', 'Andalusian', 'Arabic', 'Argentine', 'Armenian', 'Asian Fusion', 'Asturian', 'Australian', 'Austrian', 'Baguettes', 'Bangladeshi', 'Basque', 'Bavarian', 'Barbeque', 'Beer Garden', 'Beer Hall', 'Beisl', 'Belgian', 'Bistros', 'Black Sea', 'Brasseries', 'Brazilian', 'Breakfast & Brunch', 'British', 'Buffets', 'Bulgarian', 'Burgers', 'Burmese', 'Cafes', 'Cafeteria', 'Cajun/Creole', 'Cambodian', 'Canteen', 'Caribbean', 'Catalan', 'Cheesesteaks', 'Chicken Wings', 'Chicken Shop', 'Chilean', 'Chinese', 'Comfort Food', 'Corsican', 'Creperies', 'Cuban', 'Curry Sausage', 'Cypriot', 'Czech', 'Czech/Slovakian', 'Danish', 'Delis', 'Diners', 'Dinner Theater', 'Dumplings', 'Eastern European', 'Parent Cafes', 'Eritrean', 'Ethiopian', 'Filipino', 'Fischbroetchen', 'Fish & Chips', 'Flatbread', 'Fondue', 'Food Court', 'Food Stands', 'Freiduria', 'French', 'Galician', 'Game Meat', 'Gastropubs', 'Georgian', 'German', 'Giblets', 'Gluten-Free', 'Greek', 'Guamanian', 'Halal', 'Hawaiian', 'Heuriger', 'Himalayan/Nepalese', 'Hong Kong Style Cafe', 'Honduran', 'Hot Dogs', 'Fast Food', 'Hot Pot', 'Hungarian', 'Iberian', 'Indonesian', 'Indian', 'International', 'Irish', 'Island Pub', 'Israeli', 'Italian', 'Japanese', 'Jewish', 'Kebab', 'Kopitiam', 'Korean', 'Kosher', 'Kurdish', 'Laos', 'Laotian', 'Latin American', 'Lyonnais', 'Malaysian', 'Meatballs', 'Mediterranean', 'Mexican', 'Middle Eastern', 'Milk Bars', 'Modern Australian', 'Modern European', 'Mongolian', 'Moroccan', 'American (New)', 'Canadian (New)', 'New Mexican Cuisine', 'New Zealand', 'Nicaraguan', 'Night Food', 'Nikkei', 'Noodles', 'Norcinerie', 'Traditional Norwegian', 'Open Sandwiches', 'Oriental', 'Pakistani', 'Pan Asian', 'Parma', 'Persian/Iranian', 'Peruvian', 'PF/Comercial', 'Pita', 'Pizza', 'Polish', 'Polynesian', 'Pop-Up Restaurants', 'Portuguese', 'Potatoes', 'Poutineries', 'Pub Food', 'Live/Raw Food', 'Rice', 'Romanian', 'Rotisserie Chicken', 'Russian', 'Salad', 'Sandwiches', 'Scandinavian', 'Schnitzel', 'Scottish', 'Seafood', 'Serbo Croatian', 'Signature Cuisine', 'Singaporean', 'Slovakian', 'Somali', 'Soul Food', 'Soup', 'Southern', 'Spanish', 'Sri Lankan', 'Steakhouses', 'French Southwest', 'Supper Clubs', 'Sushi Bars', 'Swabian', 'Swedish', 'Swiss Food', 'Syrian', 'Tabernas', 'Taiwanese', 'Tapas Bars', 'Tapas/Small Plates', 'Tavola Calda', 'Tex-Mex', 'Thai', 'American (Traditional)', 'Traditional Swedish', 'Trattorie', 'Turkish', 'Ukrainian', 'Uzbek', 'Vegan', 'Vegetarian', 'Venison', 'Vietnamese', 'Waffles', 'Wok', 'Wraps', 'Yugoslav']
    
    if cuisine:
        if cuisine['value']['interpretedValue'].title() not in cuisine_list:
            logger.debug(f'Invalid Cuisine')
            return build_validation_result(False, 'Cuisine', 'I did not recognize that, Please try again?')
    if date:
        from datetime import datetime
        today = datetime.strftime(datetime.today(), '%m-%d')
        today = datetime.strptime(today, "%m-%d")
        print(today)
        date_str = date['value']['interpretedValue']
        date_formatted = datetime.strptime(date_str.split('-',1)[1], '%m-%d')
        if  date_formatted < today :
            logger.debug(f'Invalid Date')
            return build_validation_result(False, 'Date', 'Please enter a valid date')
    if dining_time:
        try:
            from datetime import datetime
            today = datetime.strftime(datetime.today(), '%m-%d')
            today = datetime.strptime(today, "%m-%d")
            date_str = date['value']['interpretedValue']
            date_formatted = datetime.strptime(date_str.split('-',1)[1], '%m-%d')
            if date_formatted == today:
                time_now = datetime.strftime(datetime.now(), "%H:%M")
                time_now = datetime.strptime(time_now, "%H:%M")
                time_str = dining_time['value']['interpretedValue']
                time_formatted = datetime.strptime(time_str, "%H:%M")
                if time_formatted < time_now :
                    logger.debug(f'Invalid time')
                    return build_validation_result(False, 'Dining_Time', 'Please enter a valid time')
        except Exception: 
            return build_validation_result(False, 'Dining_Time', 'Please enter a valid time')
    if no_of_people:
        if type(parse_int(no_of_people['value']['interpretedValue']))!= int:
            return build_validation_result(False, 'Number_of_People', 'I did not understand that,please enter a number')
    
    if phone_number:
        if len(phone_number['value']['interpretedValue']) != 10:
            return build_validation_result(False, 'Phone_Number', 'Please enter a valid number')

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def suggest_rest(intent_request):
    """
    Performs dialog management and fulfillment for making a restaurant reservation.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of confirmIntent to support the confirmation of inferred slot values, when confirmation is required
    on the bot model and the inferred slot values fully specify the intent.
    """
    
    logger.debug('I am suggest_rest')
    Location = intent_request["interpretations"][0]['intent']['slots']['Location']
    Cuisine = intent_request["interpretations"][0]['intent']['slots']['Cuisine']
    Date = intent_request["interpretations"][0]['intent']['slots']['Date']
    Dining_Time = intent_request["interpretations"][0]['intent']['slots']['Dining_Time']
    Number_of_People = intent_request["interpretations"][0]['intent']['slots']['Number_of_People']
    Phone_Number = intent_request["interpretations"][0]['intent']['slots']['Phone_Number']
    Email = intent_request["interpretations"][0]['intent']['slots']['Email']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request['sessionState']['sessionAttributes'] if intent_request['sessionState']['sessionAttributes'] else {}

    if source == 'DialogCodeHook':
        logger.debug('I inside dialoghook')
        # Perform basic validation on the supplied input slots.
        slots = intent_request["interpretations"][0]['intent']['slots']
        validation_result = validate_book_appointment(Location, Cuisine, Date, Dining_Time, Number_of_People, Phone_Number, Email)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                output_session_attributes,
                intent_request["interpretations"][0]['intent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message'],
                )

        return delegate(output_session_attributes, intent_request["interpretations"][0]['intent']['name'], slots)
        
    messageAttributes = {
        'Cuisine': {
            'DataType': 'String',
            'StringValue': Cuisine['value']['interpretedValue']
        },
        'Phone_Number': {
            'DataType': 'Number',
            'StringValue': Phone_Number['value']['interpretedValue']
        },
        'Number_of_People': {
            'DataType': 'Number',
            'StringValue': Number_of_People['value']['interpretedValue']
        },
        'Dining_Time': {
            'DataType': 'String',
            'StringValue': Dining_Time['value']['interpretedValue']
        },
        'Location': {
            'DataType': 'String',
            'StringValue': Location['value']['interpretedValue']
        },
        'Date':{
            'DataType': 'String',
            'StringValue': Date['value']['interpretedValue']
        },
        'Email':{
            'DataType': 'String',
            'StringValue': Email['value']['interpretedValue']
        }
    }  
    
    if source == 'FulfillmentCodeHook':
        logger.debug('I am at fulfillment')
        return close(
            messageAttributes,
            output_session_attributes,
            'DiningSuggestionsIntent',
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Okay, I will make the reservation for you'
            }
        )


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """


    intent_name = intent_request["interpretations"][0]['intent']['name']
    print(intent_name)
    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        logger.debug('intent identified')
        print(intent_request)
        return suggest_rest(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    
    return dispatch(event)
