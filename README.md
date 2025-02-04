Ecco un file `README.md` completo che copre tutti i file di codice che hai condiviso nella chat (`Portfoliopilot.py` e `config.py`). Questo file fornisce una panoramica del progetto, delle sue funzionalità, della configurazione, dell'installazione e dell'utilizzo.

---

# PortfolioPilot

PortfolioPilot è un'applicazione web basata su Dash che permette agli utenti di creare, analizzare e ottimizzare portafogli di ETF. L'applicazione fornisce strumenti per visualizzare l'andamento del portafoglio, calcolare metriche di performance come CAGR, volatilità e Sharpe Ratio, e confrontare il portafoglio con un benchmark scelto dall'utente.

---

## Struttura del Progetto

Il progetto è composto dai seguenti file principali:

1. **`Portfoliopilot.py`**: Il file principale dell'applicazione Dash. Contiene la logica per la creazione del portafoglio, l'analisi dei dati e la visualizzazione dei grafici.
2. **`config.py`**: File di configurazione che gestisce i percorsi dei file e le impostazioni specifiche per l'ambiente di sviluppo e produzione.

---

## Funzionalità

- **Creazione del Portafoglio**: Aggiungi ETF al tuo portafoglio e assegna una percentuale di allocazione.
- **Analisi del Portafoglio**: Visualizza l'andamento del portafoglio nel tempo, il drawdown, e i rendimenti rolling.
- **Confronto con Benchmark**: Confronta il tuo portafoglio con un benchmark scelto dall'utente.
- **Metriche di Performance**: Calcola metriche come CAGR, volatilità e Sharpe Ratio.
- **Frontiera Efficiente**: Visualizza la frontiera efficiente per ottimizzare il tuo portafoglio.
- **Esposizione ai Fattori**: Analizza l'esposizione del portafoglio ai fattori di Fama-French.

---

## Configurazione

### File `config.py`

Il file `config.py` gestisce i percorsi dei file e le impostazioni specifiche per l'ambiente di sviluppo e produzione. Ecco una panoramica delle variabili principali:

- **`Local`**: Un flag che indica se il codice è in esecuzione su una macchina locale (macOS) o su un server remoto.
- **`FILE_PATH`**: Il percorso del file CSV contenente la lista degli indici.
- **`ETF_BASE_PATH`**: Il percorso della cartella contenente i dati degli ETF.
- **`BASE_PATH`**: Il percorso della cartella base per i dati.

#### Esempio di `config.py`

```python
import os
import platform

# Check if the operating system is macOS (local machine)
if platform.system() == 'Darwin':  # 'Darwin' is the name for macOS
    Local = True
else:
    Local = False

if Local:
    FILE_PATH = "data/Index_list_cleaned.csv"
    ETF_BASE_PATH = "data/ETFs"
    BASE_PATH = "data"
else:
    FILE_PATH = "/home/dani/backtester/backtester-dani/data/Index_list_cleaned.csv"
    ETF_BASE_PATH = "/home/dani/backtester/backtester-dani/data/ETFs"
    BASE_PATH = "/home/dani/backtester/backtester-dani/data"
```

### Personalizzazione

- **Ambiente Locale**: Se stai lavorando su una macchina macOS, imposta `Local = True` e verifica che i percorsi dei file siano corretti.
- **Ambiente di Produzione**: Se il codice è in esecuzione su un server remoto, imposta `Local = False` e modifica i percorsi dei file secondo la struttura del server.

---

## Installazione

1. **Clona il repository**:
   ```bash
   git clone https://github.com/tuo-username/PortfolioPilot.git
   cd PortfolioPilot
   ```

2. **Installa le dipendenze**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura i percorsi dei file**:
   Modifica il file `config.py` per adattarlo al tuo ambiente di sviluppo o produzione.

4. **Esegui l'applicazione**:
   ```bash
   python Portfoliopilot.py
   ```

5. **Accedi all'applicazione**:
   Apri il browser e vai a `http://localhost:80`.

---

## Utilizzo

### Aggiungi ETF

1. Seleziona un ETF dal menu a tendina.
2. Imposta la percentuale di allocazione utilizzando lo slider.
3. Clicca su "Aggiungi ETF" per inserirlo nel portafoglio.

### Crea/Aggiorna Portafoglio

1. Clicca su "Crea/Aggiorna Portafoglio" per generare il portafoglio.
2. Se desideri, seleziona un benchmark e imposta un intervallo di date.

### Analizza il Portafoglio

1. Visualizza i grafici dell'andamento del portafoglio, del drawdown e dei rendimenti rolling.
2. Confronta il portafoglio con il benchmark scelto.

### Ottimizza il Portafoglio

1. Esplora la frontiera efficiente per trovare la migliore combinazione di rischio e rendimento.
2. Analizza l'esposizione del portafoglio ai fattori di Fama-French.

### Esporta il Report

1. Clicca su "Esporta il Report in PDF" per salvare un report dettagliato del portafoglio.

---

## Dipendenze

Il progetto utilizza le seguenti librerie Python:

- **Dash**: Per la creazione dell'interfaccia web.
- **Dash Bootstrap Components**: Per componenti UI avanzati.
- **Pandas**: Per la manipolazione dei dati.
- **Plotly**: Per la visualizzazione dei grafici.
- **Statsmodels**: Per l'analisi statistica.
- **Numpy**: Per calcoli numerici.

Puoi installare tutte le dipendenze eseguendo:
```bash
pip install -r requirements.txt
```

---

## Contributi

Se desideri contribuire al progetto, segui questi passaggi:

1. Fai un fork del repository.
2. Crea un nuovo branch per la tua feature (`git checkout -b feature/nuova-feature`).
3. Fai commit delle tue modifiche (`git commit -m "Aggiunta nuova feature"`).
4. Pusha il branch (`git push origin feature/nuova-feature`).
5. Apri una pull request.

