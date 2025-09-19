# 🏺 Janara - Servizio di Cifratura per Caccia al Tesoro

Janara è un'applicazione Flask containerizzata progettata per cifrare e decifrare enigmi durante cacce al tesoro. Utilizza crittografia AES-256-CBC con derivazione di chiavi PBKDF2 per proteggere i contenuti degli enigmi dai concorrenti.

## ✨ Caratteristiche

- **Crittografia Sicura**: AES-256-CBC con salt dinamici casuali
- **Interface Web Tematizzata**: Pagine HTML con tema magico/misterioso
- **API RESTful**: Endpoint JSON per integrazione con altre applicazioni
- **Container-Ready**: Docker e Docker Compose inclusi
- **Nginx Proxy Manager**: Configurato per reverse proxy con SSL
- **Health Monitoring**: Endpoint di stato per monitoraggio

## 🚀 Avvio Rapido

### Prerequisiti

- Docker e Docker Compose installati
- Nginx Proxy Manager configurato con rete `plv_network`
- Dominio puntato al server (es. `mio-sito.com`)

### Deployment

1. **Clona il repository**
   ```bash
   git clone <repository-url>
   cd cate-2026-portale-janara
   ```

2. **Costruisci l'immagine Docker**
   ```bash
   cd backend
   docker build -t janara:1.1 .
   ```

3. **Avvia il servizio**
   ```bash
   cd ..
   docker compose up -d
   ```

4. **Configura Nginx Proxy Manager**
   - Host: `janara` (nome container)
   - Porta: `5001`
   - Percorso avanzato: `/janara` → `http://janara:5001/janara`

## 🌐 Accesso al Servizio

Una volta deployato, il servizio sarà accessibile all'indirizzo:

- **Cifratura**: `https://mio-sito.com/janara`
- **Decifratura**: `https://mio-sito.com/janara/decifra`

## 📡 API Endpoints

### Cifratura
```http
POST /janara/encrypt
Content-Type: application/json

{
  "text": "Il tesoro si trova sotto il grande quercia",
  "password": "chiave_segreta"
}
```

**Risposta:**
```json
{
  "result": "base64_encrypted_text"
}
```

### Decifratura
```http
POST /janara/decrypt
Content-Type: application/json

{
  "text": "base64_encrypted_text",
  "password": "chiave_segreta"
}
```

**Risposta:**
```json
{
  "result": "Il tesoro si trova sotto il grande quercia"
}
```

### Stato del Servizio
```http
GET /janara/health
```

**Risposta:**
```json
{
  "status": "healthy",
  "service": "Janara Crypto Service",
  "version": "1.0"
}
```

### Informazioni del Servizio
```http
GET /janara/info
```

**Risposta:**
```json
{
  "service": "Janara - Servizio di Cifratura per Caccia al Tesoro",
  "algorithm": "AES-256-CBC",
  "key_derivation": "PBKDF2",
  "iterations": 100000,
  "endpoints": {
    "encrypt": "/janara/encrypt",
    "decrypt": "/janara/decrypt",
    "web_encrypt": "/janara/",
    "web_decrypt": "/janara/decifra"
  }
}
```

## 🔧 Configurazione Nginx Proxy Manager

Per configurare correttamente il reverse proxy:

1. **Crea nuovo Proxy Host**
   - Domain Names: `mio-sito.com`
   - Scheme: `http`
   - Forward Hostname/IP: `janara`
   - Forward Port: `5001`

2. **Configurazione SSL**
   - SSL Certificate: Let's Encrypt o certificato custom
   - Force SSL: ✅ Abilitato
   - HTTP/2 Support: ✅ Abilitato

3. **Configurazione Avanzata** (facoltativa)
   ```nginx
   location /janara {
       proxy_pass http://janara:5001/janara;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
   }
   ```

## 💻 Sviluppo Locale

Per sviluppo e testing locale:

```bash
# Crea ambiente virtuale
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate     # Windows

# Installa dipendenze
cd backend
pip install -r requirements.txt

# Avvia in modalità sviluppo
python app.py
```

Il servizio sarà disponibile su `http://localhost:5001/janara`

## 🔐 Dettagli Crittografici

### Algoritmo di Cifratura
- **Algoritmo**: AES-256-CBC (Advanced Encryption Standard)
- **Modalità**: Cipher Block Chaining
- **Lunghezza Chiave**: 256 bit (32 bytes)
- **Derivazione Chiave**: PBKDF2 con 100.000 iterazioni
- **Salt**: Casuale a 16 bytes per ogni operazione
- **IV**: Casuale a 16 bytes per ogni cifratura

### Formato Output
Il testo cifrato finale è strutturato come:
```
[16 bytes Salt][16 bytes IV][N bytes Ciphertext]
```
Tutto codificato in Base64 per facilità di trasporto.

### Sicurezza
- **Salt Dinamici**: Ogni cifratura usa un salt casuale unico
- **IV Casuali**: Ogni cifratura usa un Initialization Vector unico
- **Resistant to Rainbow Tables**: Grazie ai salt casuali
- **Forward Secrecy**: Chiavi derivate al momento

## 📊 Monitoraggio e Logging

### Health Check
Il container include un health check automatico che verifica:
- Risposta dell'endpoint `/janara/health`
- Tempo di risposta sotto i 10 secondi
- Controllo ogni 30 secondi

### Log del Container
```bash
# Visualizza i log del servizio
docker compose logs janara

# Segui i log in tempo reale
docker compose logs -f janara
```

### Metriche di Sistema
```bash
# Stato del container
docker compose ps

# Utilizzo risorse
docker stats janara
```

## 🛠️ Gestione del Servizio

### Comandi Utili

```bash
# Avvia il servizio
docker compose up -d

# Ferma il servizio
docker compose down

# Riavvia il servizio
docker compose restart

# Aggiorna il servizio
docker compose pull
docker compose up -d

# Ricostruisci l'immagine
cd backend
docker build -t janara:1.1 .
cd ..
docker compose up -d
```

### Backup e Ripristino

```bash
# Backup dell'immagine
docker save janara:1.1 > janara-backup.tar

# Ripristino dell'immagine
docker load < janara-backup.tar
```

## 🚨 Troubleshooting

### Problemi Comuni

**Il servizio non risponde:**
1. Verifica che il container sia in esecuzione: `docker compose ps`
2. Controlla i log: `docker compose logs janara`
3. Verifica la rete: `docker network ls | grep plv_network`

**Errori di cifratura/decifratura:**
1. Verifica che la password sia corretta
2. Controlla che il testo cifrato sia valido Base64
3. Assicurati che non ci siano caratteri extra o spazi

**Problemi di connessione Nginx:**
1. Verifica che il container `janara` sia nella rete `plv_network`
2. Controlla la configurazione del proxy host
3. Verifica i certificati SSL

### Debug Mode

Per attivare il debug durante lo sviluppo:

```python
# Nel file app.py, modifica l'ultima riga:
app.run(host='0.0.0.0', port=port, debug=True)
```

## 🎯 Utilizzo per Caccia al Tesoro

### Scenari d'Uso

1. **Protezione Enigmi**: Cifra indizi e enigmi per impedire che i concorrenti li risolvano con strumenti automatici

2. **Controllo Progressione**: Usa password diverse per ogni tappa, rivelate solo al completamento della precedente

3. **Validazione Soluzioni**: Cifra le risposte corrette, i concorrenti devono decifrarle per procedere

### Esempio Pratico

```bash
# Enigma Master cifra un indizio
POST /janara/encrypt
{
  "text": "Il prossimo indizio si trova nella biblioteca, scaffale 7, libro rosso",
  "password": "tappa2_biblioteca"
}

# Risultato: "eyJhbGciOiJI... (base64)"

# I concorrenti ricevono il testo cifrato e la password solo dopo aver completato la tappa precedente
```

## 📝 Licenza e Contributi

Questo progetto è sviluppato per scopi ludici ed educativi. 

### Struttura del Progetto
```
cate-2026-portale-janara/
├── backend/
│   ├── app.py              # Applicazione Flask principale
│   ├── cifra.html          # Interface web per cifratura
│   ├── decifra.html        # Interface web per decifratura
│   ├── requirements.txt     # Dipendenze Python
│   └── Dockerfile          # Container Docker
├── docker-compose.yaml     # Orchestrazione servizi
├── .gitignore             # File ignorati da Git
└── README.md              # Questa documentazione
```

---

**🏺 Che la magia di Janara protegga i tuoi enigmi! 🏺**