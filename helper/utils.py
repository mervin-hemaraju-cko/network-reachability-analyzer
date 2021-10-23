import helper.constants as Consts

def determine_final_action(output_telnet, output_port_checker, output_nia, output_wf_checker):
    
    # This function will check all the output and determine
    # which actions needs to be taken on this flow
    
    # We check for the telnet first before proceeding
    if output_telnet["operation_success"] == True:
        return Consts.FINAL_ACTION_NONE_REQ
    
    # We check if any errors occurred in one of the actions
    if(output_telnet["success"] == False or
       output_port_checker["success"] == False or
       output_nia["success"] == False or
       output_wf_checker["success"] == False
    ):
        return Consts.FINAL_ACTION_UNDETERMINED
    
    
    # If we reached this clause, it means the telnet was unsuccessful
    
    # SCENARIO: Flow enabled on AWS, Port is in Listening, WFW is disabled on destination
    if output_nia["operation_success"] == True and output_port_checker["operation_success"] == True and output_wf_checker["operation_success"] == False:
        return Consts.FINAL_ACTION_NONE_REQ
    
    # SCENARIO: Flow enabled on AWS, Port is in Listening, WFW is enabled on destination
    if output_nia["operation_success"] == True and output_port_checker["operation_success"] == True and output_wf_checker["operation_success"] == True:
        return Consts.FINAL_ACTION_WF_BLOCKING
    
    # SCENARIO: Flow enabled on AWS, Port is not in Listening, WFW is enabled on destination
    if output_nia["operation_success"] == True and output_port_checker["operation_success"] == False and output_wf_checker["operation_success"] == True:
        return Consts.FINAL_ACTION_PC_WF_BLOCKING
    
    # SCENARIO: Flow enabled on AWS, Port is not in Listening, WFW is enabled on destination
    if output_nia["operation_success"] == True and output_port_checker["operation_success"] == False and output_wf_checker["operation_success"] == False:
        return Consts.FINAL_ACTION_PC_BLOCKING
    
    # SCENARIO: Flow disabled on AWS, Port is in Listening, WFW is disabled on destination
    if output_nia["operation_success"] == False and output_port_checker["operation_success"] == True and output_wf_checker["operation_success"] == False:
        return Consts.FINAL_ACTION_AWS_BLOCKING
    
    # SCENARIO: Flow disabled on AWS, Port is in Listening, WFW is enabled on destination
    if output_nia["operation_success"] == False and output_port_checker["operation_success"] == True and output_wf_checker["operation_success"] == True:
        return Consts.FINAL_ACTION_AWS_WF_BLOCKING
    
    # SCENARIO: Flow disabled on AWS, Port is not in Listening, WFW is enabled on destination
    if output_nia["operation_success"] == False and output_port_checker["operation_success"] == False and output_wf_checker["operation_success"] == True:
        return Consts.FINAL_ACTION_AWS_PC_WF_BLOCKING
    
    # SCENARIO: Flow disabled on AWS, Port is not in Listening, WFW is disabled on destination
    if output_nia["operation_success"] == False and output_port_checker["operation_success"] == False and output_wf_checker["operation_success"] == False:
        return Consts.FINAL_ACTION_AWS_PC_BLOCKING
        
def recover_output_telnet(output):
    
    # This function will retrieve the output of the SSM command
    # which checks if the telnet was successfull or not.
    
    list_outputs = output.strip().splitlines()
    formatted_ist = [x.strip().lower().replace(" ", "") for x in list_outputs if x]
    tcp_result = next((filter(lambda output: "tcptestsucceeded" in output, formatted_ist)))
    return (tcp_result.split(':'))[1]

def recover_output_wf(output):
    
    # This function will retrieve the output of the SSM command
    # which checks if any of the firewalls are enabled.
    # If atleast one is enabled, it will return firewalls enabled.
    
    list_outputs = output.strip().splitlines()
    filtered = [x.strip().lower() for x in list_outputs if x]
    
    for o in filtered:
        
        if("on" in o):
            return True, "Some firewalls are enabled on the server"
        
    return False, "All the firewalls are turned off on the server"