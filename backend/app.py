# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

# --- Configurazione dell'Applicazione Flask ---
app = Flask(__name__)
CORS(app)

# --- Parametri Crittografici ---
STATIC_SALT = b'un_salt_statico_per_esempio_16b'
KEY_SIZE_BYTES = 32
PBKDF2_ITERATIONS = 100000

def get_key_from_password(password: str) -> bytes:
    """
    Deriva una chiave crittografica a 256 bit da una password testuale
    utilizzando PBKDF2.
    """
    return PBKDF2(password, STATIC_SALT, dkLen=KEY_SIZE_BYTES, count=PBKDF2_ITERATIONS)

# --- ROUTE PER SERVIRE LE PAGINE HTML ---

@app.route('/', methods=['GET'])
def serve_encrypt_page():
    """Serve la pagina di cifratura come pagina principale."""
    return send_from_directory('.', 'cifra.html')

@app.route('/decifra', methods=['GET'])
def serve_decrypt_page():
    """Serve la pagina di decifratura su un percorso dedicato."""
    return send_from_directory('.', 'decifra.html')


# --- ENDPOINT API PER LA CRITTOGRAFIA ---

@app.route('/encrypt', methods=['POST'])
def encrypt_text():
    """Cifra il testo ricevuto via JSON."""
    try:
        data = request.json
        plaintext = data['text']
        password = data['password']

        key = get_key_from_password(password)
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        padded_plaintext = pad(plaintext.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)

        iv_and_ciphertext = iv + ciphertext
        encrypted_b64 = base64.b64encode(iv_and_ciphertext).decode('utf-8')
        
        return jsonify({'result': encrypted_b64})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/decrypt', methods=['POST'])
def decrypt_text():
    """Decifra il testo ricevuto via JSON."""
    try:
        data = request.json
        encrypted_b64 = data['text']
        password = data['password']

        key = get_key_from_password(password)
        iv_and_ciphertext = base64.b64decode(encrypted_b64)
        iv = iv_and_ciphertext[:AES.block_size]
        ciphertext = iv_and_ciphertext[AES.block_size:]
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded_text = cipher.decrypt(ciphertext)
        plaintext = unpad(decrypted_padded_text, AES.block_size).decode('utf-8')

        return jsonify({'result': plaintext})

    except (ValueError, KeyError):
        return jsonify({'error': 'Decodifica fallita. Controlla che la chiave sia corretta e che il testo non sia corrotto.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Esegui il server sulla porta 5001, accessibile da qualsiasi IP del container
    app.run(host='0.0.0.0', port=5001)
