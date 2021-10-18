import re, boto3

class Flow:
    
    __available_protocols = ["tcp", "udp"]
    
    def __init__(self, source, destination, port, protocol) -> None:
        self.source_id = None
        self.destination_id  = None
        self.source_ip = source
        self.destination_ip = destination
        self.port = port
        self.protocol = protocol
        
        # Verify if port is valid
        if not self.is_a_valid_port():
            raise Exception("Invalid port number provided. Only 1-65535 are accepted.")
        
        # Verify if protocol is valid
        if not self.is_a_valid_protocol():
            raise Exception(f"Invalid protocol provided. Only {self.__available_protocols} are accepted.")
        
        # Get IDs and IPs for source
        if self.is_an_ip_address(source):
            self.source_id = self.fetch_instance_id("source", source)
        else:
            self.source_id = source
            self.source_ip = self.fetch_instance_ip("source", source)
        
        # Get IDs and IPs for destination
        if self.is_an_ip_address(destination):
            self.destination_id = self.fetch_instance_id("destination", destination)
        else:
            self.destination_id = destination
            self.destination_ip = self.fetch_instance_ip("destination", destination)
    
    def is_a_valid_port(self) -> bool:
        return self.port > 0 and self.port < 65536
    
    def is_a_valid_protocol(self) -> bool:
        return self.protocol in self.__available_protocols
    
    def is_an_ip_address(self, ip) -> bool:
        pat = re.match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", ip)
        return bool(pat)
    
    def fetch_instance_id(self, remote, instance_ip):
        
        # Create EC2 client
        client = boto3.client('ec2')
        
        # Make the API call
        response = client.describe_instances(Filters=[{
            'Name': 'private-ip-address',
            'Values': [instance_ip],
        }])
        
        # Retrieve instances
        for r in response['Reservations']:

            for i in r['Instances']:

                return i["InstanceId"]
        
        raise Exception(f"Wrong IP Address provided for {remote}")
    
    def fetch_instance_ip(self, remote, instance_id):
        
        # Create EC2 client
        client = boto3.client('ec2')
        
        # Make the API call
        response = client.describe_instances(Filters=[{
            'Name': 'instance-id',
            'Values': [instance_id],
        }])
        
        # Retrieve instances
        for r in response['Reservations']:

            for i in r['Instances']:

                return i["PrivateIpAddress"]
        
        raise Exception(f"Wrong Instance ID provided for {remote}")