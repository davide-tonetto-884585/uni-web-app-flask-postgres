from . import Base


class Utente(Base):
    __table__ = Base.metadata.tables['utenti']


class Studente(Base):
    __table__ = Base.metadata.tables['studenti']


class Docente(Base):
    __table__ = Base.metadata.tables['docenti']


class Amministratore(Base):
    __table__ = Base.metadata.tables['amministratori']


class Scuola(Base):
    __table__ = Base.metadata.tables['scuole']
    

class Corso(Base):
    __table__ = Base.metadata.tables['corsi']


class ProgrammazioneCorso(Base):
    __table__ = Base.metadata.tables['programmazione_corso']

    
class DocenteCorso(Base):
    __table__ = Base.metadata.tables['docenti_corso']
    

class Aula(Base):
    __table__ = Base.metadata.tables['aule']


class IscrizioniCorso(Base):
    __table__ = Base.metadata.tables['iscrizioni_corso']


class ProgrammazioneLezioni(Base):
    __table__ = Base.metadata.tables['programmazione_lezioni']


class PresenzeLezione(Base):
    __table__ = Base.metadata.tables['presenze_lezione']

class RisorseCorso(Base):
    __table__ = Base.metadata.tables['risorse_corso']