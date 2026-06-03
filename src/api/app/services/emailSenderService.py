class EmailSender:

    @staticmethod   
    def send_email(to_email: str, subject: str, body: str, attachment_data: bytes, attachment_name: str)->bool:       
        return True