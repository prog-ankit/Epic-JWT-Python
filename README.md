# Bulk Data Request Using JWT Authentication

## Overview

This project demonstrates how to interact with FHIR APIs using JWT authentication and bulk data requests. The project is split into three main scripts:

- **`generate_keys.sh`**: Generates public and private key files.
- **`token_manager.py`**: Generates an access token and writes it to a file.
- **`bulk_data_request.py`**: Handles the bulk data request process.

---

## Configuration

Create a `.env` file in the root directory with the following configurations:

```plaintext
CLIENT_ID=AVAILABLE_FROM_APP_REGISTRATION
AUTH_URL=https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token
PRIVATE_KEY_PATH=FILE_PATH_FOR_PRIVATE_KEY
BASE_URI=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/
GROUP_ID=e3iabhmS8rsueyz7vaimuiaSmfGvi.QwjVXJANlPOgR83
```
<h2>Script Functionalities</h2>

<h3>generate_keys.sh</h3>
<p>This script generates:</p>
<ul>
    <li><strong>Public Key:</strong> Used for verification.</li>
    <li><strong>Private Key:</strong> Used for signing the JWT.</li>
</ul>

<h3>token_manager.py</h3>
<p>Generates a JSON Web Token (JWT) and uses it to request an access token from the <code>AUTH_URL</code>. The access token is then saved to a file.</p>

<h3>bulk_data_request.py</h3>
<p>The script performs the following tasks:</p>
<ul>
    <li>Initiates a bulk data request.</li>
    <li>Checks the status of the bulk data request.</li>
    <li>If the request is complete:
        <ul>
            <li>Fetches the data file.</li>
        </ul>
    </li>
    <li>If not complete:
        <ul>
            <li>Waits for the recommended interval and retries.</li>
        </ul>
    </li>
    <li>Deletes the bulk data request after the data file is processed.</li>
</ul>

<h2>JSON Web Token (JWT)</h2>
<p>JWT is a compact and self-contained way to securely transmit information as a JSON object. It consists of three parts:</p>
<ul>
    <li><strong>Header:</strong> Contains metadata about the token.</li>
    <li><strong>Payload:</strong> Contains the claims or data being transmitted.</li>
    <li><strong>Signature:</strong> Ensures the token’s integrity and authenticity.</li>
</ul>

<h3>Sample JWT</h3>
<p><strong>Encoded:</strong></p>
<pre>
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ
</pre>
<p><strong>Decoded:</strong></p>
<pre>
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
</pre>

<h2>Cryptography in JWT with RS256</h2>
<p>RS256 uses asymmetric cryptography (RSA) for signing and verification.</p>

<h3>Steps:</h3>

<h4>Private Key Signing:</h4>
<ul>
    <li>The server signs the JWT’s header and payload using the private key.</li>
    <li>Only the holder of the private key can create a valid token.</li>
</ul>

<h4>Public Key Verification:</h4>
<ul>
    <li>The recipient verifies the token’s signature using the public key.</li>
    <li>The public key can only verify tokens, not create them.</li>
</ul>

<hr>

<h2>Screenshots:</h2>

![EPIC 1](https://github.com/user-attachments/assets/8e016869-1124-49b4-a196-9ae3f07225e7)

![EPIC 2](https://github.com/user-attachments/assets/4def51bd-1dd4-4b26-8f42-31732cb160bb)


        
