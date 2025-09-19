# Usa un'immagine Python ufficiale e leggera
FROM python:3.10-slim

# Imposta la cartella di lavoro all'interno del container
WORKDIR /app

# Copia il file dei requisiti e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia TUTTO il contenuto della cartella 'backend' (app.py, html, etc.)
# nel container. Questa è la riga modificata.
COPY . .

# Esponi la porta su cui Flask è in esecuzione
EXPOSE 5001

# Comando per avviare l'applicazione
CMD ["python", "app.py"]