
from flask import Flask, render_template, url_for,redirect,flash,send_from_directory,session
from flask_login import  login_user, LoginManager, login_required, logout_user, current_user
from flask_mail import Message
from flask_mail import Mail
from PIL import Image
import secrets
# coding=utf-8
import sys
import os
import glob
import re
import numpy as np
import tensorflow as tf
import tensorflow as tf

# Keras

from keras.models import load_model


# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_uploads import UploadSet,configure_uploads,IMAGES
from models import *
from flask_admin import Admin 
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
import re
#from gevent.pywsgi import WSGIServer



folder=os.path.join('static','images')
photos=UploadSet('photos',IMAGES)
admin=Admin(app)

app.config['UPLOAD_FOLDER']=folder
app.config['UPLOADED_PHOTOS_DEST']='static/images'

configure_uploads(app,photos)


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(sellers, db.session))
admin.add_view(ModelView(products, db.session))


fungicides=products.query.filter_by(product_category='fungicides').all()
insecticides=products.query.filter_by(product_category='insecticides').all()
herbicide=products.query.filter_by(product_category='herbicide').all()

t=products.query.filter(products.product_price>0).all()
five=[]
for i in range(len(t)):
	if(t[i].product_price<=500):
		five.append(t[i])
q=products.query.filter(products.product_price>500).all()
thousand=[]
for i in range(len(q)):
	if(q[i].product_price<=1000):
		thousand.append(q[i])

z=products.query.filter(products.product_price>1000).all()
two=[]
for i in range(len(z)):
	if(z[i].product_price>1000):
		two.append(z[i])



def hack(s):
	if re.findall('[^A-Za-z0-9_]',s):
		return 0
	return 1	

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(customer_id):
    return User.query.get(int(customer_id))


@app.route('/store',methods=['GET','POST'])
def store():
	form=SearchForm()
	if form.validate_on_submit():
		if request.method=='POST':
			f=products.query.filter_by(product_name=form.search.data).scalar()
			f1=products.query.filter_by(product_name=form.search.data).first()
			if f==None:
				flash("Product Not Present","danger")
				return render_template('store.html',nform=SearchForm(),fungicides=fungicides,herbicide=herbicide,insecticides=insecticides,five=five,thousand=thousand,two=two)
			else:
				return redirect('/display_product/'+str(f1.product_id))
	return render_template('store.html',nform=SearchForm(),fungicides=fungicides,herbicide=herbicide,insecticides=insecticides,five=five,thousand=thousand,two=two)



@app.route('/decide')
def decide():
	form=SearchForm()
	if not 'username' in session:
		return render_template('index.html',nform=SearchForm(),fungicides=fungicides,herbicide=herbicide,insecticides=insecticides,five=five,thousand=thousand,two=two)
	else:
		return render_template('welcome2.html',fungicides=fungicides,herbicide=herbicide,insecticides=insecticides,five=five,thousand=thousand,two=two,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)

								#    ADMIN-PAGE  #
@app.route('/admincheck',methods=['GET','POST'])
def adminncheck():
	form=Applicationform()
	if form.validate_on_submit():
		if request.method=='POST':
			if not form.key.data==23415:
				return render_template("admincheck.html",form=form,ans=0,nform=SearchForm())
			else:
				return redirect('/admin')
	return render_template("admincheck.html",form=form,ans=1,nform=SearchForm())

								#  LOGIN AND LOGOUT FUNCTIONALITY  #


@app.route('/signup',methods=['GET','POST'])
def signup():
	form=SignupForm()
	if form.validate_on_submit():
		if request.method=='POST':
			entries=User.query.all()
			for i in entries:
				if i.customer_username==form.username.data:
					return render_template('sign_up.html',form=form,exists=1,nform=SearchForm(),hacker=0)
				elif hack(form.username.data)==0:
					return render_template('sign_up.html',form=form,exists=0,nform=SearchForm(),hacker=1)	
			user=User(form.email.data,form.username.data,generate_password_hash(form.password.data),form.contact.data)
			db.session.add(user)
			db.session.commit()
			form=SearchForm()
			return render_template('dashboard.html',nform=form,fungicides=fungicides,herbicide=herbicide,insecticides=insecticides,five=five,thousand=thousand,two=two)
	
	return render_template('sign_up.html',form=form,exists=0,nform=SearchForm(),hacker=0)
						
@app.route('/logged_in')
def logged_in():
	if 'username' in session:
		a=User.query.filter_by(customer_username=session['username']).first()
		return render_template('dashboard.html',nform=SearchForm(),fungicides=fungicides,herbicide=herbicide,insecticides=insecticides,five=five,thousand=thousand,two=two,id=a.customer_id,idd=User.query.filter_by(customer_username=session['username']).first().customer_id)
	else:
		flash("You need to be logged in first","danger")
		form=SearchForm()
		return render_template('index.html',nform=form,fungicides=fungicides,herbicide=herbicide,insecticides=insecticides,five=five,thousand=thousand,two=two)

@app.route('/login',methods=['GET','POST'])
def login():
	error=None
	form=LoginForm()

	if request.method=='POST':

		entries=User.query.all()
		for i in entries:
			if i.customer_username==form.username.data and check_password_hash(i.customer_password,form.password.data):
				session['username']=form.username.data
				return redirect(url_for('logged_in'))
			elif i.customer_username==form.username.data and not check_password_hash(i.customer_password,form.password.data):
				return render_template('login-form.html',form=form,found=1,wrong_password=1,hacker=0,nform=SearchForm())
			elif hack(form.username.data)==0 :
				return render_template('login-form.html',form=form,found=1,wrong_password=1,hacker=1,nform=SearchForm())			
	return render_template('login-form.html',form=form,found=0,wrong_password=0,hacker=0,nform=SearchForm())

	
@app.route('/login-page')
def login_page():
	form=LoginForm()
	return render_template('login-form.html',form=form,found=1,wrong_password=0,hacker=0,nform=SearchForm())

@app.route('/logout')
def logout():
	form=LoginForm()
	if 'username' in session:
		session.clear()
		return redirect(url_for('home'))
	else:
		return render_template('login-form.html',form=form,found=1,wrong_password=0,nform=SearchForm(),hacker=0)

							#   SELLERS PORTAL  #

@app.route('/authenticate_seller')
def authenticate_seller():
	nform=SearchForm()
	if 'username' in session:
		a=User.query.filter_by(customer_username=session['username']).first()
		b=sellers.query.filter_by(customer_id=a.customer_id).scalar()
		if(b==None):
			return render_template('seller_reg.html',id=a.customer_id,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)
		else:
			return redirect(url_for('sale'))
	else:
		flash("You need to be logged in first","danger")
		return render_template('index.html',nform=SearchForm(),fungicides=fungicides,herbicide=herbicide,insecticides=insecticides,five=five,thousand=thousand,two=two)

@app.route('/add_seller/<int:customer_id>')
def add_seller(customer_id):
	b=User.query.filter_by(customer_id=customer_id).first()
	seller=sellers(customer_id,b.customer_contact)
	db.session.add(seller)
	db.session.commit()
	return redirect(url_for('sale'))



@app.route('/seller')
def sale():
	a=User.query.filter_by(customer_username=session['username']).first()
	b=sellers.query.filter_by(customer_id=a.customer_id).first()
	return render_template('new_sel.html',id=b.seller_id,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)

@app.route('/add',methods=['GET','POST'])
def add():
	error=None
	form=ProductFill()

	if form.validate_on_submit():
		if request.method=='POST':
			f=form.product_image.data
			filename=secure_filename(f.filename)
			f.save('static/images/'+filename)
			a=User.query.filter_by(customer_username=session['username']).first()
			b=sellers.query.filter_by(customer_id=a.customer_id).first()
			if not b.seller_id == form.seller_id.data:
				return render_template('input.html',form=form,wrong=1,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)
			else: 
				product=products(form.seller_id.data,form.product_name.data,form.product_category.data,form.product_description.data,form.product_price.data,filename,form.product_quantity.data)
				db.session.add(product)
				db.session.commit()
				return redirect('/items/'+str(form.seller_id.data))
	return render_template('input.html',form=form,wrong=0,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)	
	
@app.route('/delete',methods=['GET','POST'])
def delete():
	form=ProductRemove()
	if form.validate_on_submit():
		if request.method=='POST':
			tr=products.query.filter_by(product_id=form.product_id.data)
			exists=tr.scalar()
			product=tr.first()
			a=User.query.filter_by(customer_username=session['username']).first()
			b=sellers.query.filter_by(customer_id=a.customer_id).first()
			if exists==None:
				return render_template('input2.html',found=0,form=form,wrong=0,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)
			elif not b.seller_id == form.seller_id.data:
				return render_template('input2.html',wrong=1,found=1,form=form,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)
			elif not product.seller_id==form.seller_id.data:
				return render_template('input2.html',found=0,form=form,wrong=0,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)
			else:
				tr.delete()
				db.session.commit()
				return redirect('/items/'+str(form.seller_id.data)) 
				
	return render_template('input2.html',form=form,found=1,wrong=0,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)

@app.route('/items/<int:seller_id>')
def items(seller_id):
	q=products.query.filter_by(seller_id=seller_id).all()
	return render_template('my_products.html',product=q,id=seller_id,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)

					# SOLD ITEMS
@app.route('/pay_on_buy/<int:customer_id>/<int:sum>',methods=['GET','POST'])
def pay_on_buy(customer_id,sum):
	form=PayForm()
	if form.validate_on_submit():
		if request.method=='POST':
			return redirect('/buy_all/'+str(customer_id))
	return render_template('pay.html',nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id,form=form,sum=sum)

@app.route('/sold_items/<int:product_id>')
def sold_items(product_id):
	a=products.query.filter_by(product_id=product_id).first()
	b=User.query.filter_by(customer_username=session['username']).first()
	tr=sales(a.product_id,a.seller_id,b.customer_id)
	db.session.add(tr)
	db.session.commit()
	return render_template('rating.html',nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)



@app.route('/add_in_cart/<int:product_id>')
def add_in_cart(product_id):
	if 'username' in session:
		a=products.query.filter_by(product_id=product_id).first()
		b=User.query.filter_by(customer_username=session['username']).first()
		tr=cart(product_id,b.customer_id,a.product_name,a.product_image)
		db.session.add(tr)
		db.session.commit()
		return redirect('/items_in_cart/'+str(b.customer_id))
	else:
		flash("You need to be logged in first","danger")
		return redirect('/display_product/'+str(product_id))


@app.route('/remove_from_cart/<int:serial_no>')
def remove_from_cart(serial_no):
	a=cart.query.filter_by(serial_no=serial_no).first()
	customer_id=a.customer_id
	cart.query.filter_by(serial_no=serial_no).delete()
	db.session.commit()
	return redirect('/items_in_cart/'+str(customer_id))


@app.route('/display_product/<int:product_id>')
def display_product(product_id):
	a=products.query.filter_by(product_id=product_id).first()
	full='images/'+str(a.product_image)
	tempans=User.query.filter_by(customer_id=a.seller_id).first()
	c=sellers.query.filter_by(seller_id=a.seller_id).first()
	d=User.query.filter_by(customer_id=c.customer_id).first()
	if 'username' in session:
		return render_template('tempprod.html',ans=a,orp=a.product_price*10/9,sans=tempans,full=full,name=d.customer_username,a=products.no_of_raters,nform=SearchForm(),idd=d.customer_id)
	else:
		return render_template('tempprod1.html',ans=a,orp=a.product_price*10/9,sans=tempans,full=full,name=d.customer_username,a=products.no_of_raters,nform=SearchForm(),idd=d.customer_id)

@app.route('/items_in_cart/<int:customer_id>')
def items_in_cart(customer_id):
	a=cart.query.filter_by(customer_id=customer_id).all()
	sum=0
	for prod in a:
		b=prod.product_id
		c=products.query.filter_by(product_id=b).first()
		if c:
			sum=sum+c.product_price
	return render_template('cart.html',items=a,id=customer_id,nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id,sum=sum)

@app.route('/sasa')
def sasa():
	return render_template('new_sel.html',nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)

# @app.route('/contactus',methods=['GET','POST'])
# def contact():
# 	if 'username' in session:
# 		return render_template('contact.html',nform=SearchForm(),idd=User.query.filter_by(customer_username=session['username']).first().customer_id)
# 	else:
# 		return render_template('contact2.html',nform=SearchForm())


@app.route('/buy_all/<int:customer_id>')
def buy_all(customer_id):
	items=cart.query.filter_by(customer_id=customer_id).all()
	for i in items:
		s=products.query.filter_by(product_id=i.product_id).first()
		item=sales(i.product_id,s.seller_id,customer_id)
		db.session.add(item)
		db.session.commit()
		cart.query.filter_by(customer_id=customer_id).delete(synchronize_session='evaluate')
		db.session.commit()
	return redirect('/bought_list/'+str(customer_id))

@app.route('/bought_list/<int:customer_id>')
def bought_list(customer_id):
	a=sales.query.filter_by(customer_id=customer_id).all()
	items=[]
	for i in a:	
		item=products.query.filter_by(product_id=i.product_id).first()
		if item:
			items.append(item)
	return render_template('bought_list.html',items=items,id=customer_id,nform=SearchForm())				


@app.route('/rate/<int:product_id>',methods=['GET','POST'])
def rate(product_id):
	nform=SearchForm()
	a1=User.query.filter_by(customer_username=session['username']).first()
	exists=sales.query.filter_by(product_id=product_id).all()
	b1=sales.query.filter_by(product_id=product_id).first()
	c1=products.query.filter_by(product_id=product_id).first()
	if exists==None:
		flash('You have not bought this item, So U cannot rate this item','danger')
		return redirect('/display_product/'+str(product_id))
	elif not a1.customer_id == b1.customer_id:
		flash('You have not bought this item, So U cannot rate this item','danger')
		return redirect('/display_product/'+str(product_id))
	else:
		if request.method=='POST':
			if not request.form['stars']:

				return render_template('rating.html',flag=1,id=product_id,nform=nform)
			else:
				c1.product_rating=(c1.product_rating*c1.no_of_raters+float(request.form['stars']))*1.0/(c1.no_of_raters+1)
				c1.no_of_raters+=1
				db.session.add(c1)
				db.session.commit()
				return "Thanks for ur feedback"
		return render_template('rating.html',flag=0,id=product_id,nform=nform)




# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user = User(username=form.username.data, email=form.email.data, password=hashed_password)
#         db.session.add(user)
#         db.session.commit()
#         flash('Your account has been created! You are now able to log in', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)


# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             login_user(user, remember=form.remember.data)
#             next_page = request.args.get('next')
#             return redirect(next_page) if next_page else redirect(url_for('dashboard'))
#         else:
#             flash('Login Unsuccessful. Please check email and password', 'danger')
#     return render_template('login.html', title='Login', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



@app.route("/account", methods=['GET', 'POST'])

def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username= form.username.data
        # current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        # form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    print(current_user.username)
    return render_template("dashboard.html", username=current_user.username, logged_in=True)


# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static', filename="files/cheat_sheet.pdf")


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='toedamer03@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)



							#   SELLERS PORTAL  #




# # # Model saved with Keras model.save()
MODEL_PATH_cotton ='Model\cotton_model.h5'

# Load your trained model
model_cotton = load_model(MODEL_PATH_cotton)

def model_predict(img_path, model):
    print(img_path)
    img = tf.keras.utils.load_img(img_path, target_size=(64, 64))

    # Preprocessing the image
    x = tf.keras.utils.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="The leaf is diseased cotton leaf Treatment : Seed treatment is a pre-requisite : Use protectant spray"
    elif preds==1:
        preds="The leaf is diseased cotton plant Treatment : Seed treatment is a pre-requisite : Use protectant spray"
    elif preds==2:
        preds="The leaf is fresh cotton leaf"
    else:
        preds="The leaf is fresh cotton plant"
        
    
    
    return preds

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model_cotton)
        result=preds
        return result
    return None










@app.route('/')
def home():
    return render_template('index.html')








# Model saved with Keras model.save()
MODEL_PATH_tomato ='Model/tomato_model.h5'

# Load your trained model
model_tomato = load_model(MODEL_PATH_tomato)




def model_predict_tomato(img_path, model):
    print(img_path)
    img = tf.keras.utils.load_img(img_path, target_size=(64, 64))

    # Preprocessing the image
    x = tf.keras.utils.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="Bacterial_spot --- Treatment : A plant with bacterial spot cannot be cured. Remove symptomatic plants from the field or greenhouse to prevent the spread of bacteria to healthy plants"
    elif preds==1:
        preds="Early_blight --- Treatment. Tomatoes that have early blight require immediate attention before the disease takes over the plants. Thoroughly spray the plant (bottoms of leaves also) with Bonide Liquid Copper Fungicide concentrate or Bonide Tomato & Vegetable. Both of these treatments are organic."
    elif preds==2:
        preds="Late_blight --- Treatment : Spraying fungicides is the most effective way to prevent late blight. For conventional gardeners and commercial producers, protectant fungicides such as chlorothalonil (e.g., Bravo, Echo, Equus, or Daconil) and Mancozeb (Manzate) can be used"
    elif preds==3:
        preds="Leaf_Mold --- Treatment  : An apple-cider and vinegar mix is believed to treat the mold effectively. Corn and garlic spray can also be used to prevent fungi outbreaks before they even occur"
    elif preds==4:
        preds="Septoria_leaf_spot --- Treatment : You have to use fungicidal sprays. Fungicides will not cure infected leaves, but they will protect new leaves from becoming infected. Apply at 7 to 10 day intervals throughout the season. Apply chlorothalonil, maneb, macozeb, or a copper-based fungicide, such as Bordeaux mixture, copper hydroxide, copper sulfate, or copper oxychloride sulfate. Follow harvest restrictions listed on the pesticide label."
    elif preds==5:
        preds="Spider_mites Two-spotted_spider_mite --- Treatment : Long-lasting insecticides, such as bifenthrin and permethrin can be used on twospotted spider infestations. However, these insecticides also kill natural enemies and could possibly make infestations worse in the long run. Twospotted spider mite infestations occur when it is hot and dry."
    elif preds==6:
        preds="Target_Spot --- treatment : Many fungicides are registered to control of target spot on tomatoes. Growers should consult regional disease management guides for recommended products. Products containing chlorothalonil, mancozeb, and copper oxychloride have been shown to provide good control of target spot in research trials"
    elif preds==7:
        preds="Tomato_Yellow_Leaf_Curl_Virus --- Treatment : Use a neonicotinoid insecticide, such as dinotefuran (Venom) imidacloprid (AdmirePro, Alias, Nuprid, Widow, and others) or thiamethoxam (Platinum), as a soil application or through the drip irrigation system at transplanting of tomatoes or peppers."
    elif preds==8:
        preds="Tomato_mosaic_virus --- Treatment : Destroy any seedlings that appear stunted or distorted and then decontaminate tools and hands. Keep the area around the tomatoes weeded and free of plant detritus to minimize areas the disease can harbor. Control insects as well to lessen the chances of contamination."
    else:
        preds="Healthy"
        
    
    
    return preds

# Model saved with Keras model.save\()
MODEL_PATH_potato ='Model\potato_model.h5'

# Load your trained model
model_potato = load_model(MODEL_PATH_potato)

def model_predict_potato(img_path, model):
    print(img_path)
    img = tf.keras.utils.load_img(img_path, target_size=(64, 64))

    # Preprocessing the image
    x = tf.keras.utils.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="Potato__Early_blight --- Treatment : Treatment of early blight includes prevention by planting potato varieties that are resistant to the disease; late maturing are more resistant than early maturing varieties. Avoid overhead irrigation and allow for sufficient aeration between plants to allow the foliage to dry as quickly as possible."
    elif preds==1:
        preds="Potato__Late_blight --- Treatment : Late blight is controlled by eliminating cull piles and volunteer potatoes, using proper harvesting and storage practices, and applying fungicides when necessary. Air drainage to facilitate the drying of foliage each day is important."
    
    else:
        preds="Potato__healthy"
        
    
    
    return preds



@app.route('/predicttomato', methods=['GET', 'POST'])
def upload2():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict_tomato(file_path, model_tomato)
        result=preds
        return result
    return None

@app.route('/predictpotato', methods=['GET', 'POST'])
def upload3():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict_potato(file_path, model_potato)
        result=preds
        return result
    return None

# Grapes 

# Model saved with Keras model.save()
MODEL_PATH_grape ='Model\grape_model.h5'

# Load your trained model
model_grape = load_model(MODEL_PATH_grape)

def model_predict_grape(img_path, model):
    print(img_path)
    img = tf.keras.utils.load_img(img_path, target_size=(64, 64))

    # Preprocessing the image
    x = tf.keras.utils.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="Grape___Black_rot --- Treatment : The best time to treat black rot of grapes is between bud break until about four weeks after bloom; treating outside of this window is likely to end in frustration. However, if you want to try, captan and myclobutanil are the fungicides of choice. Prevention is key when dealing with grape black rot."
    elif preds==1:
        preds="Grape___Esca_(Black_Measles) --- Treatment : A preventive/curative treatment of grapevine towards fungal induced esca is proposed. A mixture of antimicrobial molecules inhibit mycelial growth and spore germination. The efficiency of the treatment can be monitored by an immunological assay"
    elif preds==2:
        preds="Grape___Leaf_blight_(Isariopsis_Leaf_Spot) --- Treatment :  Apply dormant sprays to reduce inoculum levels"
    
    else:
        preds="Grape___healthy"
        
    
    
    return preds

@app.route('/predictgrape', methods=['GET', 'POST'])
def upload4():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict_grape(file_path, model_grape)
        result=preds
        return result
    return None

# Wheat 

# Model saved with Keras model.save()
MODEL_PATH_wheat ='Model\wheat_model.h5'

# Load your trained model
model_wheat = load_model(MODEL_PATH_wheat)

def model_predict_wheat(img_path, model):
    print(img_path)
    img = tf.keras.utils.load_img(img_path, target_size=(64, 64))

    # Preprocessing the image
    x = tf.keras.utils.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="Healthy"
    elif preds==1:
        preds="septoria --- Treatment : Fungicides are required for effective septoria tritici control in most crops. However, to reduce reliance on fungicides and the risk of fungicide resistance developing, all other cultural control methods should first be adopted to reduce the level of input required."
    
    
    else:
        preds="stripe_rust --- Treatment : Treating seed or fertilizer with fungicide for early-sown winter wheats to prevent autumn build up of stripe rust. Treating seed or fertilizer with fungicide to delay the onset of stripe rust in susceptible to moderately resistant wheats, or early spraying to control infections in autumn or early winter."
        
    
    
    return preds
    
    return preds

@app.route('/predictwheat', methods=['GET', 'POST'])
def upload5():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict_wheat(file_path, model_wheat)
        result=preds
        return result
    return None

# rice 

# Model saved with Keras model.save()
MODEL_PATH_rice ='Model/rice_model.h5'

# Load your trained model
model_rice = load_model(MODEL_PATH_rice)

def model_predict_rice(img_path, model):
    print(img_path)
    img = tf.keras.utils.load_img(img_path, target_size=(64, 64))

    # Preprocessing the image
    x = tf.keras.utils.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="leaf_blight Treatment : Terramycin 17, Brestanol, Agrimycin 500 and a combination of Agrimycin 100 + Fytolan gave effective control of the blight phase of the disease. The combination of Agrimycin 100 + Fytolan spraying gave good control of the disease and an economic return on susceptible varieties like Sona."
    elif preds==1:
        preds="brown_spot Treatment : Seed treatment with tricyclazole followed by spraying of mancozeb + tricyclazole at tillering and late booting stages gave good control of the disease"
    elif preds==2:
        preds="Healthy" 
    elif preds==3:
        preds="leaf_blast Treatment : Systemic fungicides like triazoles and strobilurins can be used judiciously for control to leaf blast. A fungicide application at heading can be effective in controlling the disease in cases where the risk of yield losses is high."
    elif preds==4:
        preds="leaf_scald Treatment : Use benomyl, carbendazim, quitozene, and thiophanate-methyl to treat seeds. In the field, spraying of benomyl, fentin acetate, edifenphos, and validamycin significantly reduce the incidence of leaf scald."
    else:
        preds="narrow_brown_spot Treatment : Remove weeds and weedy rice in the field and nearby areas to remove alternate hosts that allow the fungus to survive and infect new rice crops. Use balanced nutrients; make sure that adequate potassium is used. If narrow brown spot poses a risk to the field, spray propiconazole at booting to heading stages."
    

    
    return preds

@app.route('/predictrice', methods=['GET', 'POST'])
def upload6():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict_rice(file_path, model_rice)
        result=preds
        return result
    return None

# corn 

# Model saved with Keras model.save()
MODEL_PATH_corn ='Model\corn_model.h5'

# Load your trained model
model_corn = load_model(MODEL_PATH_corn)

def model_predict_corn(img_path, model):
    print(img_path)
    img = tf.keras.utils.load_img(img_path, target_size=(64, 64))

    # Preprocessing the image
    x = tf.keras.utils.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="Blight--- Treatment : Treating northern corn leaf blight involves using fungicides. For most home gardeners this step isn't needed, but if you have a bad infection, you may want to try this chemical treatment. The infection usually begins around the time of silking, and this is when the fungicide should be applied."
    elif preds==1:
        preds="Common_Rust --- Treatment : To reduce the incidence of corn rust, plant only corn that has resistance to the fungus. Resistance is either in the form of race-specific resistance or partial rust resistance. In either case, no sweet corn is completely resistant. If the corn begins to show symptoms of infection, immediately spray with a fungicide."
    elif preds==2:
        preds="Gray_Leaf_Spot --- Treatment : Disease management tactics include using resistant corn hybrids, conventional tillage where appropriate, and crop rotation. Foliar fungicides can be effective if economically warranted."
    
    elif preds==2:
        preds=""
    else :
        preds="Healthy"
    
    
    return preds

@app.route('/predictcorn', methods=['GET', 'POST'])
def upload7():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict_corn(file_path, model_corn)
        result=preds
        return result
    return None

# apple

# Model saved with Keras model.save()
MODEL_PATH_apple ='Model/apple_model.h5'

# Load your trained model
model_apple = load_model(MODEL_PATH_apple)

def model_predict_apple(img_path, model):
    print(img_path)
    img = tf.keras.utils.load_img(img_path, target_size=(64, 64))

    # Preprocessing the image
    x = tf.keras.utils.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="Apple_Scab --- : Myclobutanil (Spectracide Immunox Multipurpose Fungicide Spray Concentrate) is a synthetic fungicide that is effective against apple scab. You can apply it any time from green tip until after petal fall."
        
    
    elif preds==1:
        preds="Healthy"
    else:
        preds="Wrong Input"
    
    return preds

@app.route('/predictapple', methods=['GET', 'POST'])
def upload8():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict_apple(file_path, model_apple)
        result=preds
        return result
    return None

# cucumber

# Model saved with Keras model.save()
MODEL_PATH_cucumber ='Model\cucumber_model.h5'

# Load your trained model
model_cucumber = load_model(MODEL_PATH_cucumber)

def model_predict_cucumber(img_path, model):
    print(img_path)
    img = tf.keras.utils.load_img(img_path, target_size=(64, 64))

    # Preprocessing the image
    x = tf.keras.utils.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
   # x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="Downy --- mildew Treatment : Fungicide chlorothalonil or mancozeb1 or copper fungicide4"
    
    else:
        preds="good_Cucumber"
        
    
    
    return preds

@app.route('/predictcucumber', methods=['GET', 'POST'])
def upload9():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict_cucumber(file_path, model_cucumber)
        result=preds
        return result
    return None

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/index')
def home2():
    return render_template('index.html')

@app.route('/how_we_work')
def how_we_work():
    return render_template('how_we_work.html')



@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/cotton_index_crop')
def cotton_index_crop():
    return render_template('cotton_index_crop.html')

@app.route('/tomato_index_crop')
def tomato_index_crop():
    return render_template('tomato_index_crop.html')

@app.route('/potato_index_crop')
def potato_index_crop():
    return render_template('potato_index_crop.html')

@app.route('/apple_index_crop')
def apple_index_crop():
    return render_template('apple_index_crop.html')

@app.route('/cucumber_index_crop')
def cucumber_index_crop():
    return render_template('cucumber_index_crop.html')

@app.route('/rice_index_crop')
def rice_index_crop():
    return render_template('rice_index_crop.html')

@app.route('/grape_index_crop')
def grape_index_crop():
    return render_template('grape_index_crop.html')

@app.route('/wheat_index_crop')
def wheat_index_crop():
    return render_template('wheat_index_crop.html')

@app.route('/corn_index_crop')
def corn_index_crop():
    return render_template('corn_index_crop.html')

if __name__ == "__main__":
    app.run(port=8000,debug=True)