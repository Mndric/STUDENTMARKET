from flask import render_template, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from app.profile import profile_bp
from app.profile.forms import ProfileForm
from app.utils.gridfs_utils import save_file, get_file, delete_file
from app.models import User

@profile_bp.route('/')
@login_required
def view_profile():
    return render_template('profile/view.html', user=current_user)

@profile_bp.route('/edit', methods=['GET','POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.profile_image.data:
            if current_user.profile_image_id:
                delete_file(current_user.profile_image_id)
            current_user.profile_image_id = save_file(form.profile_image.data, form.profile_image.data.filename)
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.save()
        flash('Profil uspješno ažuriran!', 'success')
        return redirect(url_for('profile.view_profile'))
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.phone.data = current_user.phone
    return render_template('profile/edit.html', form=form)

@profile_bp.route('/image/<user_id>')
def serve_profile_image(user_id):
    user = User.get_by_id(user_id)
    if not user or not user.profile_image_id:
        abort(404)
    file = get_file(user.profile_image_id)
    if not file:
        abort(404)
    return Response(file.read(), mimetype=file.content_type)
