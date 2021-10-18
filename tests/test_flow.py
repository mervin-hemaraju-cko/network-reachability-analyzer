import pytest
from models.flow import Flow

###############################
####### Important Note ########
###############################
## Tests should be performed ##
## in Playground Environment ##
###############################
###############################

class TestFlow:

    testdata = [
            (0, "Invalid port number provided. Only 1-65535 are accepted."),
            (1, "Passed"),
            (10000, "Passed"),
            (65534, "Passed"),
            (65535, "Passed"),
            (65536, "Invalid port number provided. Only 1-65535 are accepted."),
            (100000, "Invalid port number provided. Only 1-65535 are accepted."),
    ]
    @pytest.mark.parametrize("port,expected_result", testdata)    
    def test_flow_initialization_PortValidation(self,port,expected_result):
        # Arrange
        source = "172.31.255.20"
        destination = "i-07972a766e0461bee"
        protocol = "tcp"
        
        # Act 
        try:
            flow = Flow(source, destination, port, protocol)
            result = "Passed"
        except Exception as e:
            result = str(e)
            
        # Assert
        assert expected_result == result
    
    testdata = [
            ("tcp", "Passed"),
            ("udp", "Passed"),
            ("icmp", "Invalid protocol provided. Only ['tcp', 'udp'] are accepted."),
            ("iasfgwscmp", "Invalid protocol provided. Only ['tcp', 'udp'] are accepted."),
            ("tcpudp", "Invalid protocol provided. Only ['tcp', 'udp'] are accepted."),
    ]
    @pytest.mark.parametrize("protocol,expected_result", testdata)    
    def test_flow_initialization_ProtocolValidation(self,protocol,expected_result):
        # Arrange
        source = "172.31.255.20"
        destination = "i-07972a766e0461bee"
        port = 10
        
        # Act 
        try:
            flow = Flow(source, destination, port, protocol)
            result = "Passed"
        except Exception as e:
            result = str(e)
            
        # Assert
        assert expected_result == result
    
    
    testdata = [
        ("1.1.1.1", True),
        ("10.10.10.10", True),
        ("1.10.100.255", True),
        ("255.255.255.255", True),
        ("192.168.100.", False),
        ("300.168.100.1", False),
        ("1.168.100.300", False),
        ("192.168..1", False),
        ("192..1.1", False),
        (".1.1.1", False),
        ("hello.168.100.1", False),
        ("t.r.s.a", False),
        ("100.1.1.1:20", False),
        ("100.1.1.1.1", False),
    ]
    @pytest.mark.parametrize("test_data,expected_result", testdata)
    def test_test_flow_initialization_IsAnIPAddress(self,test_data,expected_result):
        # Arrange
        source = "172.31.255.20"
        destination = "i-07972a766e0461bee"
        protocol = "tcp"
        port = 10
        
        # Act 
        try:
            flow = Flow(source, destination, port, protocol)
            result = flow.is_an_ip_address(test_data)
        except Exception as e:
            result = str(e)

        # Assert
        assert result == expected_result
    
    testdata = [
        ("172.31.255.20", "172.31.255.20:i-009ced0eee26e121d"),
        ("i-009ced0eee26e121d", "172.31.255.20:i-009ced0eee26e121d"),
        ("172.31.255.50", "172.31.255.50:i-07972a766e0461bee"),
        ("i-07972a766e0461bee", "172.31.255.50:i-07972a766e0461bee"),
    ]
    @pytest.mark.parametrize("source,expected_result", testdata)
    def test_test_flow_initialization_SourceInstance(self, source, expected_result):
        # Arrange
        destination = "i-07972a766e0461bee"
        protocol = "tcp"
        port = 10
        
        # Act 
        try:
            flow = Flow(source, destination, port, protocol)
            result = f"{flow.source_ip}:{flow.source_id}"
        except Exception as e:
            result = str(e)

        # Assert
        assert expected_result == result
    
    testdata = [
        ("172.31.255.20", "172.31.255.20:i-009ced0eee26e121d"),
        ("i-009ced0eee26e121d", "172.31.255.20:i-009ced0eee26e121d"),
        ("172.31.255.50", "172.31.255.50:i-07972a766e0461bee"),
        ("i-07972a766e0461bee", "172.31.255.50:i-07972a766e0461bee"),
    ]
    @pytest.mark.parametrize("destination,expected_result", testdata)
    def test_test_flow_initialization_DestinationInstance(self, destination, expected_result):
        # Arrange
        source = "i-07972a766e0461bee"
        protocol = "tcp"
        port = 10
        
        # Act 
        try:
            flow = Flow(source, destination, port, protocol)
            result = f"{flow.destination_ip}:{flow.destination_id}"
        except Exception as e:
            result = str(e)

        # Assert
        assert expected_result == result