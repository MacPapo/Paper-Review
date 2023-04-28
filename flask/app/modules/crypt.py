from cryptography.fernet import Fernet


class Crypt:
    def encrypt(self, key, message):
        f = Fernet(key)
        token = f.encrypt(
            message.encode()
        )  # Encrypt the bytes. The returning object is of type bytes
        return token

    def decrypt(self, key, token):
        f = Fernet(key)
        message = f.decrypt(token)
        return message.decode()

    def generate_key(self):
        return Fernet.generate_key()
