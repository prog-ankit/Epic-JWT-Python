import json
import os
import time
import requests
from datetime import datetime, timedelta, timezone
from requests.structures import CaseInsensitiveDict
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import uuid
from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = 'token.json'

def get_access_token():
    """Reads the TOKEN_FILE and returns the token if it is not expired otherwise make a call to generate token function."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            token_data = json.load(f)
            access_token = token_data.get("access_token")
            expires_at = token_data.get("expires_at")
            if access_token and time.time() < expires_at:
                return access_token
    
    print("Existing Access Token Not Found, Generating New...")
    return generate_new_access_token()

def generate_new_access_token():
    """Generates an new access and update the TOKEN_FILE."""
    try:
        message = {
            'iss': os.getenv('CLIENT_ID'),
            'sub': os.getenv('CLIENT_ID'),
            'aud': os.getenv('AUTH_URL'),
            'jti': str(uuid.uuid4()),
            'iat': int(datetime.now(timezone.utc).timestamp()),
            'exp': int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
        }
        try:
            # Loads Private Key from the path
            with open(os.getenv('PRIVATE_KEY_PATH'), 'rb') as fh:
                #load_pem_private_key -Parses the private key in PEM (Privacy-Enhanced Mail) format from the file contents.
                private_key = serialization.load_pem_private_key(
                    fh.read(),
                    password=None, # As private is not encrypted using any password, it is mentioned as None.
                    backend=default_backend() # Specifies the cryptographic backend to use for the operation. 
                )
                
            print("Generating JWT Token.. ")
            compact_jws = jwt.encode(message, private_key, algorithm='RS256') # Generates the JWT Token (Not Signed Yet).
        
            headers = CaseInsensitiveDict()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            data = {
                'grant_type': 'client_credentials',
                'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                'client_assertion': compact_jws
            }
            print("Signing JWT Token.. ")
            response = requests.post(os.getenv('AUTH_URL'), headers=headers, data=data)
            access_token = response.json().get("access_token")
            expires_in = response.json().get("expires_in", 0)
            
            if access_token:
                print("Access Token Generated")
                expires_at = time.time() + expires_in
                with open(TOKEN_FILE, 'w') as f:
                    json.dump({"access_token": access_token, "expires_at": expires_at}, f)
                return access_token
            else:
                print("Fail to generate access token.")
        except Exception as e:
            print("Private key file not found ")
        
    except Exception as e:
        print("An error occurred:", e)
    return None