from helper.utils import recover_output_telnet, recover_output_wf, determine_final_action
import helper.constants as Consts
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
    
    testdata = [
        
        # Testing Operations Failed
        (
            {"success": False, "operation_success": True},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": True},
            Consts.FINAL_ACTION_UNDETERMINED
        ),
        (
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": True},
            {"success": False, "operation_success": True},
            {"success": True, "operation_success": True},
            Consts.FINAL_ACTION_UNDETERMINED
        ),
        (
            {"success": False, "operation_success": True},
            {"success": True, "operation_success": True},
            {"success": False, "operation_success": True},
            {"success": True, "operation_success": True},
            Consts.FINAL_ACTION_UNDETERMINED
        ),
        (
            {"success": False, "operation_success": True},
            {"success": False, "operation_success": True},
            {"success": False, "operation_success": True},
            {"success": False, "operation_success": True},
            Consts.FINAL_ACTION_UNDETERMINED
        ),
        
        # Testing for Telnet success
        (
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": False},
            Consts.FINAL_ACTION_NONE_REQ
        ),
        (
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": True},
            Consts.FINAL_ACTION_NONE_REQ
        ),
        
        # Testing for no blocking points
        (
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": False},
            Consts.FINAL_ACTION_NONE_REQ
        ),
        
        # Testing for WF blocking
        (
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": True},
            Consts.FINAL_ACTION_WF_BLOCKING
        ),
        
        # Testing for AWS blocking
        (
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": False},
            Consts.FINAL_ACTION_AWS_BLOCKING
        ),
        
        # Testing for PC blocking
        (
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": False},
            Consts.FINAL_ACTION_PC_BLOCKING
        ),
        
        # Testing for PC and WF blocking
        (
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": True},
            Consts.FINAL_ACTION_PC_WF_BLOCKING
        ),
        
        # Testing for AWS and WF blocking
        (
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": True},
            {"success": True, "operation_success": True},
            Consts.FINAL_ACTION_AWS_WF_BLOCKING
        ),
        
        # Testing for AWS and PC blocking
        (
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": False},
            Consts.FINAL_ACTION_AWS_PC_BLOCKING
        ),
        
        # Testing for AWS, PC and WF blocking
        (
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": False},
            {"success": True, "operation_success": True},
            Consts.FINAL_ACTION_AWS_PC_WF_BLOCKING
        ), 
    ]
    @pytest.mark.parametrize("output_telnet,output_nia,output_port_checker,output_wf_checker,expected_result", testdata)
    def test_determine_final_action(self, output_telnet, output_nia, output_port_checker, output_wf_checker, expected_result):
        
        # Arrange
        
        # Act
        result = determine_final_action(
            output_telnet=output_telnet,
            output_nia=output_nia,
            output_port_checker=output_port_checker,
            output_wf_checker=output_wf_checker
        )
        
        # Assert
        assert expected_result == result