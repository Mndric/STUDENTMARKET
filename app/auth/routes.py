from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed
from werkzeug.urls import url_parse
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm
from app.models import User
from app.utils.email import send_verification_email, verify_token
from app import limiter

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password_hash='', role='user', email_verified=False)
        user.set_password(form.password.data)
        user.save()
        send_verification_email(user)
        flash('Registracija uspješna! Provjerite email za verifikaciju.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user is None or not user.check_password(form.password.data):
            flash('Neispravno korisničko ime ili lozinka.', 'danger')
            return redirect(url_for('auth.login'))
        if not user.email_verified:
            flash('Molimo potvrdite email adresu prije prijave.', 'warning')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember.data)
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash(f'Dobrodošli, {user.username}!', 'success')
        return redirect(next_page)
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    flash('Uspješno ste se odjavili.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/verify/<token>')
def verify_email(token):
    email = verify_token(token)
    if not email:
        flash('Link za verifikaciju je nevažeći ili je istekao.', 'danger')
        return redirect(url_for('main.index'))
    user = User.get_by_email(email)
    if not user:
        flash('Korisnik ne postoji.', 'danger')
        return redirect(url_for('main.index'))
    if user.email_verified:
        flash('Email je već verificiran.', 'info')
        return redirect(url_for('auth.login'))
    user.email_verified = True
    user.save()
    flash('Email uspješno verificiran! Možete se prijaviti.', 'success')
    return redirect(url_for('auth.login'))
