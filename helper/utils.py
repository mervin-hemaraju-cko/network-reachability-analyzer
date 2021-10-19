
from typing import final


def recover_output_telnet(output):
    list_outputs = output.strip().splitlines()
    formatted_ist = [x.strip().lower().replace(" ", "") for x in list_outputs if x]
    tcp_result = next((filter(lambda output: "tcptestsucceeded" in output, formatted_ist)))
    return (tcp_result.split(':'))[1]

def recover_output_wf(output):
    list_outputs = output.strip().splitlines()
    filtered = [x.strip().lower() for x in list_outputs if x]
    
    for o in filtered:
        
        if("on" in o):
            return True, "Some firewalls are enabled on the server"
        
    return False, "All the firewalls are turned off on the server"