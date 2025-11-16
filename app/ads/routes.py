from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from app.ads import ads_bp
from app.ads.forms import AdForm, CATEGORIES
from app.models import Ad, User
from app.utils.gridfs_utils import save_file, get_file, delete_file
from app.utils.decorators import owner_or_admin_required
import markdown
import bleach

ALLOWED_TAGS = ['p','br','strong','em','u','h1','h2','h3','h4','h5','h6','ul','ol','li','a','blockquote','code','pre']
ALLOWED_ATTRIBUTES = {'a': ['href','title'], 'code': ['class']}

@ads_bp.route('/')
def list_ads():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    ad_type = request.args.get('type', None)
    search = request.args.get('search', None)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
    ads, total = Ad.get_all(category=category, search=search, ad_type=ad_type, page=page, per_page=per_page)
    return render_template('ads/list.html', ads=ads, total=total, page=page, category=category, search=search, ad_type=ad_type, categories=CATEGORIES)

@ads_bp.route('/<ad_id>')
def view_ad(ad_id):
    ad = Ad.get_by_id(ad_id)
    if not ad:
        abort(404)
    description_html = markdown.markdown(ad.description)
    description_html = bleach.clean(description_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    seller = User.get_by_id(ad.user_id)
    return render_template('ads/detail.html', ad=ad, description_html=description_html, seller=seller)

@ads_bp.route('/create', methods=['GET','POST'])
@login_required
def create_ad():
    form = AdForm()
    if form.validate_on_submit():
        image_id = None
        if form.image.data:
            image_id = save_file(form.image.data, form.image.data.filename)
        seller_name = f"{current_user.first_name} {current_user.last_name}".strip() or current_user.username
        price_val = None
        if form.price.data:
            try:
                price_val = float(form.price.data)
            except:
                price_val = None
        ad = Ad(title=form.title.data, description=form.description.data, price=price_val,
                category=form.category.data, location=form.location.data or '',
                user_id=current_user.id, seller_name=seller_name, seller_phone=current_user.phone or '',
                image_id=image_id, ad_type=form.ad_type.data)
        ad.save()
        flash('Oglas uspješno kreiran!', 'success')
        return redirect(url_for('ads.view_ad', ad_id=ad.id))
    return render_template('ads/create.html', form=form)

@ads_bp.route('/<ad_id>/edit', methods=['GET','POST'])
@login_required
@owner_or_admin_required(Ad, 'ad_id')
def edit_ad(ad_id):
    ad = Ad.get_by_id(ad_id)
    if not ad:
        abort(404)
    form = AdForm(obj=ad)
    form.ad_type.data = ad.ad_type
    form.price.data = ad.price
    if form.validate_on_submit():
        if form.image.data:
            if ad.image_id:
                delete_file(ad.image_id)
            ad.image_id = save_file(form.image.data, form.image.data.filename)
        ad.title = form.title.data
        ad.description = form.description.data
        try:
            ad.price = float(form.price.data) if form.price.data is not None else None
        except:
            ad.price = None
        ad.category = form.category.data
        ad.location = form.location.data or ''
        ad.ad_type = form.ad_type.data
        ad.save()
        flash('Oglas uspješno ažuriran!', 'success')
        return redirect(url_for('ads.view_ad', ad_id=ad.id))
    return render_template('ads/edit.html', form=form, ad=ad)

@ads_bp.route('/<ad_id>/delete', methods=['POST'])
@login_required
@owner_or_admin_required(Ad, 'ad_id')
def delete_ad(ad_id):
    ad = Ad.get_by_id(ad_id)
    if not ad:
        abort(404)
    ad.delete()
    flash('Oglas uspješno obrisan!', 'success')
    return redirect(url_for('ads.my_ads'))

@ads_bp.route('/my')
@login_required
def my_ads():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    ad_type = request.args.get('type', None)
    search = request.args.get('search', None)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
    ads, total = Ad.get_by_user(current_user.id, category=category, search=search, ad_type=ad_type, page=page, per_page=per_page)
    return render_template('ads/my_ads.html', ads=ads, total=total, page=page, category=category, ad_type=ad_type, search=search, categories=CATEGORIES)

@ads_bp.route('/image/<image_id>')
def serve_image(image_id):
    from flask import Response
    file = get_file(image_id)
    if not file:
        abort(404)
    return Response(file.read(), mimetype=file.content_type)
