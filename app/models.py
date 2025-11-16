from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from bson.objectid import ObjectId
from datetime import datetime

class User(UserMixin):
    def __init__(self, username, email, password_hash, role='user',
                 email_verified=False, first_name='', last_name='',
                 phone='', profile_image_id=None, _id=None):
        self.id = str(_id) if _id else None
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.email_verified = email_verified
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.profile_image_id = profile_image_id
        self.created_at = datetime.utcnow()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'email_verified': self.email_verified,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'profile_image_id': self.profile_image_id,
            'created_at': self.created_at
        }

    def save(self):
        data = self.to_dict()
        if self.id:
            mongo.db.users.update_one({'_id': ObjectId(self.id)}, {'$set': data})
        else:
            res = mongo.db.users.insert_one(data)
            self.id = str(res.inserted_id)
        return self.id

    @staticmethod
    def get_by_id(user_id):
        try:
            data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if data:
                return User(
                    username=data['username'],
                    email=data['email'],
                    password_hash=data['password_hash'],
                    role=data.get('role', 'user'),
                    email_verified=data.get('email_verified', False),
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    phone=data.get('phone', ''),
                    profile_image_id=data.get('profile_image_id'),
                    _id=data['_id']
                )
        except:
            return None

    @staticmethod
    def get_by_username(username):
        data = mongo.db.users.find_one({'username': username})
        if data:
            return User(
                username=data['username'],
                email=data['email'],
                password_hash=data['password_hash'],
                role=data.get('role', 'user'),
                email_verified=data.get('email_verified', False),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone=data.get('phone', ''),
                profile_image_id=data.get('profile_image_id'),
                _id=data['_id']
            )
        return None

    @staticmethod
    def get_by_email(email):
        data = mongo.db.users.find_one({'email': email})
        if data:
            return User(
                username=data['username'],
                email=data['email'],
                password_hash=data['password_hash'],
                role=data.get('role', 'user'),
                email_verified=data.get('email_verified', False),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone=data.get('phone', ''),
                profile_image_id=data.get('profile_image_id'),
                _id=data['_id']
            )
        return None

    @staticmethod
    def get_all():
        users = []
        for data in mongo.db.users.find():
            users.append(User(
                username=data['username'],
                email=data['email'],
                password_hash=data['password_hash'],
                role=data.get('role', 'user'),
                email_verified=data.get('email_verified', False),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone=data.get('phone', ''),
                profile_image_id=data.get('profile_image_id'),
                _id=data['_id']
            ))
        return users

    @staticmethod
    def create_admin(username, email, password_hash):
        admin = User(username=username, email=email, password_hash=password_hash, role='admin', email_verified=True)
        return admin.save()

    def delete(self):
        if not self.id:
            return False
        if self.profile_image_id:
            from app.utils.gridfs_utils import delete_file
            delete_file(self.profile_image_id)
        from app.models import Ad
        for ad_data in mongo.db.ads.find({'user_id': self.id}):
            ad = Ad.from_dict(ad_data)
            ad.delete()
        mongo.db.users.delete_one({'_id': ObjectId(self.id)})
        return True

class Ad:
    def __init__(self, title, description, price, category, location,
                 user_id, seller_name='', seller_phone='',
                 image_id=None, ad_type='prodaja', _id=None, created_at=None):
        self.id = str(_id) if _id else None
        self.title = title
        self.description = description
        self.price = price
        self.category = category
        self.location = location
        self.user_id = user_id
        self.seller_name = seller_name
        self.seller_phone = seller_phone
        self.image_id = image_id
        self.ad_type = ad_type
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'location': self.location,
            'user_id': self.user_id,
            'seller_name': self.seller_name,
            'seller_phone': self.seller_phone,
            'image_id': self.image_id,
            'ad_type': self.ad_type,
            'created_at': self.created_at
        }

    def save(self):
        data = self.to_dict()
        if self.id:
            mongo.db.ads.update_one({'_id': ObjectId(self.id)}, {'$set': data})
        else:
            res = mongo.db.ads.insert_one(data)
            self.id = str(res.inserted_id)
        return self.id

    @staticmethod
    def from_dict(ad_data):
        return Ad(
            title=ad_data.get('title'),
            description=ad_data.get('description'),
            price=ad_data.get('price'),
            category=ad_data.get('category'),
            location=ad_data.get('location', ''),
            user_id=ad_data.get('user_id'),
            seller_name=ad_data.get('seller_name', ''),
            seller_phone=ad_data.get('seller_phone', ''),
            image_id=ad_data.get('image_id'),
            ad_type=ad_data.get('ad_type', 'prodaja'),
            _id=ad_data.get('_id'),
            created_at=ad_data.get('created_at')
        )

    @staticmethod
    def get_by_id(ad_id):
        try:
            data = mongo.db.ads.find_one({'_id': ObjectId(ad_id)})
            if data:
                return Ad.from_dict(data)
        except:
            return None

    @staticmethod
    def get_all(category=None, search=None, ad_type=None, page=1, per_page=10):
        query = {}
        if category:
            query['category'] = category
        if ad_type:
            query['ad_type'] = ad_type
        if search:
            query['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        total = mongo.db.ads.count_documents(query)
        cursor = mongo.db.ads.find(query).sort('created_at', -1).skip((page - 1) * per_page).limit(per_page)
        ads = [Ad.from_dict(a) for a in cursor]
        return ads, total

    @staticmethod
    def get_by_user(user_id, category=None, search=None, ad_type=None, page=1, per_page=10):
        query = {'user_id': user_id}
        if category:
            query['category'] = category
        if ad_type:
            query['ad_type'] = ad_type
        if search:
            query['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        total = mongo.db.ads.count_documents(query)
        cursor = mongo.db.ads.find(query).sort('created_at', -1).skip((page - 1) * per_page).limit(per_page)
        ads = [Ad.from_dict(a) for a in cursor]
        return ads, total

    def delete(self):
        if not self.id:
            return False
        if self.image_id:
            from app.utils.gridfs_utils import delete_file
            delete_file(self.image_id)
        mongo.db.ads.delete_one({'_id': ObjectId(self.id)})
        return True
