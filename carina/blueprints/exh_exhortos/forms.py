"""
Exh Exhortos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired, Length, Optional

from carina.blueprints.materias.models import Materia
from carina.blueprints.exh_areas.models import ExhArea

REMITENTES = [
    ("INTERNO", "INTERNO"),
    ("EXTERNO", "EXTERNO"),
]


def materias_opciones():
    """Materias: opciones para select"""
    return Materia.query.filter_by(estatus="A").order_by(Materia.clave).all()


class ExhExhortoNewForm(FlaskForm):
    """Formulario New Exhorto"""

    exhorto_origen_id = StringField("Exhorto Origen ID", validators=[DataRequired(), Length(max=128)])
    estado_destino = SelectField("Estado Destino", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    municipio_destino = SelectField(
        "Municipio Destino", choices=None, validate_choice=False, validators=[DataRequired()]
    )  # Las opciones se agregan con JS
    materia = SelectField("Materia", coerce=int, validators=[DataRequired()])
    estado_origen = SelectField("Estado Origen", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    municipio_origen = SelectField(
        "Municipio Origen", choices=None, validate_choice=False, validators=[DataRequired()]
    )  # Las opciones se agregan con JS
    juzgado_origen_id = StringField("Juzgado Origen Clave", validators=[Optional(), Length(max=64)])
    juzgado_origen_nombre = StringField("Juzgado Origen Nombre", validators=[DataRequired(), Length(max=256)])
    numero_expediente_origen = StringField("Número de Expediente Origen", validators=[DataRequired(), Length(max=256)])
    numero_oficio_origen = StringField("Número de Oficio Origen", validators=[Optional(), Length(max=256)])
    tipo_juicio_asunto_delitos = StringField("Tipo de Jucio Asunto Delitos", validators=[DataRequired(), Length(max=256)])
    juez_exhortante = StringField("Juez Exhortante", validators=[Optional(), Length(max=256)])
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    dias_responder = IntegerField("Días Responder", validators=[DataRequired()])
    fecha_origen = StringField("Fecha Origen", validators=[Optional()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=1024)])
    remitente = RadioField("Remitente", validators=[DataRequired()], choices=REMITENTES, coerce=str)
    crear = SubmitField("Crear")

    def __init__(self, *args, **kwargs):
        """Inicializar y cargar opciones para materias"""
        super().__init__(*args, **kwargs)
        self.materia.choices = [(m.id, m.nombre) for m in Materia.query.filter_by(estatus="A").order_by(Materia.clave).all()]


class ExhExhortoEditForm(FlaskForm):
    """Formulario Edit Exhorto"""

    exhorto_origen_id = StringField("Exhorto Origen ID", validators=[DataRequired(), Length(max=128)])
    estado_destino = SelectField("Estado Destino", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    municipio_destino = SelectField(
        "Municipio Destino", choices=None, validate_choice=False, validators=[DataRequired()]
    )  # Las opciones se agregan con JS
    materia = SelectField("Materia", coerce=int, validators=[DataRequired()])
    estado_origen = SelectField("Estado Origen", choices=None, validate_choice=False)  # Las opciones se agregan con JS
    municipio_origen = SelectField(
        "Municipio Origen", choices=None, validate_choice=False, validators=[DataRequired()]
    )  # Las opciones se agregan con JS
    juzgado_origen_id = StringField("Juzgado Origen Clave", validators=[Optional(), Length(max=64)])
    juzgado_origen_nombre = StringField("Juzgado Origen Nombre", validators=[DataRequired(), Length(max=256)])
    numero_expediente_origen = StringField("Número de Expediente Origen", validators=[DataRequired(), Length(max=256)])
    numero_oficio_origen = StringField("Número de Oficio Origen", validators=[Optional(), Length(max=256)])
    tipo_juicio_asunto_delitos = StringField("Tipo de Jucio Asunto Delitos", validators=[DataRequired(), Length(max=256)])
    juez_exhortante = StringField("Juez Exhortante", validators=[Optional(), Length(max=256)])
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    dias_responder = IntegerField("Días Responder", validators=[DataRequired()])
    fecha_origen = StringField("Fecha Origen", validators=[Optional()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=1024)])
    remitente = RadioField("Remitente", validators=[DataRequired()], choices=REMITENTES, coerce=str)
    exh_area = SelectField("Área", coerce=int, validators=[DataRequired()])
    guardar = SubmitField("Guardar")

    def __init__(self, *args, **kwargs):
        """Inicializar y cargar opciones para materias"""
        super().__init__(*args, **kwargs)
        self.materia.choices = [(m.id, m.nombre) for m in Materia.query.filter_by(estatus="A").order_by(Materia.clave).all()]
        self.exh_area.choices = [
            (m.id, m.clave + " - " + m.nombre) for m in ExhArea.query.filter_by(estatus="A").order_by(ExhArea.clave).all()
        ]
