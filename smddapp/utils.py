from django.core.mail import EmailMessage
import random
import string


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], 
            body=data['email_body'],
            to=[data['to_email']],
        )

        email.send()


def generate_username(first_name):
    first_name = first_name.lower().replace(" ", "")
    random_number = random.randint(100, 999)
    random_letters = ''.join(random.choice(string.ascii_lowercase) for _ in range(2))
    username = f"{first_name}{random_letters}{random_number}"
    return username

