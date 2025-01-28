from flask import Flask, render_template, request, flash, redirect, url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime


# Configurations
local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)['params']
  
app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Mail Configuration
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']
)
mail = Mail(app) 



app.config['UPLOAD_FOLDER']=params['upload_location']

# Database Configuration
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

# Database Model
class Contact(db.Model):
    __tablename__ = 'contact'
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    mes = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(50), nullable=True)

class Post(db.Model):
    __tablename__ = 'post'
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(5), nullable=False)
    tagline = db.Column(db.String(5), nullable=False)
    date = db.Column(db.String(50), nullable=True)
    img_file = db.Column(db.String(50), nullable=True)

# Routes
@app.route("/")
def home():
    post=Post.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params=params , post=post)





@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
  print(session)
  if ('user' in session and session['user']==params['admin_user']):
    
    post= Post.query.all()
    print(post)

    sess = {
        'username': params['admin_user']
    }
          
    return render_template('dashboard.html', params=params, post=post, session=sess)
   
  if request.method=='POST':
      username=request.form.get('uname')
      userpass=request.form.get('pass')
      print(username)
      print(params['admin_user'])
      print(userpass)
      print(params['admin_password'])
      if (username==params['admin_user'] and userpass==params['admin_password']):
          session['user']=username  
          post= Post.query.all()
          print(post)

          sess = {
              username: username
          }
          
          return render_template('dashboard.html',params=params, post=post,session=sess )
      else: 
            
            post= Post.query.all()
            print(post)
            return render_template('dashboard.html', params=params, post=post)

     #to admin panel   
    
  else:
   

    return render_template('login.html', params=params , method=['GET','POST'])








@app.route("/about")
def about():
    return render_template('about.html', params=params)



@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    print(session)
    if 'user' in session and session['user'] == params['admin_user']:
        print("User is authenticated.")  # Debug log

        if request.method == 'POST':
            print("POST request received.")  # Debug log
            box_title = request.form.get('title') or "test"
            slug = request.form.get('slug') or "test"
            content = request.form.get('content') or "test"
            tagline = request.form.get('tagline') or "test"
            img_file = request.form.get('img_file') or "test"
            date = datetime.now().strftime("%Y-%m-%d")

            print(f"Form data: title={box_title}, slug={slug}, content={content}, tagline={tagline}, img_file={img_file}")

            if sno == '0':
                print("Creating a new post.")  # Debug log
                new_post = Post(title=box_title, slug=slug, content=content, tagline=tagline, img_file=img_file, date=date)
                db.session.add(new_post)
                db.session.commit()
                print("New post added to the database.")
            else:
                print(f"Updating post with sno={sno}.")  # Debug log
                post = Post.query.filter_by(sno=sno).first()
                print(post)
                if post:
                    post.title = box_title
                    post.slug = slug
                    post.content = content
                    post.tagline = tagline
                    post.img_file = img_file
                    post.date = date
                    db.session.commit()
                    print("Post updated in the database.")
                else:
                    print("Post not found for updating.")
        else:
            print("GET request received.")  # Debug log

        post = Post.query.filter_by(sno=sno).first() if sno != '0' else None
        return render_template('edit.html', params=params, post=post, sno=sno)
    else:
        print("User not authenticated.")
        print(sno)
        post = Post.query.filter_by(sno=sno).first()
        print(post)
        return render_template('edit.html', params=params, post=post, sno=sno)
       

    
   


@app.route("/post/<string:post_slug>" , methods=['GET'])
def post_route(post_slug):
    post=Post.query.filter_by(slug=post_slug).first()

    return render_template('post.html', params=params , post=post)


@app.route("/uploader" , methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user']==params['admin_user']):
        if request.method==['POST']:
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully"
        
    else:
        print("nope")    
   
  



@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Retrieve form data from HTML
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        try:
            # Create a new contact instance
            new_contact = Contact(
                name=name,
                email=email,
                phone=phone,
                mes=message,
                date=datetime.now().strftime("%Y-%m-%d")
            )

            # Debug: print new contact data
            print("Attempting to add new contact:", vars(new_contact))

            # Add and commit to the database
            db.session.add(new_contact)
            db.session.commit()

            # Send Email
            msg = Message(
                f'New message from {name}',
                sender=email,
                recipients=[params['gmail_user']],
                body=f"Message: {message}\nPhone: {phone}"
            )
            mail.send(msg)

            flash('Message sent successfully!', 'success')
            return redirect(url_for('contact'))

        except Exception as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('contact'))

    return render_template('contact.html', params=params)

# Run the Application
if __name__ == "__main__":
    app.run(debug=True, port=5001)


