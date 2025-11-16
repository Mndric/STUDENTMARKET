from app import mongo
from bson.objectid import ObjectId
import gridfs

def get_gridfs():
    return gridfs.GridFS(mongo.db)

def save_file(file_storage, filename):
    fs = get_gridfs()
    file_id = fs.put(file_storage.stream, filename=filename, content_type=file_storage.mimetype)
    return str(file_id)

def get_file(file_id):
    try:
        fs = get_gridfs()
        return fs.get(ObjectId(file_id))
    except:
        return None

def delete_file(file_id):
    try:
        fs = get_gridfs()
        fs.delete(ObjectId(file_id))
        return True
    except:
        return False
