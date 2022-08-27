from xml.etree.ElementInclude import include
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .models import DomandeCorso, Utente, Docente, ProgrammazioneCorso, Scuola, Corso, Aula, IscrizioniCorso, Studente, ProgrammazioneLezioni, PresenzeLezione, RisorseCorso , DocenteCorso, LikeDomanda

# QUESTE CLASSI SERVONO PER CONVERTIRE LE CLASSI DI MODELS.PY IN JSON OBJECT


class UtenteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Utente
        include_fk = True
        include_relationships = True
        load_instance = True


class ScuolaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Scuola
        include_fk = True
        include_relationships = True
        load_instance = True


class CorsoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Corso
        include_fk = True
        include_relationships = True
        load_instance = True


class DocenteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Docente
        include_fk = True
        include_relationships = True
        load_instance = True


class AulaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Aula
        include_fk = True
        include_relationships = True
        load_instance = True


class ProgrammazioneCorsoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProgrammazioneCorso
        include_fk = True
        include_relationships = True
        load_instance = True


class ProgrammazioneLezioniSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProgrammazioneLezioni
        include_fk = True
        include_relationships = True
        load_instance = True


class IscrizioniCorsoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = IscrizioniCorso
        include_fk = True
        include_relationships = True
        load_instance = True


class StudenteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Studente
        include_fk = True
        include_relationships = True
        load_instance = True


class PresenzeLezioneSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PresenzeLezione
        include_fk = True
        include_relationships = True
        load_instance = True


class RisorseCorsoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RisorseCorso
        include_fk = True
        include_relationships = True
        load_instance = True


class DomandeCorsoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DomandeCorso
        include_fk = True
        include_relationships = True
        load_instance = True


class LikeDomandaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = LikeDomanda
        include_fk = True
        include_relationships = True
        load_instance = True