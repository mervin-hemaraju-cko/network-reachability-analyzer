import requests, json, boto3, uuid, threading, time
from os import environ
from urllib.parse import parse_qs 
from models.exceptions import SlackPayloadProcessing, SlackInvalidParameters
from models.flow import Flow
from models.slack_caller import SlackCaller
from helper.utils import recover_output_telnet, recover_output_wf
import helper.block_builder as BlockBuilder

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

def post_to_slack_channel(blocks=None):
    
    # Make API Call to Slack API
    requests.post('https://slack.com/api/chat.postMessage', {
        'token': environ["ENV_SLACK_KEY_API"],
        'channel': environ["ENV_SLACK_CHANNEL"],
        'username': environ["ENV_SLACK_USERNAME"],
        'as_user': True,
        "attachments": json.dumps([{ "color": "#C990E1", "blocks": blocks}])
    }).json()
    
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

def apply_waiter_nia(command_id, waiting_intervals):
    
    # Create the EC2 client
    client = boto3.client('ec2') 

    # Define parameters
    delay = waiting_intervals["Delay"]
    max_retries = waiting_intervals["MaxAttempts"]
    current_status = "running"
    described_analysis = None

    # Keep looping until a successful status is not reached AND
    # The maxt retries is not over
    while(max_retries > 0 and current_status == "running"):
        
        # Apply delay on first shot
        time.sleep(delay)
        
        # After delay, try to poll
        described_analysis = client.describe_network_insights_analyses(
            NetworkInsightsAnalysisIds=[
                command_id,
            ]
        )
        
        # Re format the repsonse description
        described_analysis = next((filter(lambda comp: comp, described_analysis['NetworkInsightsAnalyses'])), None)
        
        # Update the current status
        current_status = described_analysis['Status']

        # Decrease max_retries
        max_retries = max_retries - 1

    # Return the data
    return described_analysis
    
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
                "output": "Telnet connection is working from Source to Destination"
            })
            
        else:
                        
            output_records.append({
                "operation": "Telnet",
                "success": True,
                "operation_success": False,
                "output": "Telnet is not working"
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
            "output": "Port is not in listening state."
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

def action_start_nia(flow, username):
    
    # Get the NIA command ID
    _, nia_id = flow.create_nia(username)
    
    # Apply waiter to wait for analysis to process
    analysis_results = apply_waiter_nia(nia_id, {
        'Delay': 30,
        'MaxAttempts': 8
    })    
    
    
    # The analysis wasn't successful
    if analysis_results['Status'] != "succeeded":
        
        output_records.append({
                "operation": "Network_Insights_Analysis",
                "success": False,
                "operation_success": False,
                "output": "An error occurred while analysing path on AWS"
            })
        
        return
    
    # No path found during analysis
    # Which means that a flow will need to be addded on security groups
    if not analysis_results['NetworkPathFound']:
        
        output_records.append({
                "operation": "Network_Insights_Analysis",
                "success": True,
                "operation_success": False,
                "output": "No flow found that will allow this connection."
            })
        
        return
    
    # Patch found on AWS
    # Which means flow already opened.
    else:
        
        # Search for the SG allowing the flow
        sg_id_source = next((filter(lambda comp: "sg-" in comp["Component"]["Id"], analysis_results['ForwardPathComponents'])), None)
        sg_id_destination = next((filter(lambda comp: "sg-" in comp["Component"]["Id"], analysis_results['ReturnPathComponents'])), None)
        
        # Search for the ENI allowing the flow
        eni_id_source = next((filter(lambda comp: "eni-" in comp["Component"]["Id"], analysis_results['ForwardPathComponents'])), None)
        eni_id_destination = next((filter(lambda comp: "eni-" in comp["Component"]["Id"], analysis_results['ReturnPathComponents'])), None)
        
        output_records.append({
                "operation": "Network_Insights_Analysis",
                "success": True,
                "operation_success": True,
                "output": "A flow already exists that will allow this connection",
                "sg_source": sg_id_source["Component"]["Id"],
                "sg_destination": sg_id_destination["Component"]["Id"],
                "eni_source": eni_id_source["Component"]["Id"],
                "eni_destination": eni_id_destination["Component"]["Id"],
            })
        
        return

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
        
def generate_report(flow, unique_identifier, username):
    
    # Get each main operation's output
    output_telnet = next((filter(lambda output: output["operation"] == "Telnet", output_records)), None)
    output_nia = next((filter(lambda output: output["operation"] == "Network_Insights_Analysis", output_records)), None)
    output_port_checker = next((filter(lambda output: output["operation"] == "Port_Checker", output_records)), None)
    output_wf_checker = next((filter(lambda output: output["operation"] == "Windows_Firewall_Checker", output_records)), None)
    
    # Create the final block and get the header
    final_report_block = BlockBuilder.block_main_header(
        source_ip= flow.source_ip,
        source_id= flow.source_id,
        destination_ip= flow.destination_ip,
        destination_id= flow.destination_id,
        port= flow.port,
        protocol= flow.protocol,
        unique_identifier=unique_identifier,
        username=username
    )
    
    # Determine final report for telnet
    if output_telnet != None:
        
        if output_telnet["success"] == True:
            final_report_telnet = BlockBuilder.block_telnet_success(output_telnet["operation_success"], output_telnet["output"])
        else:
            final_report_telnet = BlockBuilder.block_telnet_failure(output_telnet["output"])
        
        # Append to final report
        final_report_block.extend(final_report_telnet)
    
    # Determine final report for port_checker
    if output_port_checker != None:
        
        if output_port_checker["success"] == True:
            final_report_port_checker = BlockBuilder.block_port_checker_success(output_port_checker["operation_success"], output_port_checker["output"])
        else:
            final_report_port_checker = BlockBuilder.block_port_checker_failure(output_port_checker["output"])
        
        # Append to final report
        final_report_block.extend(final_report_port_checker)
    
    # Determine final report for windows firewall checker
    if output_wf_checker != None:
        
        if output_wf_checker["success"] == True:
            final_report_wf_checker = BlockBuilder.block_wf_checker_success(output_wf_checker["operation_success"], output_wf_checker["output"])
        else:
            final_report_wf_checker = BlockBuilder.block_wf_checker_failure(output_wf_checker["output"])
        
        # Append to final report
        final_report_block.extend(final_report_wf_checker)
            
    # Determine final report for nia
    if output_nia != None:
        
        if output_nia["success"] == True:
            
            if output_nia["operation_success"]:
                
                final_report_nia = BlockBuilder.block_nia_success_no_changes(
                    conclusion=output_nia["output"],
                    sg_id_source=output_nia["sg_source"],
                    sg_id_destination=output_nia["sg_destination"],
                    eni_id_source=output_nia["eni_source"],
                    eni_id_destination=output_nia["eni_destination"],
                )
            
            else:
                final_report_nia = BlockBuilder.block_nia_success_change_needed(output_nia["output"])
                
        else:
            final_report_nia = BlockBuilder.block_nia_failure(output_nia["output"])
            
        
        # Append to final report
        final_report_block.extend(final_report_nia)
        
    # Return the final report
    return final_report_block
    
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
        unique_request_id = uuid.uuid4().hex[:12].upper()
        
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
            
            slack_instant_reply(slack_caller.response_url, f"Your request has been completed.")
            
            final_report_block = generate_report(flow, unique_request_id, slack_caller.user)
            
            post_to_slack_channel(final_report_block)
            
        else:
            # Create a thread for each action
            thread_port_checker = threading.Thread(target=action_start_port_checker, args=(flow,))
            thread_nia = threading.Thread(target=action_start_nia, args=(flow, slack_caller.user,))
            thread_wf_checker = threading.Thread(target=action_start_wf_checker, args=(flow,))
            
            # Start the threads
            thread_port_checker.start()
            thread_nia.start()
            thread_wf_checker.start()
            
            # Wait for the threads
            thread_port_checker.join()
            thread_nia.join()
            thread_wf_checker.join()
            
            slack_instant_reply(slack_caller.response_url, f"Your request has been completed.")
            
            final_report_block = generate_report(flow, unique_request_id, slack_caller.user)
            
            post_to_slack_channel(final_report_block)
            
        
    except SlackPayloadProcessing as SPP:
        # TODO("Post results to Slack")
        print(str(SPP))
        
    except SlackInvalidParameters as SIP:
        slack_instant_reply(slack_caller.response_url, f"Error: {SIP}")
        
    except Exception as e:
        # TODO("Post results to Slack")
        print(str(e))