from models.exceptions import SlackPayloadProcessing

class SlackCaller:
    
    def __init__(self, payload) -> None:
        
        try:
            self.calling_channel_id = payload['channel_id'][0]
            self.calling_channel_name = payload['channel_name'][0]
            self.user = payload['user_name'][0]
            self.response_url = payload['response_url'][0]
        
        except:
            raise SlackPayloadProcessing("Cannot process payload.")
    