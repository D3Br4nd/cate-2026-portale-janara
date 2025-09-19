# Usa un'immagine Python ufficiale
FROM python:3.10-slim

# Imposta la cartella di lavoro all'interno del container
WORKDIR /app

# Copia prima il file dei requisiti. 
# Docker sfrutta la cache: questo step viene rieseguito solo se requirements.txt cambia.
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice dell'applicazione
COPY . .

# Esponi la porta su cui Flask è in esecuzione
EXPOSE 5000

# Comando per avviare l'applicazione quando il container parte
CMD ["python", "app.py"]