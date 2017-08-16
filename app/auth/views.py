from flask import render_template, redirect, request, url_for, flash, g
from . import auth
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, SignupForm
from ..models import User
from app import db
from app.emails import send_email

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect('main.index')
    return render_template('auth/unconfirmed.html')


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

            if form.user_role.data == 'applicant':
                role = 'Applicant'
            elif form.user_role.data == 'adviser':
                role = 'Adviser'

            user = User(nickname, form.firstname.data, form.lastname.data,
                        form.email.data, form.password.data, role)
            user.role = role

            db.session.add(user)
            db.session.commit()
            #send activation email
            token = user.generate_confirmation_token()

            send_email(user.email, 'Confirm Your Account',
                       'auth/confirm', user=user, token=token)
            flash('Registration was successful.'
                  'Please click the activation link sent to your email to activate your account.')
            return redirect(url_for('auth.login'))

    elif request.method == 'GET':
        return render_template('auth/register.html', form=form)




@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

'auth/confirm',
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))