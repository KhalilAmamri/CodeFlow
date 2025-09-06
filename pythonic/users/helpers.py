

"""
User Helper Functions

This module contains utility functions for user-related operations
such as sending password reset emails.
"""

import os
from flask import url_for
from flask_mail import Message

from pythonic import mail


def send_reset_email(user):
    token = user.get_reset_token()
    sender_email = os.getenv('EMAIL_USER') or 'noreply@pythonic.com'
    msg = Message('Password Reset Request', sender=sender_email, recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)