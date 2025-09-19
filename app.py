# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

# --- Configurazione dell'Applicazione Flask ---
app = Flask(__name__)
# Abilita CORS per permettere al frontend di comunicare con questo backend
CORS(app)

# --- Parametri Crittografici ---
# ATTENZIONE: Il SALT dovrebbe essere unico per ogni utente o salvato in modo sicuro.
# Per questo esempio, usiamo un salt statico. In un'applicazione reale,
# questo andrebbe gestito in modo più robusto.
STATIC_SALT = b'un_salt_statico_per_esempio_16b' 
# AES richiede che la chiave sia di 16, 24 o 32 byte. Useremo 32 byte (256 bit).
KEY_SIZE_BYTES = 32
# Numero di iterazioni per rendere più difficile un attacco a forza bruta sulla password.
PBKDF2_ITERATIONS = 100000

def get_key_from_password(password: str) -> bytes:
    """
    Deriva una chiave crittografica a 256 bit da una password testuale
    utilizzando PBKDF2. Questo è il modo corretto per non usare mai
    una password direttamente come chiave.
    """
    return PBKDF2(password, STATIC_SALT, dkLen=KEY_SIZE_BYTES, count=PBKDF2_ITERATIONS)

# --- Definizione degli Endpoint API ---

@app.route('/encrypt', methods=['POST'])
def encrypt_text():
    try:
        data = request.json
        plaintext = data['text']
        password = data['password']

        # 1. Deriva la chiave dalla password fornita
        key = get_key_from_password(password)

        # 2. Crea il cifrario AES in modalità CBC (una modalità molto comune)
        #    e genera un Vettore di Inizializzazione (IV) casuale.
        #    L'IV è fondamentale per la sicurezza e deve essere unico per ogni cifratura.
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # 3. Cifra il testo. Prima si applica un padding per rendere la lunghezza
        #    del testo un multiplo della dimensione del blocco AES (16 byte).
        padded_plaintext = pad(plaintext.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)

        # 4. Unisci IV e testo cifrato. Il client che decifra avrà bisogno di entrambi.
        #    Li codifichiamo in Base64 per una facile trasmissione via JSON.
        iv_and_ciphertext = iv + ciphertext
        encrypted_b64 = base64.b64encode(iv_and_ciphertext).decode('utf-8')
        
        return jsonify({'result': encrypted_b64})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/decrypt', methods=['POST'])
def decrypt_text():
    try:
        data = request.json
        encrypted_b64 = data['text']
        password = data['password']

        # 1. Deriva la chiave dalla password, esattamente come in fase di cifratura.
        key = get_key_from_password(password)

        # 2. Decodifica il testo da Base64 e separa l'IV dal testo cifrato.
        iv_and_ciphertext = base64.b64decode(encrypted_b64)
        iv = iv_and_ciphertext[:AES.block_size]
        ciphertext = iv_and_ciphertext[AES.block_size:]
        
        # 3. Crea il cifrario AES con la stessa chiave e l'IV recuperato.
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # 4. Decifra il testo e rimuovi il padding.
        decrypted_padded_text = cipher.decrypt(ciphertext)
        plaintext = unpad(decrypted_padded_text, AES.block_size).decode('utf-8')

        return jsonify({'result': plaintext})

    except (ValueError, KeyError) as e:
        # Questo errore si verifica spesso se la chiave è sbagliata o i dati sono corrotti,
        # perché il "unpad" fallisce.
        return jsonify({'error': 'Decodifica fallita. Controlla che la chiave sia corretta e che il testo non sia corrotto.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Esegui il server sulla porta 5001, accessibile da qualsiasi IP
    app.run(host='0.0.0.0', port=5001, debug=True)