from os import environ
from models.flow import Flow
from urllib.parse import parse_qs 

def validate_request(event):
    
    # Verify if payload sent properly
    if "postBody" not in event:
        raise Exception("Wrong payload provided.")
    
    # Extract data from paylaod
    payload = parse_qs(event['postBody'])
    
    # Verify if token provided in payload
    if "token" not in payload:
        raise Exception("Access denied. Token not provided")

    if payload["token"][0] != environ["TOKEN_VERIFICATION_SLACK_SYSAPP"]:
        raise Exception("Access denied. Wrong token provided")
    
    # return the payload
    return payload

def extract_nra_parameters(payload):
    
    # Checks if parameters was provided
    if "text" not in payload:
        raise Exception("Missing parameters.")
    
    # Extract the parameters
    parameters = payload["text"][0]
    
    # Split to get all parameters
    parameters = parameters.split(" ")
    
    # Verify if all parameters was provided
    if len(parameters) != 4:
        raise Exception("Missing parameters. Parameters should be provided in this format: source destination port protocol")

    return parameters[0], parameters[1], parameters[2], parameters[3].lower()


def main(event, context):
    
    # Perform several checks to validate 
    # whether the request has been sent in the correct format
    payload = validate_request(event)
    
    # Extract parameters
    source, destination, port, protocol = extract_nra_parameters(payload)
    
    # Construct flow model
    flow = Flow(source, destination, port, protocol)