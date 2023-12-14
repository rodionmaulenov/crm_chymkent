import imaplib
import email
import re


class InboxMessages:

    __inbox = None
    __email_ids = None
    __not_processing_email_ids = []

    def __get_inbox(self):
        return self.__inbox

    def __get_email_ids(self):
        return self.__email_ids

    def __get_not_processing_email_ids(self):
        return self.__not_processing_email_ids

    mail = property(__get_inbox)
    email_ids = property(__get_email_ids)
    not_proceed_emails = property(__get_not_processing_email_ids)

    def __call__(self, pk: int, *args, **kwargs):
        self.__not_processing_email_ids.append(pk)
        return self.__not_processing_email_ids

    def login_gmail(self, email_user: str, email_pass: str, email_server: str, email_chapter: str):
        mail = imaplib.IMAP4_SSL(email_server)
        InboxMessages.__inbox = mail
        mail.login(email_user, email_pass)
        mail.select(email_chapter)

    def search_condition(self, search_criteria: str):
        _, email_ids = InboxMessages.__inbox.search(None, search_criteria)
        InboxMessages.__email_ids = email_ids[0].decode().split()

    def extract_message(self) -> str:
        email_ids = InboxMessages.__not_processing_email_ids
        for email_id in email_ids:
            _, email_data = InboxMessages.__inbox.fetch(email_id, "(RFC822)")
            raw_email = email_data[0][1]
            msg = email.message_from_bytes(raw_email)
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode() + f'id - {email_id}\n'
                        yield body

    @staticmethod
    def get_body_email(translation_dict: dict, email: str) -> dict:
        pattern = re.compile(r"(.+?) - (.+?)\n")
        matches = pattern.findall(email)
        # Replace Russian keys with English keys
        translated_matches = [(translation_dict.get(key, key), value.rstrip('\r')) for key, value in matches]

        # Create a dictionary from the translated matches
        result_dict = dict(translated_matches)
        result_dict.pop('Почта', None)
        return result_dict
