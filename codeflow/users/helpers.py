"""
User Helper Functions

This module contains utility functions for user-related operations
such as sending password reset emails.
"""

import os
from flask import url_for
from codeflow.users.sendgrid_helper import sendgrid_send_email

def send_reset_email(user):
    token = user.get_reset_token()
    subject = 'Password Reset Request'
    body = f'''To reset your password, visit the following link:\n{url_for('users.reset_token', token=token, _external=True)}\nIf you did not make this request then simply ignore this email and no changes will be made.'''
    return sendgrid_send_email(user.email, subject, body)