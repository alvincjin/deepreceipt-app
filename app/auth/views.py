from flask import render_template, redirect, request, url_for, flash, g
from . import auth
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm, SignupForm
from ..models import User
from app import db
from app.emails import send_emails


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('.user', nickname = g.user.nickname))

    if request.method == 'POST':
        if form.validate() is False:
            return render_template('auth/register.html', form=form)
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
            %sauth/user_activation/%s/
            Thank you.
            DeepFit Inc.
            ''' % (request.url_root, user.get_id())

            send_emails(subject, msg, user.email)
            flash('Registration was successful. '
                  'Please click the activation link sent to your email to activate your account.')
            return redirect(url_for('auth.login'))

    elif request.method == 'GET':
        return render_template('auth/register.html', form=form)


@auth.route('/user_activation/<key>/')
def activate_user(key):
    user = User.query.get(key)
    if user.active is True:
        flash('The account for this link has already been activated.')
        return redirect(url_for('.login'))
    user.active = True
    db.session.add(user)
    db.session.commit()
    flash('Your account has been activated. You may now login.')
    return redirect(url_for('.login'))
