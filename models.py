from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    learning_licenses = db.relationship('LearningLicense', backref='user', lazy=True)
    driving_licenses = db.relationship('DrivingLicense', backref='user', lazy=True)
    license_renewals = db.relationship('LicenseRenewal', backref='user', lazy=True)
    change_requests = db.relationship('LicenseChangeRequest', backref='user', lazy=True)

class LearningLicense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Personal Information
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    place_of_birth = db.Column(db.String(100), nullable=False)
    
    # Contact Information
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    # Address Information
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    
    # License Information
    license_type = db.Column(db.String(50), default='Learning License')
    
    # Medical Information
    blood_group = db.Column(db.String(5), nullable=False)
    rh_factor = db.Column(db.String(10), nullable=False)
    
    # Citizenship Information
    citizenship = db.Column(db.String(50), nullable=False)
    
    # Document Information
    document_type = db.Column(db.String(50), nullable=False)
    document_path = db.Column(db.String(255), nullable=True)
    
    # Application Status
    status = db.Column(db.String(20), default='Processing')
    apply_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    driving_licenses = db.relationship('DrivingLicense', backref='learning_license', lazy=True)

class DrivingLicense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String(20), unique=True, nullable=False)
    license_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    learning_license_id = db.Column(db.String(20), db.ForeignKey('learning_license.application_id'), nullable=False)
    
    # Personal Information (copied from Learning License)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    place_of_birth = db.Column(db.String(100), nullable=False)
    
    # Contact Information
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    # Address Information
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    
    # License Information
    license_type = db.Column(db.String(50), default='Driving License')
    
    # Medical Information
    blood_group = db.Column(db.String(5), nullable=False)
    rh_factor = db.Column(db.String(10), nullable=False)
    
    # Citizenship Information
    citizenship = db.Column(db.String(50), nullable=False)
    
    # Test Information
    test_date = db.Column(db.Date, nullable=False)
    test_time = db.Column(db.String(10), nullable=False)
    
    # Application Status
    status = db.Column(db.String(20), default='Scheduled')
    apply_date = db.Column(db.DateTime, default=datetime.utcnow)
    issue_date = db.Column(db.DateTime, nullable=True)
    expiry_date = db.Column(db.DateTime, nullable=False)
    
    # Relationships
    renewals = db.relationship('LicenseRenewal', backref='driving_license', lazy=True)
    changes = db.relationship('LicenseChangeRequest', backref='driving_license', lazy=True)

class LicenseRenewal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    license_number = db.Column(db.String(20), db.ForeignKey('driving_license.license_number'), nullable=False)
    renewal_date = db.Column(db.DateTime, default=datetime.utcnow)
    renewal_reason = db.Column(db.String(200), nullable=False)
    old_expiry_date = db.Column(db.DateTime, nullable=False)
    new_expiry_date = db.Column(db.DateTime, nullable=False)

class LicenseChangeRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    license_number = db.Column(db.String(20), db.ForeignKey('driving_license.license_number'), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Old values
    old_address = db.Column(db.String(200), nullable=False)
    old_city = db.Column(db.String(50), nullable=False)
    old_state = db.Column(db.String(50), nullable=False)
    old_zip = db.Column(db.String(10), nullable=False)
    old_phone = db.Column(db.String(15), nullable=False)
    
    # New values
    new_address = db.Column(db.String(200), nullable=False)
    new_city = db.Column(db.String(50), nullable=False)
    new_state = db.Column(db.String(50), nullable=False)
    new_zip = db.Column(db.String(10), nullable=False)
    new_phone = db.Column(db.String(15), nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='Pending')
