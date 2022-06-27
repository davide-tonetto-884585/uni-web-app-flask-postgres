SET check_function_bodies = false;

/* Enum 'enum_modalità_lezioni' */
CREATE TYPE enum_modalità_lezioni AS ENUM('online', 'presenza', 'duale');

/* Enum 'enum_indirizzi_scuole' */
CREATE TYPE enum_indirizzi_scuole AS ENUM
  ('informatico', 'scientifico tradizionale', 'altro indirizzo liceale', 'scientifico scienze applicate', 'elettronica', 'elettrotecnica', 'meccatronica', 'altro indirizzo tecnico')
  ;

/* Table 'utenti' */
CREATE TABLE utenti(
  id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  email varchar(55) NOT NULL,
  salt varchar,
  digest varchar,
  nome varchar(55) NOT NULL,
  cognome varchar(55) NOT NULL,
  data_nascita date NOT NULL,
  token_verifica varchar,
  verificato bool NOT NULL DEFAULT FALSE,
  abilitato bool NOT NULL DEFAULT TRUE,
  PRIMARY KEY(id)
);

CREATE UNIQUE INDEX "Utenti_ix_email" ON utenti(email);

COMMENT ON TABLE utenti IS
  'Dati degli utenti iscritti al sito tra cui studenti e docenti';

/* Table 'studenti' */
CREATE TABLE studenti(
  id integer NOT NULL,
  indirizzo_di_studio enum_indirizzi_scuole NOT NULL,
  id_scuola varchar NOT NULL,
  PRIMARY KEY(id)
);

COMMENT ON TABLE studenti IS
  'Sottoctegoria di utenti rappresentante i possibili futuri studenti interessati ai corsi di orintamento '
  ;

/* Table 'docenti' */
CREATE TABLE docenti(
  id integer NOT NULL,
  descrizione_docente text,
  immagine_profilo varchar,
  link_pagina_docente varchar,
  PRIMARY KEY(id)
);

COMMENT ON TABLE docenti IS
  'Sottoctegoria di utenti rappresentante i docenti dell''università incaricati di gestire i corsi di orientamento'
  ;

/* Table 'corsi' */
CREATE TABLE corsi(
  id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  titolo varchar NOT NULL,
  descrizione text,
  lingua varchar(25),
  immagine_copertina varchar,
  file_certificato varchar,
  abilitato bool NOT NULL DEFAULT TRUE,
  PRIMARY KEY(id)
);

COMMENT ON TABLE corsi IS 'corsi di orientamento proposti dai vari docenti';

/* Table 'docenti_corso' */
CREATE TABLE docenti_corso(
id_docente integer NOT NULL, id_corso integer NOT NULL,
  PRIMARY KEY(id_docente, id_corso)
);

COMMENT ON TABLE docenti_corso IS 'docente o docenti responsabili di un corso';

/* Table 'risorse_corso' */
CREATE TABLE risorse_corso(
  id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  nome varchar NOT NULL,
  path_risorsa varchar NOT NULL,
  visibile bool NOT NULL DEFAULT TRUE,
  id_corso integer NOT NULL,
  PRIMARY KEY(id)
);

COMMENT ON TABLE risorse_corso IS
  'risorse messe a disposizione dai docenti per un corso';

/* Table 'aule' */
CREATE TABLE aule(
  id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  nome varchar(55) NOT NULL,
  edificio varchar(55) NOT NULL,
  campus varchar(55) NOT NULL,
  capienza integer NOT NULL,
  PRIMARY KEY(id)
);

COMMENT ON TABLE aule IS
  'aule dell''ateneo disponibili per i corsi di orientamento';

/* Table 'programmazione_lezioni' */
CREATE TABLE programmazione_lezioni(
  id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  "data" date NOT NULL check (data > current_date),
  orario_inizio time NOT NULL,
  orario_fine time NOT NULL,
  link_stanza_virtuale varchar,
  passcode_stanza_virtuale varchar(55),
  codice_verifica_presenza varchar NOT NULL,
  id_aula integer NOT NULL,
  id_programmazione_corso integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  PRIMARY KEY(id)
);

COMMENT ON TABLE programmazione_lezioni IS
  'calendario delle lezioni dei vari corsi';

alter table programmazione_lezioni
add constraint "check_orari" check ( orario_inizio < orario_fine )

/* Table 'programmazione_corso' */
CREATE TABLE programmazione_corso(
  id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  modalità enum_modalità_lezioni NOT NULL,
  limite_iscrizioni integer,
  password_certificato varchar(25) NOT NULL,
  id_corso integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  PRIMARY KEY(id)
);

COMMENT ON TABLE programmazione_corso IS
  'programmazione dello svolgimento di un corso';

/* Table 'iscrizioni_corso' */
CREATE TABLE iscrizioni_corso(
  id_studente integer NOT NULL,
  id_programmazione_corso integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  "inPresenza" bool,
  PRIMARY KEY(id_studente, id_programmazione_corso)
);

/* Table 'presenze_lezione' */
CREATE TABLE presenze_lezione(
id_studente integer NOT NULL,
  id_programmazione_lezioni integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  PRIMARY KEY(id_studente, id_programmazione_lezioni)
);

COMMENT ON TABLE presenze_lezione IS 'storico presenze studenti alle lezioni';

/* Table 'domande_corso' */
CREATE TABLE domande_corso(
  id integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  id_utente integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  id_corso integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  testo text NOT NULL,
  chiusa bool NOT NULL DEFAULT FALSE,
  id_domanda_corso integer,
  PRIMARY KEY(id)
);

COMMENT ON TABLE domande_corso IS
  'domande post dagli studenti al docente del corso e risposte';

/* Table 'like_domanda' */
CREATE TABLE like_domanda(
id_utente integer NOT NULL GENERATED ALWAYS AS IDENTITY,
  id_domanda_corso integer NOT NULL, PRIMARY KEY(id_utente, id_domanda_corso)
);

COMMENT ON TABLE like_domanda IS
  'like delle domande usati per dare priorità alle domande più votate';

/* Table 'amministratori' */
CREATE TABLE amministratori(id integer NOT NULL, PRIMARY KEY(id));

COMMENT ON TABLE amministratori IS
  'amministratori di sistema con dei privilegi in più';

/* Table 'scuole' */
CREATE TABLE scuole(
  id varchar NOT NULL,
  denominazione varchar NOT NULL,
  comune varchar NOT NULL,
  tipologia varchar NOT NULL,
  indirizzo varchar NOT NULL,
  provincia varchar NOT NULL,
  regione varchar NOT NULL,
  sito varchar NOT NULL,
  PRIMARY KEY(id)
);

COMMENT ON TABLE scuole IS
  'Tabella contenente informzioni delle scuole italiane statali';

/* Relation 'Utenti_Studenti' */
ALTER TABLE studenti
  ADD CONSTRAINT "Utenti_Studenti" FOREIGN KEY (id) REFERENCES utenti (id);

/* Relation 'Utenti_docenti' */
ALTER TABLE docenti
  ADD CONSTRAINT "Utenti_docenti" FOREIGN KEY (id) REFERENCES utenti (id);

/* Relation 'docenti_docenti_corso' */
ALTER TABLE docenti_corso
  ADD CONSTRAINT docenti_docenti_corso
    FOREIGN KEY (id_docente) REFERENCES docenti (id);

/* Relation 'corsi_docenti_corso' */
ALTER TABLE docenti_corso
  ADD CONSTRAINT corsi_docenti_corso FOREIGN KEY (id_corso) REFERENCES corsi (id)
  ;

/* Relation 'corsi_risorse_corso' */
ALTER TABLE risorse_corso
  ADD CONSTRAINT corsi_risorse_corso FOREIGN KEY (id_corso) REFERENCES corsi (id)
  ;

/* Relation 'aule_programmazione_lezioni' */
ALTER TABLE programmazione_lezioni
  ADD CONSTRAINT aule_programmazione_lezioni
    FOREIGN KEY (id_aula) REFERENCES aule (id);

/* Relation 'corsi_programmazione_corso' */
ALTER TABLE programmazione_corso
  ADD CONSTRAINT corsi_programmazione_corso
    FOREIGN KEY (id_corso) REFERENCES corsi (id);

/* Relation 'programmazione_corso_programmazione_lezioni' */
ALTER TABLE programmazione_lezioni
  ADD CONSTRAINT programmazione_corso_programmazione_lezioni
    FOREIGN KEY (id_programmazione_corso) REFERENCES programmazione_corso (id);

/* Relation 'studenti_iscrizioni_corso' */
ALTER TABLE iscrizioni_corso
  ADD CONSTRAINT studenti_iscrizioni_corso
    FOREIGN KEY (id_studente) REFERENCES studenti (id);

/* Relation 'programmazione_corso_iscrizioni_corso' */
ALTER TABLE iscrizioni_corso
  ADD CONSTRAINT programmazione_corso_iscrizioni_corso
    FOREIGN KEY (id_programmazione_corso) REFERENCES programmazione_corso (id);

/* Relation 'studenti_presenze_lezione' */
ALTER TABLE presenze_lezione
  ADD CONSTRAINT studenti_presenze_lezione
    FOREIGN KEY (id_studente) REFERENCES studenti (id);

/* Relation 'programmazione_lezioni_presenze_lezione' */
ALTER TABLE presenze_lezione
  ADD CONSTRAINT programmazione_lezioni_presenze_lezione
    FOREIGN KEY (id_programmazione_lezioni) REFERENCES programmazione_lezioni (id)
  ;

/* Relation 'utenti_domande_corso' */
ALTER TABLE domande_corso
  ADD CONSTRAINT utenti_domande_corso
    FOREIGN KEY (id_utente) REFERENCES utenti (id);

/* Relation 'corsi_domande_corso' */
ALTER TABLE domande_corso
  ADD CONSTRAINT corsi_domande_corso FOREIGN KEY (id_corso) REFERENCES corsi (id)
  ;

/* Relation 'domande_corso_domande_corso' */
ALTER TABLE domande_corso
  ADD CONSTRAINT domande_corso_domande_corso
    FOREIGN KEY (id_domanda_corso) REFERENCES domande_corso (id);

/* Relation 'utenti_like_domanda' */
ALTER TABLE like_domanda
  ADD CONSTRAINT utenti_like_domanda
    FOREIGN KEY (id_utente) REFERENCES utenti (id);

/* Relation 'domande_corso_like_domanda' */
ALTER TABLE like_domanda
  ADD CONSTRAINT domande_corso_like_domanda
    FOREIGN KEY (id_domanda_corso) REFERENCES domande_corso (id);

/* Relation 'docenti_amministratori' */
ALTER TABLE amministratori
  ADD CONSTRAINT docenti_amministratori FOREIGN KEY (id) REFERENCES docenti (id)
  ;

/* Relation 'scuole_studenti' */
ALTER TABLE studenti
  ADD CONSTRAINT scuole_studenti FOREIGN KEY (id_scuola) REFERENCES scuole (id);

/* Function 'check_like' */
CREATE OR REPLACE FUNCTION public.check_like()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    VOLATILE
    COST 100
AS $BODY$
begin
    if (SELECT id_domanda_corso from domande_corso where id = new.id_domanda_corso) is not null then
        RAISE EXCEPTION 'it is not allowed to like an answer';
    end if;
    return new;
end;
$BODY$;

/* Function 'check_risposte' */
CREATE OR REPLACE FUNCTION public.check_risposte()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    VOLATILE
    COST 100
AS $BODY$
begin
    if new.id_domanda_corso is not null then
        if (select chiusa from domande_corso where id = new.id_domanda_corso) = true then
            RAISE EXCEPTION 'it is not allowed to answer closed questions';
        end if;
        if (select id_utente from domande_corso where id = new.id_domanda_corso) != new.id_utente and
           new.id_utente not in (select id_docente from docenti_corso where id_corso = new.id_corso) then
            RAISE EXCEPTION 'only teachers and the author of the question can answer a question';
        end if;
    end if;
    
    return new;
end;
$BODY$;

/* Function 'check_iscrizioni' */
CREATE OR REPLACE FUNCTION public.check_iscrizioni()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    VOLATILE
    COST 100
AS $BODY$
declare
    new_lecture  programmazione_lezioni;
    lecture      programmazione_lezioni;
    prog_corso   programmazione_corso;
    num_iscritti integer;
begin
    if (select id_corso from programmazione_corso where id = new.id_programmazione_corso) in
       (select id_corso
        from iscrizioni_corso ic
                 join programmazione_corso pc on ic.id_programmazione_corso = pc.id
        where ic.id_studente = new.id_studente) then
        RAISE EXCEPTION 'there is already an enrollment to this course';
    end if;

    for new_lecture in
        (select pl.*
         from programmazione_lezioni pl
         where pl.id_programmazione_corso = new.id_programmazione_corso)
        loop
            for lecture in
                (select pl.*
                 from programmazione_lezioni pl
                          join programmazione_corso p on p.id = pl.id_programmazione_corso
                          join iscrizioni_corso i on p.id = i.id_programmazione_corso
                 where i.id_studente = new.id_studente)
                loop
                    if new_lecture.data = lecture.data and new_lecture.orario_fine > new_lecture.orario_inizio then
                        RAISE EXCEPTION 'there is another lesson with overlapping timetable';
                    end if;
                end loop;
        end loop;

    select pc.*
    into prog_corso
    from programmazione_corso pc
    where pc.id = new.id_programmazione_corso;

    select coalesce(count(*), 0)
    into num_iscritti
    from iscrizioni_corso
    where new.id_programmazione_corso = id_programmazione_corso
      and "inPresenza";

    if (prog_corso.limite_iscrizioni is not null and num_iscritti >= prog_corso.limite_iscrizioni) or
        num_iscritti >= (select min(a.capienza)
                        from programmazione_lezioni pl
                                 join aule a on pl.id_aula = a.id
                        where pl.id_programmazione_corso = new.id_programmazione_corso) then
        raise exception 'the course is full';
    end if;

    return new;
end;
$BODY$;

/* Function 'check_limite_iscrizioni' */
CREATE FUNCTION public.check_limite_iscrizioni()
    RETURNS trigger
    LANGUAGE 'plpgsql'
     NOT LEAKPROOF
AS $BODY$
declare
    prog_corso programmazione_corso;
begin
    select pc.*
    into prog_corso
    from programmazione_corso pc
    where pc.id = new.id_programmazione_corso;

    if prog_corso.modalità = 'duale' or prog_corso.modalità = 'presenza' and prog_corso.limite_iscrizioni is not null then
        if (select a.capienza from aule a where a.id = new.id_aula) < prog_corso.limite_iscrizioni then
            raise exception 'classroom too small for the registration limit of the course';
        end if;
    end if;

    return new;
end;
$BODY$;

/* Trigger 'trigger_check_like' */
CREATE TRIGGER trigger_check_like
    BEFORE INSERT OR UPDATE
    ON public.like_domanda
    FOR EACH ROW
    EXECUTE FUNCTION public.check_like();

/* Trigger 'trigger_check_risposte' */
CREATE TRIGGER trigger_check_risposte
    BEFORE INSERT OR UPDATE
    ON public.domande_corso
    FOR EACH ROW
    EXECUTE FUNCTION public.check_risposte();

/* Trigger 'trigger_check_iscrizioni' */
CREATE TRIGGER trigger_check_iscrizioni
    BEFORE INSERT OR UPDATE 
    ON public.iscrizioni_corso
    FOR EACH ROW
    EXECUTE FUNCTION public.check_iscrizioni();

/* Trigger 'check_aule' */
CREATE TRIGGER check_aule
    BEFORE INSERT OR UPDATE 
    ON public.programmazione_lezioni
    FOR EACH ROW
    EXECUTE FUNCTION public.check_limite_iscrizioni();
