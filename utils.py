import random
import string
from datetime import datetime
from flask import session

def generate_application_id():
    """Generate a unique application ID with prefix 'APP' followed by timestamp and random chars"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"APP{timestamp}{random_chars}"

def generate_license_number():
    """Generate a unique license number with prefix 'DL' followed by timestamp and random chars"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"DL{timestamp}{random_chars}"

def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session
