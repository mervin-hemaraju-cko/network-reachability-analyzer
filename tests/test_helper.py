from helper.utils import recover_output_telnet
import pytest

class TestHelper:
    
    testdata = [
        ('''ComputerName     : 172.31.255.50
        RemoteAddress    : 172.31.255.50
        RemotePort       : 3389
        InterfaceAlias   : Ethernet 3
        SourceAddress    : 172.31.255.20
        TcpTestSucceeded : True''',
        "true"),
        ('''ComputerName     : 172.31.255.50
        RemoteAddress    : 172.31.255.50
        RemotePort       : 3389
        InterfaceAlias   : Ethernet 3
        SourceAddress    : 172.31.255.20
        TcpTestSucceeded : False''',
        "false"),
        ('''
        SourceAddress    : 172.31.255.20
        TcpTestSucceeded : False ''',
        "false"),
    ]
    @pytest.mark.parametrize("output,expected_result", testdata)
    def test_recover_output_telnet_1Of3(self, output, expected_result):
        
        # Arrange
        
        # Act
        result = recover_output_telnet(output)
        
        # Assert
        assert expected_result == result