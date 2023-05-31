import hashlib

users = {}
file_owners = {}


def generate_string_hash(credential):
    return hashlib.sha256(credential.encode('utf-8')).hexdigest()


def authenticate(auth_data):
    username, password = generate_string_hash(auth_data['username']), generate_string_hash(auth_data['password'])
    if username in users:
        if users[username] == password:
            return True

    return False


def generate_file_hash(file):
    sha256 = hashlib.sha256()
    for chunk in iter(lambda: file.stream.read(4096), b''):
        sha256.update(chunk)
    file.stream.seek(0)

    return sha256.hexdigest()
