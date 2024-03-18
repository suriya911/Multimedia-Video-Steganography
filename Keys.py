from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import random,string,secrets
import os

# To generate a random password for the AES key
def generate_random_password():
    length=random.randint(8,20)
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

# To generate the random AES key using the random password generated 
def generate_aes_key():
    password = generate_random_password()
    salt = b'salt_'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256 key length
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key.hex()

# To encrypt the AES key using the RSA public key and store it in a file
def encrypt_key(Public_key):
    # Load RSA public key from PEM file
    with open(Public_key, 'rb') as f:
        RSA_public_key = serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )

    # Load AES key from text file
    with open('./Keys/aes_key.txt', 'rb') as f:
        aes_key = f.read()


    # Encrypt AES key with RSA public key
    encrypted_aes_key = RSA_public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Save the encrypted AES key to a file
    with open('./Keys/encrypted_aes_key.enc', 'wb') as f:
        f.write(encrypted_aes_key)

# To decrypt the AES key using the RSA private key and store it in a file
def decrypt_key(RSA_Key):
    # Load RSA private key from PEM file
    with open(RSA_Key, 'rb') as f:
        RSA_private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,  # You may need to provide a password if the key is encrypted
            backend=default_backend()
        )

    # Load the encrypted AES key from file
    with open('./Retrived_Files/key.enc', 'rb') as f:
        encrypted_aes_key = f.read()

    # Decrypt AES key with RSA private key
    decrypted_aes_key = RSA_private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Save the decrypted AES key to a file
    with open('./Retrived_Files/decrypted_aes_key.txt', 'wb') as f:
        f.write(decrypted_aes_key)

# To call the function to generate the AES key and store it in a file
def call_aes_key():
    aes_key=generate_aes_key()
    if not os.path.exists("./Keys"):
        os.makedirs("./Keys")
    file_obj = open("./Keys/aes_key.txt", "wb")
    file_obj.write(aes_key.encode())
    file_obj.close()

# To call the function to generate the RSA key pair and store it in a file
def generate_rsa_key():
    # Generate RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    public_key = private_key.public_key()

    # Serialize the keys to PEM format
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    if not os.path.exists("./Keys"):
        os.makedirs("./Keys")
    file_obj1 = open("./Keys/RSA_public.pem", "wb")
    file_obj2 = open("./Keys/RSA_private.pem", "wb")
    file_obj1.write(public_key_pem)
    file_obj2.write(private_key_pem)