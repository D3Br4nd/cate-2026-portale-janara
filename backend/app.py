# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import os

# --- Configurazione dell'Applicazione Flask ---
app = Flask(__name__)
CORS(app)

# --- Parametri Crittografici ---
KEY_SIZE_BYTES = 32
PBKDF2_ITERATIONS = 100000

def get_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Deriva una chiave crittografica a 256 bit da una password testuale
    utilizzando PBKDF2 con salt dinamico.
    """
    return PBKDF2(password, salt, dkLen=KEY_SIZE_BYTES, count=PBKDF2_ITERATIONS)

# --- ROUTE PER SERVIRE LE PAGINE HTML CON PREFISSO /janara ---

@app.route('/janara', methods=['GET'])
@app.route('/janara/', methods=['GET'])
def serve_encrypt_page():
    """Serve la pagina di cifratura come pagina principale su /janara."""
    return send_from_directory('.', 'cifra.html')

@app.route('/janara/decifra', methods=['GET'])
def serve_decrypt_page():
    """Serve la pagina di decifratura su /janara/decifra."""
    return send_from_directory('.', 'decifra.html')

# --- ENDPOINT API PER LA CRITTOGRAFIA CON PREFISSO /janara ---

@app.route('/janara/encrypt', methods=['POST'])
def encrypt_text():
    """Cifra il testo ricevuto via JSON con salt dinamico."""
    try:
        data = request.json
        if not data or 'text' not in data or 'password' not in data:
            return jsonify({'error': 'Dati mancanti: text e password sono obbligatori'}), 400
            
        plaintext = data['text']
        password = data['password']
        
        if not plaintext or not password:
            return jsonify({'error': 'Text e password non possono essere vuoti'}), 400

        # Genera un salt casuale per questa operazione
        salt = get_random_bytes(16)
        key = get_key_from_password(password, salt)
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        padded_plaintext = pad(plaintext.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)

        # Concatena: salt + iv + ciphertext
        salt_iv_and_ciphertext = salt + iv + ciphertext
        encrypted_b64 = base64.b64encode(salt_iv_and_ciphertext).decode('utf-8')
        
        return jsonify({'result': encrypted_b64})

    except Exception as e:
        return jsonify({'error': f'Errore durante la cifratura: {str(e)}'}), 500


@app.route('/janara/decrypt', methods=['POST'])
def decrypt_text():
    """Decifra il testo ricevuto via JSON utilizzando salt dinamico."""
    try:
        data = request.json
        if not data or 'text' not in data or 'password' not in data:
            return jsonify({'error': 'Dati mancanti: text e password sono obbligatori'}), 400
            
        encrypted_b64 = data['text']
        password = data['password']
        
        if not encrypted_b64 or not password:
            return jsonify({'error': 'Text cifrato e password non possono essere vuoti'}), 400

        try:
            salt_iv_and_ciphertext = base64.b64decode(encrypted_b64)
        except Exception:
            return jsonify({'error': 'Testo cifrato non valido (errore Base64)'}), 400

        # Estrai salt (primi 16 bytes), IV (successivi 16 bytes) e ciphertext
        if len(salt_iv_and_ciphertext) < 32:
            return jsonify({'error': 'Testo cifrato troppo corto'}), 400
            
        salt = salt_iv_and_ciphertext[:16]
        iv = salt_iv_and_ciphertext[16:32]
        ciphertext = salt_iv_and_ciphertext[32:]
        
        key = get_key_from_password(password, salt)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded_text = cipher.decrypt(ciphertext)
        plaintext = unpad(decrypted_padded_text, AES.block_size).decode('utf-8')

        return jsonify({'result': plaintext})

    except (ValueError, KeyError) as e:
        return jsonify({'error': 'Decodifica fallita. Controlla che la chiave sia corretta e che il testo non sia corrotto.'}), 400
    except Exception as e:
        return jsonify({'error': f'Errore durante la decifratura: {str(e)}'}), 500

# --- ROUTE DI STATO E SALUTE ---

@app.route('/janara/health', methods=['GET'])
def health_check():
    """Endpoint per verificare lo stato dell'applicazione."""
    return jsonify({
        'status': 'healthy',
        'service': 'Janara Crypto Service',
        'version': '1.0'
    })

@app.route('/janara/info', methods=['GET'])
def service_info():
    """Informazioni sul servizio."""
    return jsonify({
        'service': 'Janara - Servizio di Cifratura per Caccia al Tesoro',
        'algorithm': 'AES-256-CBC',
        'key_derivation': 'PBKDF2',
        'iterations': PBKDF2_ITERATIONS,
        'endpoints': {
            'encrypt': '/janara/encrypt',
            'decrypt': '/janara/decrypt',
            'web_encrypt': '/janara/',
            'web_decrypt': '/janara/decifra'
        }
    })

if __name__ == '__main__':
    # Esegui il server sulla porta 5001, accessibile da qualsiasi IP del container
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
