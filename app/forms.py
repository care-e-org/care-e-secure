from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class HospitalRegistrationForm(FlaskForm):
    facility_name = StringField('Facility Name', validators=[DataRequired(), Length(max=100)])
    organization_type = SelectField('Organization Type', choices=[('hospital', 'Hospital'), ('clinic', 'Clinic'), ('blood_bank', 'Blood Bank')], validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[DataRequired(), Length(max=100)])
    contact_email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    contact_phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    pickup_location = StringField('Facility Address', validators=[DataRequired(), Length(max=200)])
    priority_level = SelectField('Priority Level', choices=[('Routine', 'Routine'), ('Urgent', 'Urgent'), ('Critical', 'Critical')], validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', validators=[Length(max=500)])
    submit = SubmitField('Register as Hospital')

class SupplierRegistrationForm(FlaskForm):
    facility_name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    organization_type = SelectField('Organization Type', choices=[('logistics', 'Logistics Provider'), ('fleet', 'Independent Fleet')], validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[DataRequired(), Length(max=100)])
    contact_email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    contact_phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    operating_zone = StringField('Operating Region/Zone', validators=[DataRequired(), Length(max=200)])
    cold_storage_capacity = SelectField('Cold Storage Capacity', choices=[('small', 'Small (<500L)'), ('medium', 'Medium (500L-2000L)'), ('large', 'Large (>2000L)')], validators=[DataRequired()])
    temperature_capability = SelectField('Temperature Capability', choices=[('ambient', 'Ambient (15-25 C)'), ('refrigerated', 'Refrigerated (2-8 C)'), ('frozen', 'Frozen (-20 C)'), ('ultra_cold', 'Ultra-Cold (-70 C)')], validators=[DataRequired()])
    priority_level = SelectField('Availability', choices=[('Routine', 'Routine'), ('Urgent', 'Urgent'), ('Critical', '24/7 Critical Response')], validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', validators=[Length(max=500)])
    submit = SubmitField('Apply as Supplier')
