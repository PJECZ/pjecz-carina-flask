"""
Exh Exhortos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from carina.blueprints.materias.models import Materia


def materias_opciones():
    """Materias: opciones para select"""
    return Materia.query.filter_by(estatus="A").order_by(Materia.clave).all()


class ExhExhortoNewForm(FlaskForm):
    """Formulario ExhExhortoNew"""

    exhorto_origen_id = StringField("Exhorto Origen ID", validators=[DataRequired(), Length(max=128)])
    municipio_destino = IntegerField("Municipio Destino", validators=[DataRequired()])
    materia = SelectField("Materia", coerce=int, validators=[DataRequired()])
    municipio_origen = IntegerField("Municipio Origen ID", validators=[DataRequired(), Length(max=256)])
    juzgado_origen = StringField("Juzgado Origen Clave", validators=[Optional(), Length(max=64)])
    juzgado_origen_nombre = StringField("Juzgado Origen Nombre", validators=[DataRequired(), Length(max=256)])
    numero_expediente_origen = StringField("Número de Expediente Origen", validators=[DataRequired(), Length(max=256)])
    numero_oficio_origen = StringField("Número de Expediente Origen", validators=[Optional(), Length(max=256)])
    tipo_juicio_asunto_delitos = StringField("Tipo de Jucio Asunto Delitos", validators=[DataRequired(), Length(max=256)])
    juez_exhortante = StringField("Juez Exhortante", validators=[Optional(), Length(max=256)])
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=1024)])
    crear = SubmitField("Crear")

    def __init__(self, *args, **kwargs):
        """Inicializar y cargar opciones para materias"""
        super().__init__(*args, **kwargs)
        self.materia.choices = [(m.id, m.nombre) for m in Materia.query.filter_by(estatus="A").order_by(Materia.clave).all()]
