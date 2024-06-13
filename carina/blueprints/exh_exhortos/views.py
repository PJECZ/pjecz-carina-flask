"""
Exh Exhortos, vistas
"""

import json
import uuid
from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from carina.blueprints.bitacoras.models import Bitacora
from carina.blueprints.estados.models import Estado
from carina.blueprints.exh_exhortos.forms import ExhExhortoEditForm, ExhExhortoNewForm
from carina.blueprints.exh_exhortos.models import ExhExhorto
from carina.blueprints.modulos.models import Modulo
from carina.blueprints.municipios.models import Municipio
from carina.blueprints.permisos.models import Permiso
from carina.blueprints.usuarios.decorators import permission_required
from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string

MODULO = "EXH EXHORTOS"

exh_exhortos = Blueprint("exh_exhortos", __name__, template_folder="templates")


@exh_exhortos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@exh_exhortos.route("/exh_exhortos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Exhortos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ExhExhorto.query
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
    #             consulta = consulta.filter(ExhExhorto.clave.contains(columna_clave))
    #     except ValueError:
    #         pass
    # if "columna_descripcion" in request.form:
    #     columna_descripcion = safe_string(request.form["columna_descripcion"], save_enie=True)
    #     if columna_descripcion != "":
    #         consulta = consulta.filter(ExhExhorto.descripcion.contains(columna_descripcion))
    # Luego filtrar por columnas de otras tablas
    # if "otra_columna_descripcion" in request.form:
    #     otra_columna_descripcion = safe_string(request.form["otra_columna_descripcion"], save_enie=True)
    #     consulta = consulta.join(OtroModelo)
    #     consulta = consulta.filter(OtroModelo.rfc.contains(otra_columna_descripcion))
    # Ordenar y paginar
    registros = consulta.order_by(ExhExhorto.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "creado": resultado.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "detalle": {
                    "uuid": resultado.exhorto_origen_id,
                    "url": url_for("exh_exhortos.detail", exh_exhorto_id=resultado.id),
                },
                "juzgado_origen": {
                    "clave": resultado.juzgado_origen_id,
                    "nombre": resultado.juzgado_origen_nombre,
                },
                "numero_expediente_origen": resultado.numero_expediente_origen,
                "estado_origen": resultado.municipio_origen.estado.nombre,
                "remitente": resultado.remitente,
                "estado": resultado.estado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@exh_exhortos.route("/exh_exhortos")
def list_active():
    """Listado de Exhortos activos"""
    return render_template(
        "exh_exhortos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Exhortos",
        estatus="A",
    )


@exh_exhortos.route("/exh_exhortos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Exhortos inactivos"""
    return render_template(
        "exh_exhortos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Exhortos inactivos",
        estatus="B",
    )


@exh_exhortos.route("/exh_exhortos/<int:exh_exhorto_id>")
def detail(exh_exhorto_id):
    """Detalle de un Exhorto"""
    # Consultar exh_exhorto
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)

    # Consultar municipio_destino_id, porque no es una clave foránea
    municipio_destino = Municipio.query.filter_by(id=exh_exhorto.municipio_destino_id).first()

    # Entregar
    return render_template(
        "exh_exhortos/detail.jinja2",
        exh_exhorto=exh_exhorto,
        municipio_destino=municipio_destino,
    )


@exh_exhortos.route("/exh_exhortos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Exhorto"""
    form = ExhExhortoNewForm()
    if form.validate_on_submit():
        exh_exhorto = ExhExhorto(
            exhorto_origen_id=form.exhorto_origen_id.data,
            municipio_destino_id=form.municipio_destino.data,
            materia_id=form.materia.data,
            municipio_origen_id=form.municipio_origen.data,
            juzgado_origen_id=safe_string(form.juzgado_origen_id.data),
            juzgado_origen_nombre=safe_string(form.juzgado_origen_nombre.data),
            numero_expediente_origen=safe_string(form.numero_expediente_origen.data),
            numero_oficio_origen=safe_string(form.numero_oficio_origen.data),
            tipo_juicio_asunto_delitos=safe_string(form.tipo_juicio_asunto_delitos.data),
            juez_exhortante=safe_string(form.juez_exhortante.data),
            fojas=form.fojas.data,
            dias_responder=form.dias_responder.data,
            tipo_diligenciacion_nombre=form.tipo_diligenciacion_nombre.data,
            fecha_origen=form.fecha_origen.data,
            observaciones=safe_message(form.observaciones.data, default_output_str=None),
            # Datos por defecto
            exh_area_id=1,  # valor: NO DEFINIDO
            autoridad_id=342,  # valor por defecto: ND - NO DEFINIDO
            numero_exhorto="",
            remitente="INTERNO",
            estado="PENDIENTE",
        )
        exh_exhorto.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Exhorto {exh_exhorto.exhorto_origen_id}"),
            url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.exhorto_origen_id.data = str(uuid.uuid4())  # Elaborar un UUID para mostrar READ ONLY
    form.estado_origen.data = "COAHUILA DE ZARAGOZA"
    form.estado.data = "PENDIENTE"
    form.fecha_origen.data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Consultar el estado de origen por medio de la clave INEGI en las variables de entorno ESTADO_CLAVE
    estado_origen_id = Estado.query.filter_by(clave=current_app.config["ESTADO_CLAVE"]).first().id
    # Entregar
    return render_template("exh_exhortos/new.jinja2", form=form, estado_origen_id=estado_origen_id)


@exh_exhortos.route("/exh_exhortos/edicion/<int:exh_exhorto_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(exh_exhorto_id):
    """Editar Exhorto"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    form = ExhExhortoEditForm()
    if form.validate_on_submit():
        exh_exhorto.municipio_destino_id = form.municipio_destino.data
        exh_exhorto.materia_id = form.materia.data
        exh_exhorto.municipio_origen_id = form.municipio_origen.data
        exh_exhorto.juzgado_origen_id = safe_string(form.juzgado_origen_id.data)
        exh_exhorto.juzgado_origen_nombre = safe_string(form.juzgado_origen_nombre.data)
        exh_exhorto.numero_expediente_origen = safe_string(form.numero_expediente_origen.data)
        exh_exhorto.numero_oficio_origen = safe_string(form.numero_oficio_origen.data)
        exh_exhorto.tipo_juicio_asunto_delitos = safe_string(form.tipo_juicio_asunto_delitos.data)
        exh_exhorto.juez_exhortante = safe_string(form.juez_exhortante.data)
        exh_exhorto.fojas = form.fojas.data
        exh_exhorto.dias_responder = form.dias_responder.data
        exh_exhorto.tipo_diligenciacion_nombre = safe_string(form.tipo_diligenciacion_nombre.data)
        exh_exhorto.fecha_origen = form.fecha_origen.data
        exh_exhorto.observaciones = safe_message(form.observaciones.data, default_output_str=None)
        exh_exhorto.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Exhorto {exh_exhorto.exhorto_origen_id}"),
            url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.exhorto_origen_id.data = exh_exhorto.exhorto_origen_id
    form.materia.data = exh_exhorto.materia.id
    form.juzgado_origen_id.data = exh_exhorto.juzgado_origen_id
    form.juzgado_origen_nombre.data = exh_exhorto.juzgado_origen_nombre
    form.numero_expediente_origen.data = exh_exhorto.numero_expediente_origen
    form.numero_oficio_origen.data = exh_exhorto.numero_oficio_origen
    form.tipo_juicio_asunto_delitos.data = exh_exhorto.tipo_juicio_asunto_delitos
    form.juez_exhortante.data = exh_exhorto.juez_exhortante
    form.fojas.data = exh_exhorto.fojas
    form.dias_responder.data = exh_exhorto.dias_responder
    form.tipo_diligenciacion_nombre.data = exh_exhorto.tipo_diligenciacion_nombre
    form.fecha_origen.data = exh_exhorto.fecha_origen
    form.observaciones.data = exh_exhorto.observaciones
    form.remitente.data = exh_exhorto.remitente
    form.exh_area.data = exh_exhorto.exh_area.id
    form.folio_seguimiento.data = exh_exhorto.folio_seguimiento
    form.numero_exhorto.data = exh_exhorto.numero_exhorto
    form.estado.data = exh_exhorto.estado  # Read only
    municipio_destino = Municipio.query.filter_by(id=exh_exhorto.municipio_destino_id).first()
    # Entregar
    return render_template("exh_exhortos/edit.jinja2", form=form, exh_exhorto=exh_exhorto, municipio_destino=municipio_destino)


@exh_exhortos.route("/exh_exhortos/eliminar/<int:exh_exhorto_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(exh_exhorto_id):
    """Eliminar Exhorto"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    if exh_exhorto.estatus == "A":
        exh_exhorto.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Exhorto {exh_exhorto.exhorto_origen_id}"),
            url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id))


@exh_exhortos.route("/exh_exhortos/recuperar/<int:exh_exhorto_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(exh_exhorto_id):
    """Recuperar Exhorto"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    if exh_exhorto.estatus == "B":
        exh_exhorto.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Exhorto {exh_exhorto.exhorto_origen_id}"),
            url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id))


@exh_exhortos.route("/exh_exhortos/cancelar/<int:exh_exhorto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel(exh_exhorto_id):
    """Cancelar Exhorto"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    if exh_exhorto.estado == "PENDIENTE":
        exh_exhorto.estado = "CANCELADO"
        exh_exhorto.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Exhorto CANCELADO {exh_exhorto.exhorto_origen_id}"),
            url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id))


@exh_exhortos.route("/exh_exhortos/enviar/<int:exh_exhorto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def enviar(exh_exhorto_id):
    """Envíar Exhorto"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    if exh_exhorto.estado == "PENDIENTE":
        exh_exhorto.estado = "POR ENVIAR"
        exh_exhorto.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Exhorto POR ENVIAR {exh_exhorto.exhorto_origen_id}"),
            url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id))
