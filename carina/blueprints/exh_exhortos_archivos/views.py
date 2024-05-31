"""
Exh Exhortos Archivos, vistas
"""

import json
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from carina.blueprints.bitacoras.models import Bitacora
from carina.blueprints.modulos.models import Modulo
from carina.blueprints.permisos.models import Permiso
from carina.blueprints.usuarios.decorators import permission_required
from carina.blueprints.exh_exhortos_archivos.models import ExhExhortoArchivo
from carina.blueprints.exh_exhortos.models import ExhExhorto
from carina.blueprints.exh_exhortos_archivos.forms import ExhExhortoArchivoEditForm, ExhExhortoArchivoNewForm

MODULO = "EXH EXHORTOS ARCHIVOS"

exh_exhortos_archivos = Blueprint("exh_exhortos_archivos", __name__, template_folder="templates")


@exh_exhortos_archivos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@exh_exhortos_archivos.route("/exh_exhortos_archivos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Archivos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ExhExhortoArchivo.query
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
    #             consulta = consulta.filter(ExhExhortoArchivo.clave.contains(columna_clave))
    #     except ValueError:
    #         pass
    # if "columna_descripcion" in request.form:
    #     columna_descripcion = safe_string(request.form["columna_descripcion"], save_enie=True)
    #     if columna_descripcion != "":
    #         consulta = consulta.filter(ExhExhortoArchivo.descripcion.contains(columna_descripcion))
    # Luego filtrar por columnas de otras tablas
    # if "otra_columna_descripcion" in request.form:
    #     otra_columna_descripcion = safe_string(request.form["otra_columna_descripcion"], save_enie=True)
    #     consulta = consulta.join(OtroModelo)
    #     consulta = consulta.filter(OtroModelo.rfc.contains(otra_columna_descripcion))
    # Ordenar y paginar
    registros = consulta.order_by(ExhExhortoArchivo.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "creado": resultado.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "vinculo": {
                    "nombre_archivo": resultado.nombre_archivo,
                    "url": url_for("exh_exhortos_archivos.detail", exh_exhorto_archivo_id=resultado.id),
                },
                "tipo_documento_nombre": resultado.tipo_documento_nombre,
                "estado": resultado.estado,
                "fecha_hora_recepcion": resultado.fecha_hora_recepcion.strftime("%Y-%m-%d %H:%M:%S"),
                "tamano": f"{resultado.tamano / 1024} MB",
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@exh_exhortos_archivos.route("/exh_exhortos_archivos")
def list_active():
    """Listado de Archivos activos"""
    return render_template(
        "exh_exhortos_archivos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Archivos",
        estatus="A",
    )


@exh_exhortos_archivos.route("/exh_exhortos_archivos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Archivos inactivos"""
    return render_template(
        "exh_exhortos_archivos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Archivos inactivos",
        estatus="B",
    )


@exh_exhortos_archivos.route("/exh_exhortos_archivos/<int:exh_exhorto_archivo_id>")
def detail(exh_exhorto_archivo_id):
    """Detalle de un Archivo"""
    exh_exhorto_archivo = ExhExhortoArchivo.query.get_or_404(exh_exhorto_archivo_id)
    return render_template("exh_exhortos_archivos/detail.jinja2", exh_exhorto_archivo=exh_exhorto_archivo)


@exh_exhortos_archivos.route("/exh_exhortos_archivos/nuevo_con_exhorto/<int:exh_exhorto_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_exh_exhorto(exh_exhorto_id):
    """Nuevo Archivo"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    form = ExhExhortoArchivoNewForm()
    if form.validate_on_submit():
        exh_exhorto_archivo = ExhExhortoArchivo(
            exh_exhorto=exh_exhorto,
            nombre_archivo=safe_string(form.nombre_archivo.data),
            hash_sha1="ABC-123-XXX",
            hash_sha256="ABC-123-256-999-ZZZ",
            tipo_documento=form.tipo_documento.data,
            url="www.google.com/data.pdf",
            estado="RECIBIDO",
            tamano=1024 * 3,
            fecha_hora_recepcion=datetime.now(),
        )
        exh_exhorto_archivo.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Archivo {exh_exhorto_archivo.nombre_archivo}"),
            url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("exh_exhortos_archivos/new_with_exh_exhorto.jinja2", form=form, exh_exhorto=exh_exhorto)


@exh_exhortos_archivos.route("/exh_exhortos_archivos/edicion/<int:exh_exhorto_archivo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(exh_exhorto_archivo_id):
    """Editar Archivo"""
    exh_exhorto_archivo = ExhExhortoArchivo.query.get_or_404(exh_exhorto_archivo_id)
    form = ExhExhortoArchivoEditForm()
    if form.validate_on_submit():
        exh_exhorto_archivo.nombre_archivo = safe_string(form.nombre_archivo.data)
        exh_exhorto_archivo.tipo_documento = form.tipo_documento.data
        exh_exhorto_archivo.fecha_hora_recepcion = datetime.now()
        exh_exhorto_archivo.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Archivo {exh_exhorto_archivo.nombre_archivo}"),
            url=url_for("exh_exhortos_archivos.detail", exh_exhorto_archivo_id=exh_exhorto_archivo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombre_archivo.data = exh_exhorto_archivo.nombre_archivo
    form.hash_sha1.data = exh_exhorto_archivo.hash_sha1
    form.hash_sha256.data = exh_exhorto_archivo.hash_sha256
    form.tipo_documento.data = exh_exhorto_archivo.tipo_documento
    form.url.data = exh_exhorto_archivo.url
    form.tamano.data = f"{exh_exhorto_archivo.tamano / 1024} MB"
    form.fecha_hora_recepcion.data = exh_exhorto_archivo.fecha_hora_recepcion.strftime("%Y-%m-%d %H:%M:%S")
    return render_template("exh_exhortos_archivos/edit.jinja2", form=form, exh_exhorto_archivo=exh_exhorto_archivo)


@exh_exhortos_archivos.route("/exh_exhortos_archivos/eliminar/<int:exh_exhorto_archivo_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(exh_exhorto_archivo_id):
    """Eliminar Archivo"""
    exh_exhorto_archivo = ExhExhortoArchivo.query.get_or_404(exh_exhorto_archivo_id)
    if exh_exhorto_archivo.estatus == "A":
        exh_exhorto_archivo.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Archivo {exh_exhorto_archivo.nombre_archivo}"),
            url=url_for("exh_exhortos_archivos.detail", exh_exhorto_archivo_id=exh_exhorto_archivo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("exh_exhortos_archivos.detail", exh_exhorto_archivo_id=exh_exhorto_archivo.id))


@exh_exhortos_archivos.route("/exh_exhortos_archivos/recuperar/<int:exh_exhorto_archivo_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(exh_exhorto_archivo_id):
    """Recuperar Archivo"""
    exh_exhorto_archivo = ExhExhortoArchivo.query.get_or_404(exh_exhorto_archivo_id)
    if exh_exhorto_archivo.estatus == "B":
        exh_exhorto_archivo.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Archivo {exh_exhorto_archivo.nombre_archivo}"),
            url=url_for("exh_exhortos_archivos.detail", exh_exhorto_archivo_id=exh_exhorto_archivo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("exh_exhortos_archivos.detail", exh_exhorto_archivo_id=exh_exhorto_archivo.id))
