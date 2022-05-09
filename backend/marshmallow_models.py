from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from .models import Docente, Scuola, Corso

# QUESTE CLASSI SERVONO PER CONVERTIRE LE CLASSI DI MODELS.PY IN JSON OBJECT


class ScuolaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Scuola
        include_relationships = True
        load_instance = True


class CorsoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Corso
        include_relationships = True
        load_instance = True

class DocenteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Docente
        include_relationships = True
        load_instance = True
