import os

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import requests
from bs4 import BeautifulSoup


key = os.getenv("FERNET_KEY")

if not key:
    raise ValueError("FERNET KEY missing")

cipher = Fernet(key.encode())

# Helper functions
def hashp(original_p):
    hash_p = generate_password_hash(original_p)
    return hash_p

def valp(oringinal_p, hashed):
    valid = check_password_hash(hashed, oringinal_p)
    return valid

def encrypt_url(url):
    encrypted = cipher.encrypt(url.encode())
    return encrypted.decode()

def decrypt_url(encrypted_url):
    decrypted = cipher.decrypt(encrypted_url.encode())
    return decrypted.decode()

def get_title(url):
    try: 
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        if soup.title and soup.title.string:
            return soup.title.string.strip()
    
        return "No title"
    
    except requests.RequestException:
        return "Untitled"








