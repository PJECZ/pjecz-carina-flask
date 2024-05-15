"""
Exh Externos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class ExhExternoForm(FlaskForm):
    """Formulario ExhExterno"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    api_key = StringField("API Key", validators=[Optional(), Length(max=128)])
    endpoint_consultar_materias = StringField("Materias", validators=[Optional(), Length(max=256)])
    endpoint_recibir_exhorto = StringField("Recibir Exhorto", validators=[Optional(), Length(max=256)])
    endpoint_recibir_exhorto_archivo = StringField("Recibir Exhorto Archivo", validators=[Optional(), Length(max=256)])
    endpoint_consultar_exhorto = StringField("Consultar Exhorto", validators=[Optional(), Length(max=256)])
    endpoint_recibir_respuesta_exhorto = StringField("Recibir Respuesta Exhorto", validators=[Optional(), Length(max=256)])
    endpoint_recibir_respuesta_exhorto_archivo = StringField(
        "Recibir Respuesta Exhorto Archivo", validators=[Optional(), Length(max=256)]
    )
    endpoint_actualizar_exhorto = StringField("Actualizar Exhorto", validators=[Optional(), Length(max=256)])
    endpoint_recibir_promocion = StringField("Recibir Promoción", validators=[Optional(), Length(max=256)])
    endpoint_recibir_promocion_archivo = StringField("Recibir Promoción Archivo", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")