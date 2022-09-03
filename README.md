# PCTO del DAIS

Applicazione web atta a gestire i corsi di orientamento dell'università Ca' Foscari di venezia.

## Struttura codice

L'applicativo si divide in due aree:
  
- **Backend** - sviluppato usando `Python` con il framework `FLask`
- **Frontend** - sviluppato usando `JavaScript` con il framework `Angular`

## Configurazione

Segue una breve guida su come installare e configurare i file necessari a far funzionare l'applicativo.

>**ATTENZIONE:** la seguente procedura vale per ambiente windows, per altri sistemi operativi i comandi potrebbero leggermente variare.

- **Databse:**
    1. Creare ruoli ed utenti del database necessari all'applicativo (vedere documentazione);
    2. Eseguire il dump del database (`./dump database e file JSON scuole\PostgreSQL___postgres_localhost-2022_08_28_18_03_47-dump.sql`) su DBMS Postgresql.
- **Backend:**    
    1. (*Opzionale*) Creare virtual environment;
    2. Installare i pacchetti Python usando il seguente comando: `pip install -r requirements.txt`;
    3. Settare il file `.\sorgente_orientamento_dais\backend\.env`, ecco un esempio di configurazione:
    ```
    SECRET_KEY=password
    SQLALCHEMY_DATABASE_URI=postgresql://postgres:password@localhost:5432/orientamento_dais
    SQLALCHEMY_DATABASE_URI_PRELOGIN=postgresql://preLoginUser_flask:password@localhost:5432/orientamento_dais
    SQLALCHEMY_DATABASE_URI_STUDENTI=postgresql://studente_flask:password@localhost:5432/orientamento_dais
    SQLALCHEMY_DATABASE_URI_DOCENTI=postgresql://docente_flask:password@localhost:5432/orientamento_dais
    SQLALCHEMY_DATABASE_URI_AMMINISTRATORI=postgresql://amministratore_flask:password@localhost:5432/orientamento_dais
    UPLOAD_FOLDER=.\static
    MAIL_PW=password
    ```
- **Frontend:**
    1. installare pacchetti necessari lanciando il comando `pip install`.

## Avvio dell'applicativo

>**ATTENZIONE:** la seguente procedura vale per ambiente windows, per altri sistemi operativi i comandi potrebbero leggermente variare.

Segue una breve guida su come avviare l'applicativo.

- **Backend:**
    1. Impostare le variabili d'ambiente necessari per l'avvio di Flask con i seguenti comandi:
        1. `$env:FLASK_ENV = "development"`
        2. `$env:FLASK_DEBUG = "1"` 
    2. (*Opzionale*) Avviare virtual environment con il seguente comando: `.\venv\Scripts\activate`;
    3. Avviare Flask con il seguente comoando: `flask run`.
- **Frontend:**
    1. Avviare Angular con il seguente comando: `ng serve`.