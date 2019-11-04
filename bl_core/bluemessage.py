class BluebotMessage():
    """
        Create some blueprint Class for Message type, so we will have standarize type
    """
    def type_name(self):
        """
            To handle request type from the chatbot
            To define request type for front end do it on send() method
        """
        pass

    def send(self, session_id, data):
        """
            Send method, to send the result to front end as a request
        """
        pass