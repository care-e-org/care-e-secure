from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class PartnerLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=96)])
    password = PasswordField('Temporary Password', validators=[DataRequired()])
    submit = SubmitField('Partner Login')


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField('Update Password')

class HospitalRegistrationForm(FlaskForm):
    facility_name = StringField('Facility Name', validators=[DataRequired(), Length(max=100)])
    organization_type = SelectField('Organization Type', choices=[('hospital', 'Hospital'), ('clinic', 'Clinic')], validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[DataRequired(), Length(max=100)])
    contact_email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    contact_phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    pickup_location = StringField('Facility Address', validators=[DataRequired(), Length(max=200)])
    notes = TextAreaField('Additional Notes', validators=[Length(max=500)])
    submit = SubmitField('Register as Hospital')

class SupplierRegistrationForm(FlaskForm):
    facility_name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    organization_type = SelectField('Organization Type', choices=[ ('blood_bank', 'Blood Bank'), ('logistics', 'Logistics Provider'), ('fleet', 'Independent Fleet')], validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[DataRequired(), Length(max=100)])
    contact_email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    contact_phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    operating_zone = StringField('Operating Region/Zone', validators=[DataRequired(), Length(max=200)])
    cold_storage_capacity = SelectField('Cold Storage Capacity', choices=[('small', 'Small (<500L)'), ('medium', 'Medium (500L-2000L)'), ('large', 'Large (>2000L)')], validators=[DataRequired()])
    temperature_capability = SelectField('Temperature Capability', choices=[('ambient', 'Ambient (15-25 C)'), ('refrigerated', 'Refrigerated (2-8 C)'), ('frozen', 'Frozen (-20 C)'), ('ultra_cold', 'Ultra-Cold (-70 C)')], validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', validators=[Length(max=500)])
    submit = SubmitField('Apply as Supplier')


class SupplierOfferingForm(FlaskForm):
    title = StringField('Supply Title', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('What is being supplied', validators=[DataRequired(), Length(max=1000)])
    quantity = StringField('Quantity / Capacity', validators=[DataRequired(), Length(max=50)])
    availability = SelectField('Availability', choices=[('Available', 'Available'), ('Limited', 'Limited'), ('Out of Stock', 'Out of Stock')], validators=[DataRequired()])
    submit = SubmitField('Upload Supply')
