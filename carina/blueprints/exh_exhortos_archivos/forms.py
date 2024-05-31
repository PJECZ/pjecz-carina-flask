"""
Exh Exhorto Archivo, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from carina.blueprints.exh_exhortos_archivos.models import ExhExhortoArchivo


class ExhExhortoArchivoNewForm(FlaskForm):
    """Formulario ExhExhortoArchivoNew"""

    nombre_archivo = StringField("Nombre del Archivo", validators=[DataRequired(), Length(max=256)])
    tipo_documento = SelectField(
        "Tipo", coerce=int, choices=ExhExhortoArchivo.TIPOS_DOCUMENTOS.items(), validators=[DataRequired()]
    )
    crear = SubmitField("Crear")


class ExhExhortoArchivoEditForm(FlaskForm):
    """Formulario para Editar"""

    nombre_archivo = StringField("Nombre del Archivo", validators=[DataRequired(), Length(max=256)])
    hash_sha1 = StringField("Hash SHA-1")
    hash_sha256 = StringField("Hash SHA-256")
    tipo_documento = SelectField(
        "Tipo", coerce=int, choices=ExhExhortoArchivo.TIPOS_DOCUMENTOS.items(), validators=[DataRequired()]
    )
    url = StringField("Url")
    tamano = StringField("Tamaño")
    fecha_hora_recepcion = StringField("Fecha y hora de recepción")
    guardar = SubmitField("Guardar")
