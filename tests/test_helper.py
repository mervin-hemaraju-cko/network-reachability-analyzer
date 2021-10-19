from helper.utils import recover_output_telnet, recover_output_wf
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
        ('''ComputerName           : 172.31.255.50
            RemoteAddress          : 172.31.255.50
            RemotePort             : 5030
            InterfaceAlias         : Ethernet 3
            SourceAddress          : 172.31.255.20
            PingSucceeded          : True
            PingReplyDetails (RTT) : 0 ms
            TcpTestSucceeded       : False''',
        "false"),
    ]
    @pytest.mark.parametrize("output,expected_result", testdata)
    def test_recover_output_telnet(self, output, expected_result):
        
        # Arrange
        
        # Act
        result = recover_output_telnet(output)
        
        # Assert
        assert expected_result == result
    
    testdata = [
        ('''State ON

            State ON

            State ON''',
        "Some firewalls are enabled on the server"),
        (''' State ON


            State OFF

            State OFF ''',
        "Some firewalls are enabled on the server"),
        (''' State ON


            State OFF

            State ON ''',
        "Some firewalls are enabled on the server"),
        (''' State OFF


            State OFF

            State ON ''',
        "Some firewalls are enabled on the server"),
        (''' State OFF


            State OFF

            State OFF ''',
        "All the firewalls are turned off on the server"),
    ]
    @pytest.mark.parametrize("output,expected_result", testdata)
    def test_recover_output_wf(self, output, expected_result):
        
        # Arrange
        
        # Act
        _, result = recover_output_wf(output)
        
        # Assert
        assert expected_result == result