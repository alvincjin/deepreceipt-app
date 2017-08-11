import os
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid, admin
from forms import *
from app.models import User, ROLE_USER, ROLE_ADMIN, Post, Preference, Favourite
from datetime import datetime
from app.emails import follower_notification, send_emails
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS
from werkzeug.utils import secure_filename
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from pygeocoder import Geocoder
import os.path as op
from config import ADMINS


# file upload setting
UPLOAD_AGENT_FOLDER = 'app/static/agent_photo'
UPLOAD_HOUSE_FOLDER = 'app/static/house_photo'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_AGENT_FOLDER'] = UPLOAD_AGENT_FOLDER
app.config['UPLOAD_HOUSE_FOLDER'] = UPLOAD_HOUSE_FOLDER

# admin management setup
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
path = op.join(op.dirname(__file__), 'static')
admin.add_view(FileAdmin(path, '/static/', name='Static Files'))


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/list_post', methods = ['GET', 'POST'])
@app.route('/list_post/<int:page>', methods = ['GET', 'POST'])
@login_required
def list_post(page = 1):
    
    form = PeferForm()
    user = g.user
        
    posts = Post.query.filter( Post.id == Post.id).order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)

    if form.validate_on_submit() and user.role==0:
        
        pref = Preference(style = form.style.data, bedroom_no = form.bedroom_no.data,
                          bathroom_no = form.bathroom_no.data, garage_no = form.garage_no.data,
                          location = form.location.data, price = form.price.data)

        results = Post.query.filter( Post.style == pref.style).filter(Post.location== pref.location)\
            .filter(Post.price >= 0.8 * float(pref.price)).filter(Post.price <= 1.2 * float(pref.price))\
            .filter(Post.bedroom_no >= pref.bedroom_no-1).filter(Post.bedroom_no <= pref.bedroom_no+1)\
            .order_by(Post.timestamp.desc())
        
        posts = results.paginate(page, POSTS_PER_PAGE, False)
        flash('Find '+str(results.count())+' matching results')
 
    return render_template('list_post.html',
        title = 'All the Houses',
        posts = posts, form = form)


@app.route('/list_agent', methods=['GET', 'POST'])
@app.route('/list_agent/<int:page>', methods=['GET', 'POST'])
def list_agent(page = 1):
    users = User.query.filter(User.role == 1).paginate(page, POSTS_PER_PAGE, False)
    
    return render_template('list_agent.html',
        title='All the Agents',
        users=users)


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        g.user.phone = form.phone.data

        file = form.fileName.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_AGENT_FOLDER'], filename))
            file_path = os.path.join('/static/agent_photo/', filename)
            # only when file is not none, change it, otherwise keep the previous one
            g.user.portrait = file_path

        if g.user.portrait is None:
            g.user.portrait = '/static/agent_photo/agent_default.gif'

        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', nickname=g.user.nickname))

    elif request.method != "POST":
        form = EditForm(g.user.nickname, obj=g.user)
        
    return render_template('edit_profile.html', form=form)


@app.route('/preference', methods=['GET', 'POST'])
@login_required
def preference():

    form = PeferForm()
    user = g.user
    if form.validate_on_submit() and user.role==0:
        
        pref = Preference.query.filter_by(user_id=user.id).first()
        if pref is None:
            pref = Preference(style = form.style.data, bedroom_no = form.bedroom_no.data,
                              bathroom_no=form.bathroom_no.data, garage_no=form.garage_no.data,
                              location = form.location.data, price=form.price.data, user_id=user.id,
                              notify=form.notify.data)
        else:
            pref.style = form.style.data
            pref.bedroom_no = form.bedroom_no.data
            pref.bathroom_no=form.bathroom_no.data
            pref.garage_no=form.garage_no.data
            pref.location = form.location.data
            pref.price = form.price.data
            pref.notify = form.notify.data

        db.session.add(pref)
        db.session.commit()
        flash('Your preference is set! ')
        return redirect(url_for('user', nickname = user.nickname))
    elif request.method != "POST" and user.pref is not None:
       form = PeferForm(obj=user.pref)
       
    return render_template('preference.html',
        form = form)


def map_address(address):
    results = Geocoder.geocode(address)
    return str(results[0].coordinates).strip('()')


@app.route('/edit_post/', methods = ['GET', 'POST'])
@app.route('/edit_post/<int:pid>', methods = ['GET', 'POST'])
@login_required
def edit_post(pid=0):

    form = PostForm()
    user = g.user      
    post = Post.query.filter_by(id = pid).first()

    if form.validate_on_submit() and user.role:
        
        if post is None:
            post = Post(title = form.title.data, body = form.body.data,
                        timestamp = datetime.utcnow(), user_id = user.id)
        else:
            post.title = form.title.data
            post.body = form.body.data
            post.timestamp = datetime.utcnow()
            post.user_id = user.id

        file = form.fileName.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_HOUSE_FOLDER'], filename))
            file_path = os.path.join('/static/house_photo/', filename)
            post.img = file_path # change only when a new img is given

        if post.img is None:
            post.img = '/static/house_photo/house_default.jpeg'

        post.location = form.location.data
        post.price = form.price.data
        post.style = form.style.data
        post.bedroom_no = form.bedroom_no.data
        post.bathroom_no = form.bathroom_no.data
        post.garage_no = form.garage_no.data
        post.address = form.address.data
        post.coordinate = map_address(post.address + " " + post.location)

        db.session.add(post)
        db.session.commit()
        flash("Your post is alive now")
        return redirect(url_for('user', nickname = g.user.nickname))

    elif request.method != "POST":
        form = PostForm(obj=post)

    return render_template('new_post.html', form=form)


@app.route('/bookmark/<int:pid>', methods = ['GET', 'POST'])
@login_required
def bookmark(pid):

    user = g.user 
    if Favourite.query.filter_by(id = str(user.id)+':'+str(pid)).first():
        flash('The post was already in your collection.')
    else:
        fav = Favourite(user.id, pid)
        db.session.add(fav)
        db.session.commit()
        flash('The post was added in your collection.')       
    
    return redirect(url_for('list_post'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
 
    if request.method == 'POST':
        if form.validate() is False:
            flash('All fields are required.')
            return render_template('contact.html', form=form)
        else:
            text_body = """
            From: %s < %s >
            %s """ % (form.name.data, form.email.data, form.message.data)
            send_emails(form.subject.data, text_body, ADMINS[0])
            return render_template('contact.html', success=True)
 
    elif request.method == 'GET':
        return render_template('contact.html', form=form)


@app.route('/home/<int:pid>')
@login_required
def home(pid):
    post = Post.query.get(pid)
    return render_template("home.html", post=post)


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page = 1):

    user = User.query.filter_by(nickname = nickname).first()
    if user is None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('signin'))
    if user.role == 1:
        posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    else:
        favs = user.fav.all()
        idlist = []
        for fav in favs:
            idlist.append(fav.post_id)
        posts = Post.query.filter(Post.id.in_(idlist)).paginate(page, POSTS_PER_PAGE, False)
        
    return render_template('user.html', user = user, posts = posts)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('user', nickname = g.user.nickname))
    
    if request.method == 'POST':
        if form.validate() is False:
            return render_template('signup.html', form=form)
        else:  
            nickname = form.email.data.split('@')[0]
            nickname = User.make_unique_nickname(nickname)
            
            if form.user_role.data == 'agent':
               role = 1
            else:
               role = 0

            user = User(nickname, form.firstname.data, form.lastname.data,
                        form.email.data, form.password.data, role)
            user.role = role
            
            db.session.add(user)
            db.session.commit()
            #send activation email
             
            subject = 'Confirmation of registration to %s' % request.url_root
            msg = '''
            This email serves to confirm that you are the owner of this email address.
            Please click the following activation link to confirm:
            %suser_activation/%s/
            Thank you.
            Big Face Inc.
            ''' % (request.url_root,user.get_id())

            send_emails(subject, msg, user.email)
            flash('Registration was successful. '
                  'Please click the activation link sent to your email to activate your account.')
            return redirect(url_for('signin'))

    elif request.method == 'GET':
        return render_template('signup.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
        
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('user', nickname = g.user.nickname))
    form = SigninForm()
   
    if request.method == 'POST':
        if form.validate() is False:
            return render_template('signin.html', form=form)
        else:
            g.user = User.query.filter_by(email = form.email.data.lower()).first()
            remember_me = form.remember_me.data
            login_user(g.user, remember = remember_me)
            
            if g.user.active is False:
                flash(' Your account has not been activated yet. '
                      'To do this,please click on the activation link on the email we sent to you.')
                return render_template('signin.html', form=form)
        return redirect(request.args.get('next') or url_for('user', nickname = g.user.nickname))
                        
    elif request.method == 'GET':
        return render_template('signin.html', form=form) 


@app.route('/signout')
def signout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post is None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('You cannot delete this post.')
        return redirect(url_for('list_post'))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('list_post'))
    

@app.route('/user_activation/<key>/')
def activate_user(key):
    user = User.query.get(key)
    if user.active is True:
        flash('The account for this link has already been activated.')
        return redirect(url_for('signin'))
    user.active = True
    db.session.add(user)
    db.session.commit()
    flash('Your account has been activated. You may now login.')
    return redirect(url_for('signin'))


class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False