import os
import glob

from utils import authenticate, generate_file_hash, generate_string_hash
from config import db, storage_directory

from flask import Flask, request, jsonify, send_file
from functools import wraps

app = Flask(__name__)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_data = request.authorization
        if not auth_data:
            return jsonify({'message': 'Authentication required'}), 401
        if not authenticate(auth_data):
            return jsonify({'message': 'Authentication failed'}), 400

        return f(*args, **kwargs)

    return decorated


@app.route('/register', methods=['POST'])
def create_user():
    auth_data = request.authorization
    username, password = generate_string_hash(auth_data['username']), generate_string_hash(auth_data['password'])
    if db.get_user(username):
        return jsonify({'message': 'The user with this username already exists'}), 400

    db.add_user(username, password)

    return jsonify({'message': 'The user was created successfully'}), 201


@app.route('/upload', methods=['POST'])
@requires_auth
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'message': 'No file selected'}), 400

    _, extension = os.path.splitext(file.filename)
    file_hash = generate_file_hash(file)
    final_filename = file_hash + extension

    subdirectory_path = os.path.join(storage_directory, file_hash[:2])
    os.makedirs(subdirectory_path, exist_ok=True)

    file_path = os.path.join(subdirectory_path, final_filename)
    if os.path.exists(file_path):
        return jsonify({'message': 'The file already exists in storage'}), 400

    file.save(file_path)

    db.add_file(file_hash, generate_string_hash(request.authorization['username']))

    return jsonify({'hash': file_hash}), 200


@app.route('/delete/<string:file_hash>', methods=['DELETE'])
@requires_auth
def delete_file(file_hash):
    subdirectory_path = os.path.join(storage_directory, file_hash[:2])

    file_paths = glob.glob(os.path.join(subdirectory_path, file_hash + '.*'))
    if not file_paths:
        return jsonify({'message': 'File not found'}), 404

    hashed_username = generate_string_hash(request.authorization['username'])
    if (file_hash,) not in db.get_user_files(hashed_username):
        return jsonify({'message': 'You aren\'t permitted to delete this file'}), 400

    db.delete_file(file_hash)
    os.remove(file_paths[0])
    if not os.listdir(subdirectory_path):
        os.rmdir(subdirectory_path)

    return jsonify({'message': 'File was deleted'}), 200


@app.route('/download/<string:file_hash>', methods=['GET'])
def download_file(file_hash):
    file_path = os.path.join(storage_directory, file_hash[:2], file_hash + '.*')
    matches = glob.glob(file_path)
    if matches:
        return send_file(matches[0], as_attachment=True)

    return jsonify({'message': 'File not found'}), 404


if __name__ == '__main__':
    app.run()
