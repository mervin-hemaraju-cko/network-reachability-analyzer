
def recover_output_telnet(output):
    output = output.strip()
    return (output.split("TcpTestSucceeded :",1)[1]).strip().lower()