import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import secrets
import string
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Setup SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize Flask app and database
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_for_development_only")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///dlservice.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

# Initialize the app with the extension
db.init_app(app)

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Import models after db initialization to avoid circular imports
with app.app_context():
    from models import User, LearningLicense, DrivingLicense, LicenseRenewal, LicenseChangeRequest
    db.create_all()

# Import forms
from forms import (LoginForm, SignupForm, LearningLicenseForm, DrivingLicenseForm, 
                   RenewLicenseForm, ChangeDetailsForm, StatusCheckForm, PaymentForm)

# Import utility functions
from utils import generate_application_id, generate_license_number, is_logged_in

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists', 'danger')
            return render_template('signup.html', form=form)
            
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email already registered', 'danger')
            return render_template('signup.html', form=form)
            
        # Create new user
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# Home route
@app.route('/')
@app.route('/home')
def home():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('home.html', username=session.get('username'))

# Learning License application route
@app.route('/learning-license', methods=['GET', 'POST'])
def learning_license():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    form = LearningLicenseForm()
    if form.validate_on_submit():
        # Store form data in session for payment
        session['learning_license_data'] = {
            'name': form.name.data,
            'dob': form.dob.data.strftime('%Y-%m-%d'),
            'gender': form.gender.data,
            'place_of_birth': form.place_of_birth.data,
            'phone': form.phone.data,
            'email': form.email.data,
            'address': form.address.data,
            'city': form.city.data,
            'state': form.state.data,
            'zip_code': form.zip_code.data,
            'license_type': 'Learning License',
            'blood_group': form.blood_group.data,
            'rh_factor': form.rh_factor.data,
            'citizenship': form.citizenship.data,
            'document_type': form.document_type.data
        }
        
        # Handle document upload if provided
        if form.document.data:
            filename = secure_filename(form.document.data.filename)
            random_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            new_filename = f"{session['user_id']}_{random_string}_{filename}"
            form.document.data.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            session['learning_license_data']['document_filename'] = new_filename
        
        # Redirect to payment page
        return redirect(url_for('payment', license_type='learning'))
    
    return render_template('learning_license.html', form=form)

# Driving License application route
@app.route('/driving-license', methods=['GET', 'POST'])
def driving_license():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    form = DrivingLicenseForm()
    if form.validate_on_submit():
        # Verify learning license exists
        learning_license = LearningLicense.query.filter_by(
            application_id=form.learning_license_id.data,
            user_id=session['user_id']
        ).first()
        
        if not learning_license:
            flash('Invalid Learning License ID or license does not belong to you', 'danger')
            return render_template('driving_license.html', form=form)
        
        # Store data in session for payment
        session['driving_license_data'] = {
            'learning_license_id': form.learning_license_id.data,
            'test_date': form.test_date.data.strftime('%Y-%m-%d'),
            'test_time': form.test_time.data
        }
        
        # Redirect to payment page
        return redirect(url_for('payment', license_type='driving'))
    
    return render_template('driving_license.html', form=form)

# Renew License route
@app.route('/renew-license', methods=['GET', 'POST'])
def renew_license():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    form = RenewLicenseForm()
    if form.validate_on_submit():
        # Check if driving license exists
        driving_license = DrivingLicense.query.filter_by(
            license_number=form.license_number.data,
            user_id=session['user_id']
        ).first()
        
        if not driving_license:
            flash('Invalid License Number or license does not belong to you', 'danger')
            return render_template('renew_license.html', form=form)
        
        # Store data in session for payment
        session['renewal_data'] = {
            'license_number': form.license_number.data,
            'renewal_reason': form.renewal_reason.data
        }
        
        # Redirect to payment page
        return redirect(url_for('payment', license_type='renewal'))
    
    return render_template('renew_license.html', form=form)

# Change Details route
@app.route('/change-details', methods=['GET', 'POST'])
def change_details():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    form = ChangeDetailsForm()
    
    if request.method == 'POST' and 'license_number' in request.form and not form.address.data:
        # This is the license verification step
        license_number = request.form['license_number']
        driving_license = DrivingLicense.query.filter_by(
            license_number=license_number,
            user_id=session['user_id']
        ).first()
        
        if not driving_license:
            flash('Invalid License Number or license does not belong to you', 'danger')
            return render_template('change_details.html', form=None)
        
        # Pre-fill the form with current details
        form.license_number.data = license_number
        form.address.data = driving_license.address
        form.city.data = driving_license.city
        form.state.data = driving_license.state
        form.zip_code.data = driving_license.zip_code
        form.phone.data = driving_license.phone
        
        return render_template('change_details.html', form=form, license_verified=True)
    
    elif form.validate_on_submit() and form.license_number.data:
        # This is the form submission after verification
        driving_license = DrivingLicense.query.filter_by(
            license_number=form.license_number.data,
            user_id=session['user_id']
        ).first()
        
        if not driving_license:
            flash('License not found', 'danger')
            return redirect(url_for('change_details'))
        
        # Create change request record
        change_request = LicenseChangeRequest(
            user_id=session['user_id'],
            license_number=form.license_number.data,
            old_address=driving_license.address,
            new_address=form.address.data,
            old_city=driving_license.city,
            new_city=form.city.data,
            old_state=driving_license.state,
            new_state=form.state.data,
            old_zip=driving_license.zip_code,
            new_zip=form.zip_code.data,
            old_phone=driving_license.phone,
            new_phone=form.phone.data,
            status='Pending'
        )
        
        # Update license details
        driving_license.address = form.address.data
        driving_license.city = form.city.data
        driving_license.state = form.state.data
        driving_license.zip_code = form.zip_code.data
        driving_license.phone = form.phone.data
        
        db.session.add(change_request)
        db.session.commit()
        
        flash('Your details have been updated successfully', 'success')
        return redirect(url_for('home'))
    
    return render_template('change_details.html', form=None)

# Application Status route
@app.route('/application-status', methods=['GET', 'POST'])
def application_status():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    form = StatusCheckForm()
    application = None
    
    if form.validate_on_submit():
        application_id = form.application_id.data
        
        # Check for Learning License
        learning_license = LearningLicense.query.filter_by(
            application_id=application_id,
            user_id=session['user_id']
        ).first()
        
        if learning_license:
            application = {
                'type': 'Learning License',
                'id': learning_license.application_id,
                'status': learning_license.status,
                'apply_date': learning_license.apply_date,
                'estimate': '7-10 business days'
            }
        else:
            # Check for Driving License
            driving_license = DrivingLicense.query.filter_by(
                application_id=application_id,
                user_id=session['user_id']
            ).first()
            
            if driving_license:
                application = {
                    'type': 'Driving License',
                    'id': driving_license.application_id,
                    'status': driving_license.status,
                    'apply_date': driving_license.apply_date,
                    'estimate': '14-21 business days'
                }
            else:
                flash('Application not found or does not belong to you', 'danger')
    
    return render_template('application_status.html', form=form, application=application)

# Check RC Details route (placeholder)
@app.route('/check-rc')
def check_rc():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    return render_template('check_rc.html')

# Payment processing route
@app.route('/payment/<license_type>', methods=['GET', 'POST'])
def payment(license_type):
    if not is_logged_in():
        return redirect(url_for('login'))
    
    # Set payment amount based on license type
    amount = 0
    if license_type == 'learning':
        amount = 500
    elif license_type == 'driving':
        amount = 1000
    elif license_type == 'renewal':
        amount = 750
    else:
        abort(404)
    
    form = PaymentForm()
    form.amount.data = amount
    
    if form.validate_on_submit():
        # Process payment based on license type
        if license_type == 'learning' and 'learning_license_data' in session:
            # Create Learning License record
            data = session['learning_license_data']
            application_id = generate_application_id()
            
            new_application = LearningLicense(
                application_id=application_id,
                user_id=session['user_id'],
                name=data['name'],
                dob=datetime.strptime(data['dob'], '%Y-%m-%d'),
                gender=data['gender'],
                place_of_birth=data['place_of_birth'],
                phone=data['phone'],
                email=data['email'],
                address=data['address'],
                city=data['city'],
                state=data['state'],
                zip_code=data['zip_code'],
                license_type=data['license_type'],
                blood_group=data['blood_group'],
                rh_factor=data['rh_factor'],
                citizenship=data['citizenship'],
                document_type=data['document_type'],
                document_path=data.get('document_filename', ''),
                status='Processing',
                apply_date=datetime.now()
            )
            
            db.session.add(new_application)
            db.session.commit()
            
            # Clear session data
            session.pop('learning_license_data', None)
            
            return render_template('confirmation.html', 
                                  application_id=application_id, 
                                  license_type='Learning License')
        
        elif license_type == 'driving' and 'driving_license_data' in session:
            # Create Driving License record
            data = session['driving_license_data']
            application_id = generate_application_id()
            license_number = generate_license_number()
            
            # Get learning license details
            learning_license = LearningLicense.query.filter_by(
                application_id=data['learning_license_id'],
                user_id=session['user_id']
            ).first()
            
            new_license = DrivingLicense(
                application_id=application_id,
                license_number=license_number,
                user_id=session['user_id'],
                learning_license_id=data['learning_license_id'],
                name=learning_license.name,
                dob=learning_license.dob,
                gender=learning_license.gender,
                place_of_birth=learning_license.place_of_birth,
                phone=learning_license.phone,
                email=learning_license.email,
                address=learning_license.address,
                city=learning_license.city,
                state=learning_license.state,
                zip_code=learning_license.zip_code,
                license_type='Driving License',
                blood_group=learning_license.blood_group,
                rh_factor=learning_license.rh_factor,
                citizenship=learning_license.citizenship,
                test_date=datetime.strptime(data['test_date'], '%Y-%m-%d'),
                test_time=data['test_time'],
                status='Scheduled',
                apply_date=datetime.now(),
                expiry_date=datetime.now().replace(year=datetime.now().year + 10)
            )
            
            db.session.add(new_license)
            db.session.commit()
            
            # Clear session data
            session.pop('driving_license_data', None)
            
            return render_template('confirmation.html', 
                                  application_id=application_id,
                                  license_number=license_number,
                                  license_type='Driving License')
        
        elif license_type == 'renewal' and 'renewal_data' in session:
            # Process license renewal
            data = session['renewal_data']
            
            # Get driving license details
            driving_license = DrivingLicense.query.filter_by(
                license_number=data['license_number'],
                user_id=session['user_id']
            ).first()
            
            # Update expiry date
            current_expiry = driving_license.expiry_date
            driving_license.expiry_date = current_expiry.replace(year=current_expiry.year + 10)
            driving_license.status = 'Renewed'
            
            # Create renewal record
            renewal = LicenseRenewal(
                user_id=session['user_id'],
                license_number=data['license_number'],
                renewal_date=datetime.now(),
                renewal_reason=data['renewal_reason'],
                old_expiry_date=current_expiry,
                new_expiry_date=driving_license.expiry_date
            )
            
            db.session.add(renewal)
            db.session.commit()
            
            # Clear session data
            session.pop('renewal_data', None)
            
            return render_template('confirmation.html',
                                  license_number=data['license_number'],
                                  license_type='License Renewal')
        
        else:
            flash('Invalid request', 'danger')
            return redirect(url_for('home'))
    
    return render_template('payment.html', form=form, license_type=license_type, amount=amount)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
