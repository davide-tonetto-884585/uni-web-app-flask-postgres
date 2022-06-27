-- utenti e ruoli
CREATE ROLE studenteDAIS WITH
    NOLOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    NOREPLICATION
    CONNECTION LIMIT -1;

CREATE ROLE studente_flask WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    NOREPLICATION
    CONNECTION LIMIT -1
    PASSWORD 'pw_studente_flask';

GRANT "studenteDAIS" TO studente_flask;

CREATE ROLE docenteDAIS WITH
    NOLOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    NOREPLICATION
    CONNECTION LIMIT -1;

CREATE ROLE docente_flask WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    NOREPLICATION
    CONNECTION LIMIT -1
    PASSWORD 'pw_docente_flask';

GRANT "docenteDAIS" TO docente_flask;

CREATE ROLE amministratoreDAIS WITH
    NOLOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    NOREPLICATION
    CONNECTION LIMIT -1;

CREATE ROLE amministratore_flask WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    NOREPLICATION
    CONNECTION LIMIT -1
    PASSWORD 'pw_amministratore_flask';

GRANT "amministratoreDAIS" TO amministratore_flask;

CREATE ROLE "preLoginUser_flask" WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    NOREPLICATION
    CONNECTION LIMIT -1
    PASSWORD 'pw_preloginuser_flask';

-- privileges
grant usage on schema public to "amministratoreDAIS";
grant usage on schema public to "docenteDAIS";
grant usage on schema public to "studenteDAIS";
grant usage on schema public to "preLoginUser_flask";
-- amministratori
GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.scuole TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.amministratori TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.aule TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.corsi TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.docenti TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.docenti_corso TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.domande_corso TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.iscrizioni_corso TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.like_domanda TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.presenze_lezione TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.programmazione_corso TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.programmazione_lezioni TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.risorse_corso TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.studenti TO "amministratoreDAIS";

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.utenti TO "amministratoreDAIS";

-- docenti
GRANT SELECT ON TABLE public.scuole TO "docenteDAIS";

GRANT SELECT ON TABLE public.aule TO "docenteDAIS";

GRANT SELECT ON TABLE public.docenti TO "docenteDAIS";

GRANT SELECT ON TABLE public.studenti TO "docenteDAIS";

GRANT SELECT ON TABLE public.utenti TO "docenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.corsi TO "docenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.docenti_corso TO "docenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.domande_corso TO "docenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.iscrizioni_corso TO "docenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.like_domanda TO "docenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.presenze_lezione TO "docenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.programmazione_corso TO "docenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.programmazione_lezioni TO "docenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.risorse_corso TO "docenteDAIS";

-- studenti
GRANT SELECT ON TABLE public.scuole TO "studenteDAIS";

GRANT SELECT ON TABLE public.aule TO "studenteDAIS";

GRANT SELECT ON TABLE public.corsi TO "studenteDAIS";

GRANT SELECT ON TABLE public.docenti TO "studenteDAIS";

GRANT SELECT ON TABLE public.docenti_corso TO "studenteDAIS";

GRANT SELECT ON TABLE public.programmazione_corso TO "studenteDAIS";

GRANT SELECT ON TABLE public.programmazione_lezioni TO "studenteDAIS";

GRANT SELECT ON TABLE public.risorse_corso TO "studenteDAIS";

GRANT SELECT ON TABLE public.studenti TO "studenteDAIS";

GRANT SELECT ON TABLE public.utenti TO "studenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.domande_corso TO "studenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.iscrizioni_corso TO "studenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.like_domanda TO "studenteDAIS";

GRANT INSERT, SELECT, UPDATE, DELETE ON TABLE public.presenze_lezione TO "studenteDAIS";

-- pre login user
GRANT SELECT ON TABLE public.amministratori TO "preLoginUser_flask";

GRANT SELECT, INSERT, UPDATE ON TABLE public.studenti TO "preLoginUser_flask";

GRANT SELECT, INSERT, UPDATE ON TABLE public.utenti TO "preLoginUser_flask";

GRANT SELECT, UPDATE ON TABLE public.docenti TO "preLoginUser_flask";

GRANT SELECT ON TABLE public.scuole TO "preLoginUser_flask";

GRANT SELECT ON TABLE public.corsi TO "preLoginUser_flask";

GRANT SELECT ON TABLE public.domande_corso TO "preLoginUser_flask";

GRANT SELECT ON TABLE public.like_domanda TO "preLoginUser_flask";

GRANT SELECT ON TABLE public.programmazione_corso TO "preLoginUser_flask";

GRANT SELECT ON TABLE public.programmazione_lezioni TO "preLoginUser_flask";

GRANT SELECT ON TABLE public.docenti_corso TO "preLoginUser_flask";




