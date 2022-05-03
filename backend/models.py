from . import Base

class Utente(Base):
    __table__ = Base.metadata.tables['utenti']
    
class Studente(Base):
    __table__ = Base.metadata.tables['studenti']

class Docente(Base):
    __table__ = Base.metadata.tables['docenti']
    
class Amministratore(Base):
    __table__ = Base.metadata.tables['amministratori']