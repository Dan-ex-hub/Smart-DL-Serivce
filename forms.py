from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, DateField, SelectField, 
                    TextAreaField, FileField, SubmitField, HiddenField, TimeField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from datetime import date, datetime, timedelta

# Login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Signup form
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

# Learning License application form
class LearningLicenseForm(FlaskForm):
    # Personal Information
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    place_of_birth = StringField('Place of Birth', validators=[DataRequired(), Length(max=100)])
    
    # Contact Information
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Address Information
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    state = StringField('State', validators=[DataRequired(), Length(max=50)])
    zip_code = StringField('ZIP Code', validators=[DataRequired(), Length(max=10)])
    
    # Medical Information
    blood_group = SelectField('Blood Group', choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    rh_factor = SelectField('Rh Factor', choices=[('positive', 'Positive'), ('negative', 'Negative')], validators=[DataRequired()])
    
    # Citizenship Information
    citizenship = StringField('Citizenship', validators=[DataRequired()])
    
    # Document Information
    document_type = SelectField('Document Type', choices=[
        ('aadhar', 'Aadhar Card'), 
        ('passport', 'Passport'), 
        ('voter_id', 'Voter ID'),
        ('pan_card', 'PAN Card')
    ], validators=[DataRequired()])
    document = FileField('Upload Document')
    
    submit = SubmitField('Submit Application')
    
    def validate_dob(self, field):
        today = date.today()
        age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
        if age < 18:
            raise ValidationError('You must be at least 18 years old to apply for a license.')

# Driving License application form
class DrivingLicenseForm(FlaskForm):
    learning_license_id = StringField('Learning License Application ID', validators=[DataRequired()])
    
    # Test slot booking
    test_date = DateField('Preferred Test Date', validators=[DataRequired()])
    test_time = SelectField('Preferred Time Slot', choices=[
        ('09:00', '9:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '1:00 PM'),
        ('14:00', '2:00 PM'),
        ('15:00', '3:00 PM'),
        ('16:00', '4:00 PM')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Book Test Slot')
    
    def validate_test_date(self, field):
        # Ensure test date is at least 7 days in the future
        min_date = datetime.now().date() + timedelta(days=7)
        if field.data < min_date:
            raise ValidationError(f'Test date must be at least 7 days from today ({min_date.strftime("%Y-%m-%d")}).')
        
        # Ensure test date is not more than 60 days in the future
        max_date = datetime.now().date() + timedelta(days=60)
        if field.data > max_date:
            raise ValidationError(f'Test date cannot be more than 60 days from today ({max_date.strftime("%Y-%m-%d")}).')

# Renew License form
class RenewLicenseForm(FlaskForm):
    license_number = StringField('Driving License Number', validators=[DataRequired()])
    renewal_reason = SelectField('Reason for Renewal', choices=[
        ('expiring', 'License Expiring'),
        ('expired', 'License Expired'),
        ('damaged', 'License Damaged/Lost')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Renew License')

# Change Details form
class ChangeDetailsForm(FlaskForm):
    license_number = HiddenField('License Number')
    
    # New address details
    address = StringField('New Address', validators=[DataRequired(), Length(max=200)])
    city = StringField('New City', validators=[DataRequired(), Length(max=50)])
    state = StringField('New State', validators=[DataRequired(), Length(max=50)])
    zip_code = StringField('New ZIP Code', validators=[DataRequired(), Length(max=10)])
    phone = StringField('New Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    
    submit = SubmitField('Update Details')

# Status Check form
class StatusCheckForm(FlaskForm):
    application_id = StringField('Application ID', validators=[DataRequired()])
    submit = SubmitField('Check Status')

# Payment form
class PaymentForm(FlaskForm):
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16)])
    card_holder = StringField('Card Holder Name', validators=[DataRequired()])
    expiry_date = StringField('Expiry Date (MM/YY)', validators=[DataRequired()])
    cvv = StringField('CVV', validators=[DataRequired(), Length(min=3, max=3)])
    amount = HiddenField('Amount')
    
    submit = SubmitField('Pay Now')
