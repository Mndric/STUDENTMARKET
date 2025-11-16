from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.admin.forms import UserCreateForm, UserEditForm
from app.models import User
from app.utils.decorators import admin_required

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/new', methods=['GET','POST'])
@login_required
@admin_required
def create_user():
    form = UserCreateForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password_hash='', role=form.role.data, email_verified=form.email_verified.data)
        user.set_password(form.password.data)
        user.save()
        flash(f'Korisnik {user.username} uspješno kreiran!', 'success')
        return redirect(url_for('admin.list_users'))
    return render_template('admin/user_create.html', form=form)

@admin_bp.route('/users/<user_id>/edit', methods=['GET','POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        abort(404)
    form = UserEditForm()
    if form.validate_on_submit():
        if form.username.data != user.username:
            existing = User.get_by_username(form.username.data)
            if existing:
                flash('Korisničko ime već postoji.', 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
        if form.email.data != user.email:
            existing = User.get_by_email(form.email.data)
            if existing:
                flash('Email već postoji.', 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.email_verified = form.email_verified.data
        if form.password.data:
            user.set_password(form.password.data)
        user.save()
        flash(f'Korisnik {user.username} uspješno ažuriran!', 'success')
        return redirect(url_for('admin.list_users'))
    form.username.data = user.username
    form.email.data = user.email
    form.role.data = user.role
    form.email_verified.data = user.email_verified
    return render_template('admin/user_edit.html', form=form, user=user)

@admin_bp.route('/users/<user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('Ne možete obrisati samog sebe!', 'danger')
        return redirect(url_for('admin.list_users'))
    user = User.get_by_id(user_id)
    if not user:
        abort(404)
    username = user.username
    user.delete()
    flash(f'Korisnik {username} uspješno obrisan!', 'success')
    return redirect(url_for('admin.list_users'))
