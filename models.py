from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField,IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,InputRequired,Length
from flask_mail import Message
from flask_mail import Mail
from flask_wtf.file import FileField, FileRequired
from wtforms.widgets import TextArea
from flask import Flask, render_template, url_for,redirect,flash,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import UserMixin
import os
app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
# 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
print (os.environ.get("EMAIL_USER")) 
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
	customer_id=db.Column(db.Integer,primary_key=True)
	customer_name=db.Column(db.String(50))
	customer_username=db.Column(db.String(50),unique=True)
	customer_password=db.Column(db.String(50))
	customer_contact=db.Column(db.String(50))
	email = db.Column(db.String(100), unique=True)

	 
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

	
	def __init__(self,customer_name,customer_username,customer_password,customer_contact):
		self.customer_name=customer_name
		self.customer_username=customer_username
		self.customer_password=customer_password
		self.customer_contact=customer_contact


    








class ProductFill(FlaskForm):
	seller_id=IntegerField('Seller-Id',validators=[InputRequired()])
	product_name=StringField('Product-Name',validators=[InputRequired()])
	product_category=StringField('Category',validators=[InputRequired()])
	product_description=StringField('Description',validators=[InputRequired()],widget=TextArea())
	product_price=IntegerField('Price',validators=[InputRequired()])
	product_image=FileField('Image',validators=[FileRequired()])
	product_quantity=IntegerField('Quantity',validators=[InputRequired()])

class ProductRemove(FlaskForm):
	seller_id=IntegerField('Seller-Id',validators=[InputRequired()])
	product_id=IntegerField('Product-Id',validators=[InputRequired()])


class Applicationform(FlaskForm):
	key=IntegerField('Admin Security Key',validators=[InputRequired()])	

class SearchForm(FlaskForm):
	search=StringField('Search',validators=[InputRequired()])

class PayForm(FlaskForm):
	name=StringField('Name',validators=[InputRequired()])
	card_no=IntegerField('Price',validators=[InputRequired()])
	address=StringField('Name2',validators=[InputRequired()])
	cvc=IntegerField('Price2',validators=[InputRequired()])
	expiration_m=IntegerField('Name3',validators=[InputRequired()])
	expiration_y=IntegerField('Name4',validators=[InputRequired()])


class sellers(db.Model):
	seller_id=db.Column(db.Integer,primary_key=True)
	customer_id=db.Column(db.Integer,unique=True)
	seller_contact=db.Column(db.String(50))
	def __init__(self,customer_id,seller_contact):
		self.customer_id=customer_id
		self.seller_contact=seller_contact

class products(db.Model):
	product_id=db.Column(db.Integer,primary_key=True)
	product_name=db.Column(db.String(50))
	seller_id=db.Column(db.Integer)
	product_category=db.Column(db.String(50))
	product_description=db.Column(db.String(150))
	product_price=db.Column(db.Integer)
	product_image=db.Column(db.String(50))
	product_quantity=db.Column(db.Integer)
	no_of_raters=db.Column(db.Integer)
	product_rating=db.Column(db.Integer)
	def __init__(self,seller_id,product_name,product_category,product_description,product_price,product_image,product_quantity,no_of_raters=0,product_rating=0):
		self.product_name=product_name
		self.seller_id=seller_id
		self.product_category=product_category
		self.product_description=product_description
		self.product_price=product_price
		self.product_image=product_image
		self.product_quantity=product_quantity
		self.no_of_raters=no_of_raters
		self.product_rating=product_rating

class sales(db.Model):
	serial_no=db.Column(db.Integer,primary_key=True)
	product_id=db.Column(db.Integer)
	seller_id=db.Column(db.Integer)
	customer_id=db.Column(db.Integer)
	def __init__(self,product_id,seller_id,customer_id):
		self.product_id=product_id
		self.seller_id=seller_id
		self.customer_id=customer_id

class cart(db.Model):
	serial_no=db.Column(db.Integer,primary_key=True)
	product_id=db.Column(db.Integer)
	customer_id=db.Column(db.Integer)
	product_name=db.Column(db.String(50))
	product_image=db.Column(db.String(50))
	def __init__(self,product_id,customer_id,product_name,product_image):
		self.product_id=product_id
		self.customer_id=customer_id
		self.product_name=product_name
		self.product_image=product_image


class SignupForm(FlaskForm):
	email = StringField('Email',
                        validators=[DataRequired(), Email()])
	username=StringField('Username',validators=[InputRequired()])
	password=PasswordField('Password',validators=[InputRequired(),Length(min=6,max=100,message="Must contain greater than 6 characters")])
	contact=StringField('Contact Number',validators=[InputRequired()])

class LoginForm(FlaskForm):
	username=StringField('Username',validators=[InputRequired()])
	password=PasswordField('Password',validators=[InputRequired(),Length(min=6,max=100)])
	submit = SubmitField('Login')

# class RegistrationForm(FlaskForm):
#     username = StringField('Username',
#                            validators=[DataRequired(), Length(min=2, max=20)])
#     email = StringField('Email',
#                         validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm Password',
#                                      validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Sign Up')

#     def validate_username(self, username):
#         user = User.query.filter_by(username=username.data).first()
#         if user:
#             raise ValidationError('That username is taken. Please choose a different one.')

#     def validate_email(self, email):
#         user = User.query.filter_by(email=email.data).first()
#         if user:
#             raise ValidationError('That email is taken. Please choose a different one.')


# class LoginForm(FlaskForm):
#     email = StringField('Email',
#                         validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     remember = BooleanField('Remember Me')
#     submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    # email = StringField('Email',
    #                     validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    # def validate_email(self, email):
    #     if email.data != current_user.email:
    #         user = User.query.filter_by(email=email.data).first()
    #         if user:
    #             raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('An email has been sent with instructions to reset your password.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')



