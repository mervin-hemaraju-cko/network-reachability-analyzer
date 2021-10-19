import requests, json
from os import environ
from urllib.parse import parse_qs 
from models.exceptions import SlackPayloadProcessing, SlackInvalidParameters
from models.flow import Flow
from models.slack_caller import SlackCaller

def validate_request(event):
    
    # Verify if payload sent properly
    if "postBody" not in event:
        raise SlackPayloadProcessing("Wrong payload provided.")
    
    # Extract data from paylaod
    payload = parse_qs(event['postBody'])
    
    # Verify if token provided in payload
    if "token" not in payload:
        raise SlackPayloadProcessing("Access denied. Token not provided")

    if payload["token"][0] != environ["TOKEN_VERIFICATION_SLACK_SYSAPP"]:
        raise SlackPayloadProcessing("Access denied. Wrong token provided")
    
    # return the payload
    return payload

def extract_nra_parameters(payload):
    
    # Checks if parameters was provided
    if "text" not in payload:
        raise SlackInvalidParameters("Missing parameters.")
    
    if len(payload["text"]) < 1:
        raise SlackInvalidParameters("Missing parameters.")
        
    # Extract the parameters
    parameters = payload["text"][0]
    
    # Split to get all parameters
    parameters = parameters.split(" ")
    
    # Verify if all parameters was provided
    if len(parameters) != 4:
        raise SlackInvalidParameters("Missing parameters. Parameters should be provided in this format: source destination port protocol")

    return parameters[0], parameters[1], parameters[2], parameters[3].lower()

def slack_instant_reply(resonse_url, message, blocks):

    # Make API Call to Slack API
    requests.post(
        url=resonse_url,
        data = json.dumps({"text": message}),
        headers={"Content-Type": "application/json"}
    )

def main(event, context):
    
    try:
        
        # Perform several checks to validate 
        # whether the request has been sent in the correct format
        payload = validate_request(event)
        
        # Construct Slack Channel model
        slack_caller = SlackCaller(payload)
        
        # Extract parameters
        source, destination, port, protocol = extract_nra_parameters(payload)
        
        # Send a message to the user notifying the start of the script
        slack_instant_reply(slack_caller.response_url, "Your request has started.")
        
        # Construct flow model
        flow = Flow(source, destination, port, protocol)
    
    except SlackPayloadProcessing as SPP:
        # TODO("Post results to Slack")
        print(str(SPP))
        
    except SlackInvalidParameters as SIP:
        slack_instant_reply(f"Error: {SIP}")
        
    except Exception as e:
        # TODO("Post results to Slack")
        print(str(e))