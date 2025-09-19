# Usa un'immagine Python ufficiale e leggera
FROM python:3.11-slim

# Installa wget per health check
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

# Imposta la cartella di lavoro all'interno del container
WORKDIR /app

# Copia il file dei requisiti e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia TUTTO il contenuto della cartella 'backend' nel container
COPY . .

# Crea un utente non privilegiato per sicurezza
RUN useradd --create-home --shell /bin/bash janara && \
    chown -R janara:janara /app
USER janara

# Esponi la porta su cui Flask è in esecuzione
EXPOSE 5001

# Health check interno
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5001/janara/health || exit 1

# Comando per avviare l'applicazione
CMD ["python", "app.py"]
