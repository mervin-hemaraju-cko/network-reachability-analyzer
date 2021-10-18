import pytest, os
from main import extract_nra_parameters, validate_request

class TestMain:
    
    testdata = [
        ({}, "Missing parameters."),
        ({"Texting"}, "Missing parameters."),
        ({"text": []}, "Missing parameters."),
        ({"text": [""]}, "Missing parameters. Parameters should be provided in this format: source destination port protocol"),
        ({"text": ["1 2 3"]}, "Missing parameters. Parameters should be provided in this format: source destination port protocol"),
        ({"text": ["1 2 3 4 5"]}, "Missing parameters. Parameters should be provided in this format: source destination port protocol"),
        ({"text": ["1 2 3 4"]}, "Passed"),
    ]
    @pytest.mark.parametrize("payload,expected_result", testdata)
    def test_extract_nra_parameters(self, payload, expected_result):
        # Arrange
                
        # Act 
        try:
            source, destination, port, protocol = extract_nra_parameters(payload)
            result = "Passed"
        except Exception as e:
            result = str(e)

        # Assert
        assert expected_result == result
    
    testdata = [
        ({}, "Wrong payload provided."),
        ({"post": "token=something&team_id=something"}, "Wrong payload provided."),
        ({"postBody": "tok=something&team_id=something"}, "Access denied. Token not provided"),
        ({"postBody": "token=something&team_id=something"}, "Access denied. Wrong token provided"),
        ({"postBody": f"token={os.environ['TOKEN_VERIFICATION_SLACK_SYSAPP']}&team_id=something"}, {"token": [os.environ['TOKEN_VERIFICATION_SLACK_SYSAPP']], "team_id": ["something"]}),
    ]
    @pytest.mark.parametrize("event,expected_result", testdata)
    def test_validate_request(self, event, expected_result):
        # Arrange
                
        # Act 
        try:
            result = validate_request(event)
        except Exception as e:
            result = str(e)

        # Assert
        assert expected_result == result