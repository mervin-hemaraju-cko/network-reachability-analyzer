
def block_main_header(source_ip, source_id, destination_ip, destination_id, port, protocol, username, unique_identifier):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": f"Network Reachability Analyzer Report - {unique_identifier}",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Source:*\n{source_ip} ({source_id})"
				},
				{
					"type": "mrkdwn",
					"text": f"*Destination:*\n{destination_ip} ({destination_id})"
				}
			]
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Port:*\n{port}"
				},
				{
					"type": "mrkdwn",
					"text": f"*Protocol:*\n{protocol}"
				}
			]
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Started By:*\n{username}"
				}
			]
		}
    ]
    
def block_telnet_success(is_success, conclusion):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Telnet",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*is_success:*\n{'Yes' if is_success else 'No'}"
				},
				{
					"type": "mrkdwn",
					"text": f"*Conclusion:*\n{conclusion}"
				}
			]
		}
    ]

def block_telnet_failure(error_message):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Telnet",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*is_success:*\nN/A"
				},
				{
					"type": "mrkdwn",
					"text": f"*Conclusion:*\n{error_message}"
				}
			]
		}
    ]

def block_wf_checker_success(is_success, conclusion):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Windows Firewall Checker",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Enabled:*\n{'Yes' if is_success else 'No'}"
				},
				{
					"type": "mrkdwn",
					"text": f"*Conclusion:*\n{conclusion}"
				}
			]
		}
    ]

def block_wf_checker_failure(error_message):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Windows Firewall Checker",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Enabled:*\nN/A"
				},
				{
					"type": "mrkdwn",
					"text": f"*Conclusion:*\n{error_message}"
				}
			]
		}
    ]

def block_port_checker_success(is_success, conclusion):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Port Checker",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Listening:*\n{'Yes' if is_success else 'No'}"
				},
				{
					"type": "mrkdwn",
					"text": f"*Conclusion:*\n{conclusion}"
				}
			]
		}
    ]

def block_port_checker_failure(error_message):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Port Checker",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Listening:*\nN/A"
				},
				{
					"type": "mrkdwn",
					"text": f"*Conclusion:*\n{error_message}"
				}
			]
		}
    ]

def block_nia_success_change_needed(conclusion):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "AWS Checker",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Has Entry in SG:*\nNo"
				},
				{
					"type": "mrkdwn",
					"text": f"*Conclusion:*\n{conclusion}"
				}
			]
		}
    ]
    
def block_nia_success_no_changes(conclusion, sg_id_source, sg_id_destination, eni_id_source, eni_id_destination):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "AWS Checker",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Has Entry in SG:*\nYes"
				},
				{
					"type": "mrkdwn",
					"text": f"*Conclusion:*\n{conclusion}"
				}
			]
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Source SG:*\n{sg_id_source}"
				},
				{
					"type": "mrkdwn",
					"text": f"*Destination SG:*\n{sg_id_destination}"
				}
			]
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Source ENI:*\n{eni_id_source}"
				},
				{
					"type": "mrkdwn",
					"text": f"*Destination ENI:*\n{eni_id_destination}"
				}
			]
		}
    ]

def block_nia_failure(error_message):
    return [
        {
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "AWS Checker",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": "*Has Entry in SG:*\nN/A"
				},
				{
					"type": "mrkdwn",
					"text": f"*Conclusion:*\n{error_message}"
				}
			]
		}
    ]

def block_actions_needed(actions_needed):
    return [
		{
			"type": "divider"
		},
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Actions",
				"emoji": True
			}
		},
		{
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"{actions_needed}"
				}
			]
		}
	]