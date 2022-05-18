from xml.etree.ElementInclude import include
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .models import Docente, Scuola, Corso, Aula

# QUESTE CLASSI SERVONO PER CONVERTIRE LE CLASSI DI MODELS.PY IN JSON OBJECT


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
