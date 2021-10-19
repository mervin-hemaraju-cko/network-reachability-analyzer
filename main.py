import requests, json, boto3, uuid, threading
from os import environ
from urllib.parse import parse_qs 
from models.exceptions import SlackPayloadProcessing, SlackInvalidParameters
from models.flow import Flow
from models.slack_caller import SlackCaller
from helper.utils import recover_output_telnet, recover_output_wf


############################
##### Global Variables #####
############################
# Define an empty list of output to
# build the final report
output_records = []

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

def slack_instant_reply(resonse_url, message):

    # Make API Call to Slack API
    requests.post(
        url=resonse_url,
        data = json.dumps({"text": message}),
        headers={"Content-Type": "application/json"}
    )

def apply_waiter_command_execution(command_id, instance_id, waiting_intervals):
    
    # Create the SSM client
    client = boto3.client('ssm')
    
    # Create waiter
    waiter = client.get_waiter('command_executed')
    
    # Apply waiter
    waiter.wait(
        CommandId=command_id,
        InstanceId=instance_id,
        WaiterConfig=waiting_intervals
    )
    
def get_command_output(command_id, instance_id, generic_error_message):
    
    ############################################
    ### Will return output as success, error ###
    ############################################
    
    # Create the SSM client
    client = boto3.client('ssm')
    
    # Get details
    response = client.get_command_invocation(
        CommandId=command_id,
        InstanceId=instance_id
    )
    
    # Verify if request was successfull
    if response['Status'] != "Success":
        return "", generic_error_message
    
    return response['StandardOutputContent'], response['StandardErrorContent']

def action_start_telnet(flow):
    
    # Get the telnet command ID
    telnet_command_id = flow.create_command_telnet()
    
    # Wait for completion of Telnet
    apply_waiter_command_execution(telnet_command_id, flow.source_id, {
        'Delay': 15,
        'MaxAttempts': 4
    })
    
    # Get the telnet result
    telnet_res_success, telnet_res_failure = get_command_output(telnet_command_id, flow.source_id, "Couldn't carry out the Telnet request.")

    if telnet_res_success != "":
        
        is_telnet_successfull = recover_output_telnet(telnet_res_success)
        
        if is_telnet_successfull == "true":
            
            output_records.append({
                "operation": "Telnet",
                "success": True,
                "operation_success": True,
                "output": ""
            })
            
        else:
                        
            output_records.append({
                "operation": "Telnet",
                "success": True,
                "operation_success": False,
                "output": ""
            }) 
    
    else:
        
        output_records.append({
            "operation": "Telnet",
            "success": False,
            "operation_success": False,
            "output": telnet_res_failure
        }) 
    
def action_start_port_checker(flow):
    
    # Get the port checker command ID
    pc_command_id = flow.create_command_port_checking()
    
    # Wait for completion of Port Checker
    apply_waiter_command_execution(pc_command_id, flow.destination_id, {
        'Delay': 5,
        'MaxAttempts': 3
    })
    
    # Get the port checker result
    pc_res_success, pc_res_failure = get_command_output(pc_command_id, flow.destination_id, "Couldn't carry out the Port Checker request.")
    
    if pc_res_success == "" and pc_res_failure == "":
        
        output_records.append({
            "operation": "Port_Checker",
            "success": True,
            "operation_success": False,
            "output": ""
        }) 
        
        return
    
    if pc_res_failure != "":
        
        output_records.append({
            "operation": "Port_Checker",
            "success": False,
            "operation_success": False,
            "output": pc_res_failure
        }) 
        
        return
    
    if pc_res_success != "":
        
        # TODO(Enhance validation of port_checker)
        output_records.append({
            "operation": "Port_Checker",
            "success": True,
            "operation_success": True,
            "output": pc_res_success
        }) 
        
        return

def action_start_nip(flow):
    # TODO("Complete NIP")
    pass

def action_start_wf_checker(flow):
    
    # Get the firewall checker command ID
    wf_command_id = flow.create_command_wf_checking()
    
    # Wait for completion of firewall checker
    apply_waiter_command_execution(wf_command_id, flow.destination_id, {
        'Delay': 5,
        'MaxAttempts': 3
    })
    
    # Get the firewall checker result
    wf_res_success, wf_res_failure = get_command_output(wf_command_id, flow.destination_id, "Couldn't carry out the Port Checker request.")
    
    if wf_res_success != "":
        
        is_enabled, wf_output = recover_output_wf(wf_res_success)
        
        output_records.append({
            "operation": "Windows_Firewall_Checker",
            "success": True,
            "operation_success": is_enabled,
            "output": wf_output
        }) 
        
    else:
        
        output_records.append({
            "operation": "Windows_Firewall_Checker",
            "success": False,
            "operation_success": False,
            "output": wf_res_failure
        }) 
        

def main(event, context):
    
    # My Variables
    global output_records
    output_records.clear()
    
    slack_caller = None
    
    try:
        
        # Perform several checks to validate 
        # whether the request has been sent in the correct format
        # If exception occurs, it will trigger the SlackPayloadProcessing Exception
        payload = validate_request(event)
        
        # Construct Slack Channel model
        # Will get details like user name
        # channel id, response url etc..
        slack_caller = SlackCaller(payload)
        
        # Extract parameters of the connection request
        # In case of malformed requests, it will trigger the SlackInvalidParameters Exception
        source, destination, port, protocol = extract_nra_parameters(payload)
        
        # Create a unique identifier for the request
        unique_request_id = uuid.uuid4().hex[:6].upper()
        
        # Send a message to the user notifying the start of the script
        slack_instant_reply(slack_caller.response_url, f"Your request with ID {unique_request_id} has started.")
        
        # Construct flow model
        flow = Flow(source, destination, port, protocol)

        #####################################
        #### Main Troubleshooting Actions####
        #####################################
        
        # Perform a telnet test as this is the very
        # first troubleshooting action to know if we need
        # to proceed further
        action_start_telnet(flow)
        
        # Checks if telnet is a success.
        # If telnet is a success, stop the request as
        # the flow is already opened.
        # If not, call all other actions in a thread to process simultaneously.         
        telnet_output = next((filter(lambda output: output["operation"] == "Telnet", output_records)))
        
        if telnet_output["operation_success"] == True:
            # TODO("Send report on Slack Channel")
            slack_instant_reply(slack_caller.response_url, f"Your request has been completed.")
        else:
            # Create a thread for each action
            thread_port_checker = threading.Thread(target=action_start_port_checker, args=(flow,))
            thread_nip = threading.Thread(target=action_start_nip, args=(flow,))
            thread_wf_checker = threading.Thread(target=action_start_wf_checker, args=(flow,))
            
            # Start the threads
            thread_port_checker.start()
            thread_nip.start()
            thread_wf_checker.start()
            
            # Wait for the threads
            thread_port_checker.join()
            thread_nip.join()
            thread_wf_checker.join()
            
            print(output_records)
        
    except SlackPayloadProcessing as SPP:
        # TODO("Post results to Slack")
        print(str(SPP))
        
    except SlackInvalidParameters as SIP:
        slack_instant_reply(slack_caller.response_url, f"Error: {SIP}")
        
    except Exception as e:
        # TODO("Post results to Slack")
        print(str(e))