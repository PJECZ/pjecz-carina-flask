"""
Exh Externos, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_string, safe_message

from carina.blueprints.bitacoras.models import Bitacora
from carina.blueprints.modulos.models import Modulo
from carina.blueprints.permisos.models import Permiso
from carina.blueprints.usuarios.decorators import permission_required
from carina.blueprints.exh_externos.models import ExhExterno
from carina.blueprints.exh_externos.forms import ExhExternoForm

MODULO = "EXH EXTERNOS"

exh_externos = Blueprint("exh_externos", __name__, template_folder="templates")


@exh_externos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@exh_externos.route("/exh_externos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Externos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ExhExterno.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    # if "columna_id" in request.form:
    #     consulta = consulta.filter_by(columna_id=request.form["columna_id"])
    # if "columna_clave" in request.form:
    #     try:
    #         columna_clave = safe_clave(request.form["columna_clave"])
    #         if clave != "":
    #             consulta = consulta.filter(ExhExterno.clave.contains(columna_clave))
    #     except ValueError:
    #         pass
    # if "columna_descripcion" in request.form:
    #     columna_descripcion = safe_string(request.form["columna_descripcion"], save_enie=True)
    #     if columna_descripcion != "":
    #         consulta = consulta.filter(ExhExterno.descripcion.contains(columna_descripcion))
    # Luego filtrar por columnas de otras tablas
    # if "otra_columna_descripcion" in request.form:
    #     otra_columna_descripcion = safe_string(request.form["otra_columna_descripcion"], save_enie=True)
    #     consulta = consulta.join(OtroModelo)
    #     consulta = consulta.filter(OtroModelo.rfc.contains(otra_columna_descripcion))
    # Ordenar y paginar
    registros = consulta.order_by(ExhExterno.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("exh_externos.detail", exh_externo_id=resultado.id),
                },
                "api_key": "Sí" if resultado.api_key != "" else "",
                "endpoint_consultar_materias": "Sí" if resultado.endpoint_consultar_materias != "" else "",
                "endpoint_recibir_exhorto": "Sí" if resultado.endpoint_recibir_exhorto != "" else "",
                "endpoint_recibir_exhorto_archivo": "Sí" if resultado.endpoint_recibir_exhorto_archivo != "" else "",
                "endpoint_consultar_exhorto": "Sí" if resultado.endpoint_consultar_exhorto != "" else "",
                "endpoint_recibir_respuesta_exhorto": "Sí" if resultado.endpoint_recibir_respuesta_exhorto != "" else "",
                "endpoint_recibir_respuesta_exhorto_archivo": (
                    "Sí" if resultado.endpoint_recibir_respuesta_exhorto_archivo != "" else ""
                ),
                "endpoint_actualizar_exhorto": "Sí" if resultado.endpoint_actualizar_exhorto != "" else "",
                "endpoint_recibir_promocion": "Sí" if resultado.endpoint_recibir_promocion != "" else "",
                "endpoint_recibir_promocion_archivo": "Sí" if resultado.endpoint_recibir_promocion_archivo != "" else "",
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@exh_externos.route("/exh_externos")
def list_active():
    """Listado de Externos activos"""
    return render_template(
        "exh_externos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Externos",
        estatus="A",
    )


@exh_externos.route("/exh_externos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Externos inactivos"""
    return render_template(
        "exh_externos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Externos inactivos",
        estatus="B",
    )


@exh_externos.route("/exh_externos/<int:exh_externo_id>")
def detail(exh_externo_id):
    """Detalle de un Externo"""
    exh_externo = ExhExterno.query.get_or_404(exh_externo_id)
    return render_template("exh_externos/detail.jinja2", exh_externo=exh_externo)


@exh_externos.route("/exh_externos/edicion/<int:exh_externo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(exh_externo_id):
    """Editar Externo"""
    exh_externo = ExhExterno.query.get_or_404(exh_externo_id)
    form = ExhExternoForm()
    if form.validate_on_submit():
        exh_externo.clave = safe_clave(form.clave.data)
        exh_externo.descripcion = safe_string(form.descripcion.data)
        exh_externo.api_key = safe_string(form.api_key.data)
        exh_externo.endpoint_consultar_materias = safe_message(form.endpoint_consultar_materias.data)
        exh_externo.endpoint_recibir_exhorto = safe_message(form.endpoint_recibir_exhorto.data)
        exh_externo.endpoint_recibir_exhorto_archivo = safe_message(form.endpoint_recibir_exhorto_archivo.data)
        exh_externo.endpoint_consultar_exhorto = safe_message(form.endpoint_consultar_exhorto.data)
        exh_externo.endpoint_recibir_respuesta_exhorto = safe_message(form.endpoint_recibir_respuesta_exhorto.data)
        exh_externo.endpoint_recibir_respuesta_exhorto_archivo = safe_message(
            form.endpoint_recibir_respuesta_exhorto_archivo.data
        )
        exh_externo.endpoint_actualizar_exhorto = safe_message(form.endpoint_actualizar_exhorto.data)
        exh_externo.endpoint_recibir_promocion = safe_message(form.endpoint_recibir_promocion.data)
        exh_externo.endpoint_recibir_promocion_archivo = safe_message(form.endpoint_recibir_promocion_archivo.data)
        exh_externo.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Externo {exh_externo.clave}"),
            url=url_for("exh_externos.detail", exh_externo_id=exh_externo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Cargar valor almacenado de campos en el formulario
    form.clave.data = exh_externo.clave
    form.descripcion.data = exh_externo.descripcion
    form.api_key.data = exh_externo.api_key
    form.endpoint_consultar_materias.data = exh_externo.endpoint_consultar_materias
    form.endpoint_recibir_exhorto.data = exh_externo.endpoint_recibir_exhorto
    form.endpoint_recibir_exhorto_archivo.data = exh_externo.endpoint_recibir_exhorto_archivo
    form.endpoint_consultar_exhorto.data = exh_externo.endpoint_consultar_exhorto
    form.endpoint_recibir_respuesta_exhorto.data = exh_externo.endpoint_recibir_respuesta_exhorto
    form.endpoint_recibir_respuesta_exhorto_archivo.data = exh_externo.endpoint_recibir_respuesta_exhorto_archivo
    form.endpoint_actualizar_exhorto.data = exh_externo.endpoint_actualizar_exhorto
    form.endpoint_recibir_promocion.data = exh_externo.endpoint_recibir_promocion
    form.endpoint_recibir_promocion_archivo.data = exh_externo.endpoint_recibir_promocion_archivo
    # Entregar el template
    return render_template("exh_externos/edit.jinja2", form=form, exh_externo=exh_externo)
