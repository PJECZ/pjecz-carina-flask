"""
Exh Exhortos Partes, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from carina.blueprints.bitacoras.models import Bitacora
from carina.blueprints.modulos.models import Modulo
from carina.blueprints.permisos.models import Permiso
from carina.blueprints.usuarios.decorators import permission_required
from carina.blueprints.exh_exhortos_partes.models import ExhExhortoParte
from carina.blueprints.exh_exhortos_partes.forms import ExhExhortoParteForm
from carina.blueprints.exh_exhortos.models import ExhExhorto


MODULO = "EXH EXHORTOS PARTES"

exh_exhortos_partes = Blueprint("exh_exhortos_partes", __name__, template_folder="templates")


@exh_exhortos_partes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@exh_exhortos_partes.route("/exh_exhortos_partes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Partes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ExhExhortoParte.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "exh_exhorto_id" in request.form:
        consulta = consulta.filter_by(exh_exhorto_id=request.form["exh_exhorto_id"])
    # if "columna_clave" in request.form:
    #     try:
    #         columna_clave = safe_clave(request.form["columna_clave"])
    #         if clave != "":
    #             consulta = consulta.filter(ExhExhortoParte.clave.contains(columna_clave))
    #     except ValueError:
    #         pass
    # if "columna_descripcion" in request.form:
    #     columna_descripcion = safe_string(request.form["columna_descripcion"], save_enie=True)
    #     if columna_descripcion != "":
    #         consulta = consulta.filter(ExhExhortoParte.descripcion.contains(columna_descripcion))
    # Luego filtrar por columnas de otras tablas
    # if "otra_columna_descripcion" in request.form:
    #     otra_columna_descripcion = safe_string(request.form["otra_columna_descripcion"], save_enie=True)
    #     consulta = consulta.join(OtroModelo)
    #     consulta = consulta.filter(OtroModelo.rfc.contains(otra_columna_descripcion))
    # Ordenar y paginar
    registros = consulta.order_by(ExhExhortoParte.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "url": url_for("exh_exhortos_partes.detail", exh_exhorto_parte_id=resultado.id),
                    "nombre": resultado.nombre_completo,
                },
                "nombre": resultado.nombre,
                "apellido_paterno": resultado.apellido_paterno,
                "apellido_materno": resultado.apellido_materno,
                "genero": resultado.genero,
                "es_persona_moral": resultado.es_persona_moral,
                "tipo_parte": resultado.tipo_parte,
                "tipo_parte_nombre": resultado.tipo_parte_nombre,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@exh_exhortos_partes.route("/exh_exhortos_partes")
def list_active():
    """Listado de Partes activos"""
    return render_template(
        "exh_exhortos_partes/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Partes",
        estatus="A",
    )


@exh_exhortos_partes.route("/exh_exhortos_partes/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Partes inactivos"""
    return render_template(
        "exh_exhortos_partes/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Partes inactivos",
        estatus="B",
    )


@exh_exhortos_partes.route("/exh_exhortos_partes/nuevo_con_exhorto/<int:exh_exhorto_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_exh_exhorto(exh_exhorto_id):
    """Nueva Parte"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    form = ExhExhortoParteForm()
    if form.validate_on_submit():
        es_persona_moral = form.es_persona_moral.data
        pedir_tipo_parte_nombre = False
        tipo_parte_nombre = None
        if form.tipo_parte.data == 0:
            pedir_tipo_parte_nombre = True
            tipo_parte_nombre = form.tipo_parte_nombre.data
        if pedir_tipo_parte_nombre == True and tipo_parte_nombre == "":
            flash("Debe especificar un 'Tipo Parte Nombre'", "warning")
        else:
            if es_persona_moral:
                exh_exhorto_parte = ExhExhortoParte(
                    exh_exhorto=exh_exhorto,
                    es_persona_moral=es_persona_moral,
                    nombre=safe_string(form.nombre.data),
                    tipo_parte=form.tipo_parte.data,
                    tipo_parte_nombre=tipo_parte_nombre,
                )
            exh_exhorto_parte = ExhExhortoParte(
                exh_exhorto=exh_exhorto,
                es_persona_moral=es_persona_moral,
                nombre=safe_string(form.nombre.data),
                apellido_paterno=safe_string(form.apellido_paterno.data),
                apellido_materno=safe_string(form.apellido_materno.data),
                genero=safe_string(form.genero.data),
                tipo_parte=form.tipo_parte.data,
                tipo_parte_nombre=tipo_parte_nombre,
            )
            exh_exhorto_parte.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Parte {exh_exhorto_parte.nombre}"),
                url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("exh_exhortos_partes/new_with_exh_exhorto.jinja2", form=form, exh_exhorto=exh_exhorto)


@exh_exhortos_partes.route("/exh_exhortos_partes/<int:exh_exhorto_parte_id>")
def detail(exh_exhorto_parte_id):
    """Detalle de un Parte"""
    exh_exhorto_parte = ExhExhortoParte.query.get_or_404(exh_exhorto_parte_id)
    return render_template("exh_exhortos_partes/detail.jinja2", exh_exhorto_parte=exh_exhorto_parte)
