from templated_mail.mail import BaseEmailMessage


class UserConfirmationEmail(BaseEmailMessage):
    template_name = 'users/confirmation_email.html'
