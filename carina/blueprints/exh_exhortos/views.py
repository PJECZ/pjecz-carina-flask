"""
Exh Exhortos, vistas
"""

import json
import uuid
from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from carina.blueprints.autoridades.models import Autoridad
from carina.blueprints.bitacoras.models import Bitacora
from carina.blueprints.estados.models import Estado
from carina.blueprints.exh_exhortos.forms import ExhExhortoEditForm, ExhExhortoNewForm, ExhExhortoTransferForm
from carina.blueprints.exh_exhortos.models import ExhExhorto
from carina.blueprints.modulos.models import Modulo
from carina.blueprints.municipios.models import Municipio
from carina.blueprints.permisos.models import Permiso
from carina.blueprints.usuarios.decorators import permission_required
from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_message, safe_string

from carina.blueprints.exh_exhortos_partes.models import ExhExhortoParte
from carina.blueprints.exh_exhortos_archivos.models import ExhExhortoArchivo

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
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form["estado"])
    if "juzgado_origen_clave" in request.form:
        juzgado_origen_clave = safe_clave(request.form["juzgado_origen_clave"])
        if juzgado_origen_clave != "":
            consulta = consulta.filter(ExhExhorto.juzgado_origen_id.contains(juzgado_origen_clave))
    # Buscar en otras tablas
    if "estado_origen" in request.form:
        estado_origen = safe_string(request.form["estado_origen"], save_enie=True)
        if estado_origen != "":
            consulta = consulta.join(Municipio).join(Estado)
            consulta = consulta.filter(Estado.nombre.contains(estado_origen))
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
                    "id": resultado.id,
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
        estados=ExhExhorto.ESTADOS,
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
        estados=ExhExhorto.ESTADOS,
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
        juzgado_origen = Autoridad.query.filter_by(id=form.juzgado_origen.data).filter_by(estatus="A").first()
        if juzgado_origen is None:
            flash("El juzgado de origen no es válido", "warning")
        else:
            exh_exhorto = ExhExhorto(
                exhorto_origen_id=form.exhorto_origen_id.data,
                municipio_destino_id=form.municipio_destino.data,
                materia_id=form.materia.data,
                municipio_origen_id=form.municipio_origen.data,
                juzgado_origen_id=safe_string(juzgado_origen.clave),
                juzgado_origen_nombre=safe_string(juzgado_origen.descripcion, save_enie=True),
                numero_expediente_origen=safe_string(form.numero_expediente_origen.data),
                numero_oficio_origen=safe_string(form.numero_oficio_origen.data),
                tipo_juicio_asunto_delitos=safe_string(form.tipo_juicio_asunto_delitos.data),
                juez_exhortante=safe_string(form.juez_exhortante.data, save_enie=True),
                fojas=form.fojas.data,
                dias_responder=form.dias_responder.data,
                tipo_diligenciacion_nombre=safe_string(form.tipo_diligenciacion_nombre.data, save_enie=True),
                fecha_origen=form.fecha_origen.data,
                observaciones=safe_string(form.observaciones.data, save_enie=True, max_len=1024),
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
        juzgado_origen = Autoridad.query.filter_by(id=form.juzgado_origen.data).filter_by(estatus="A").first()
        if juzgado_origen is None:
            flash("El juzgado de origen no es válido", "warning")
        else:
            exh_exhorto.municipio_destino_id = form.municipio_destino.data
            exh_exhorto.materia_id = form.materia.data
            exh_exhorto.municipio_origen_id = form.municipio_origen.data
            exh_exhorto.juzgado_origen_id = safe_string(juzgado_origen.clave)
            exh_exhorto.juzgado_origen_nombre = safe_string(juzgado_origen.descripcion, save_enie=True)
            exh_exhorto.numero_expediente_origen = safe_string(form.numero_expediente_origen.data)
            exh_exhorto.numero_oficio_origen = safe_string(form.numero_oficio_origen.data)
            exh_exhorto.tipo_juicio_asunto_delitos = safe_string(form.tipo_juicio_asunto_delitos.data)
            exh_exhorto.juez_exhortante = safe_string(form.juez_exhortante.data, save_enie=True)
            exh_exhorto.fojas = form.fojas.data
            exh_exhorto.dias_responder = form.dias_responder.data
            exh_exhorto.tipo_diligenciacion_nombre = safe_string(form.tipo_diligenciacion_nombre.data, save_enie=True)
            exh_exhorto.fecha_origen = form.fecha_origen.data
            exh_exhorto.observaciones = safe_string(form.observaciones.data, save_enie=True, max_len=1024)
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
    # Buscar el juzgado origen en Autoridades
    juzgado_origen = Autoridad.query.filter_by(clave=exh_exhorto.juzgado_origen_id).filter_by(estatus="A").first()
    # Cargar los valores guardados en el formulario
    form.exhorto_origen_id.data = exh_exhorto.exhorto_origen_id
    form.materia.data = exh_exhorto.materia.id
    form.juzgado_origen.data = juzgado_origen.id
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


@exh_exhortos.route("/exh_exhortos/consultar/<int:exh_exhorto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def get_from_externo(exh_exhorto_id):
    """Lanzar tarea en el fondo para consultar Exhorto al PJ Externo"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    tarea = current_user.launch_task(
        comando="exh_exhortos.tasks.lanzar_consultar",
        mensaje="Consultando exhorto desde externo",
        exh_exhorto_id=exh_exhorto.id,
    )
    flash("Se ha lanzado la tarea en el fondo. Esta página se va a recargar en 10 segundos...", "info")
    return redirect(url_for("tareas.detail", tarea_id=tarea.id))


@exh_exhortos.route("/exh_exhortos/enviar/<int:exh_exhorto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def send(exh_exhorto_id):
    """Lanzar tarea en el fondo para envíar Exhorto al PJ Externo"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    es_valido = True
    # Validar que el Exhorto tenga partes
    exh_exhorto_partes = ExhExhortoParte.query.filter_by(exh_exhorto_id=exh_exhorto_id).filter_by(estatus="A").first()
    if exh_exhorto_partes is None:
        es_valido = False
        flash("No se pudo enviar el exhorto. Debe incluir al menos una parte.", "warning")
    # Validar que el Exhorto tenga archivos
    exh_exhorto_archivos = ExhExhortoArchivo.query.filter_by(exh_exhorto_id=exh_exhorto_id).filter_by(estatus="A").first()
    if exh_exhorto_archivos is None:
        es_valido = False
        flash("No se pudo enviar el exhorto. Debe incluir al menos un archivo.", "warning")
    # Validar que el estado del Exhorto sea "PENDIENTE"
    if exh_exhorto.estado != "PENDIENTE":
        es_valido = False
        flash("El estado del exhorto debe ser PENDIENTE.", "warning")
    # Hacer el cambio de estado
    if es_valido:
        tarea = current_user.launch_task(
            comando="exh_exhortos.tasks.lanzar_consultar",
            mensaje="Enviando exhorto al externo",
            exh_exhorto_id=exh_exhorto.id,
        )
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


@exh_exhortos.route("/exh_exhortos/regresar_a_por_enviar/<int:exh_exhorto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def back_to_by_send(exh_exhorto_id):
    """Regresar el estado del exhorto a por enviar"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    es_valido = True
    # Validar que el estado del Exhorto sea "INTENTOS AGOTADOS"
    if exh_exhorto.estado != "INTENTOS AGOTADOS":
        es_valido = False
        flash("El estado del exhorto debe ser INTENTOS AGOTADOS.", "warning")
    # Hacer el cambio de estado
    if es_valido:
        exh_exhorto.estado = "POR ENVIAR"
        exh_exhorto.por_enviar_intentos = 0
        exh_exhorto.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Se reiniciaron los intentos de envío del exhorto {exh_exhorto.exhorto_origen_id}"),
            url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id))


@exh_exhortos.route("/exh_exhortos/regresar_a_pendiente/<int:exh_exhorto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def back_to_pending(exh_exhorto_id):
    """Regresar el estado del exhorto a por enviar"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    es_valido = True
    # Validar que el estado del Exhorto sea "RECHAZADO"
    if exh_exhorto.estado != "RECHAZADO":
        es_valido = False
        flash("El estado del exhorto debe ser RECHAZADO.", "warning")
    # Hacer el cambio de estado
    if es_valido:
        exh_exhorto.estado = "PENDIENTE"
        exh_exhorto.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"El exhorto se regresó al estado PENDIENTE {exh_exhorto.exhorto_origen_id}"),
            url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id))


@exh_exhortos.route("/exh_exhortos/transferir/<int:exh_exhorto_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def transfer(exh_exhorto_id):
    """Transferir un exhorto a un juzgado"""
    exh_exhorto = ExhExhorto.query.get_or_404(exh_exhorto_id)
    form = ExhExhortoTransferForm()
    if form.validate_on_submit():
        exh_exhorto.area = form.exh_area.data
        exh_exhorto.autoridad_id = form.autoridad.data
        exh_exhorto.estado = "TRANSFIRIENDO"
        exh_exhorto.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Exhorto Transferido {exh_exhorto.exhorto_origen_id}"),
            url=url_for("exh_exhortos.detail", exh_exhorto_id=exh_exhorto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Buscar el juzgado origen en Autoridades
    juzgado_origen = Autoridad.query.filter_by(clave=exh_exhorto.juzgado_origen_id).filter_by(estatus="A").first()
    municipio_origen = Municipio.query.filter_by(id=exh_exhorto.municipio_origen_id).first()
    municipio_destino = Municipio.query.filter_by(id=exh_exhorto.municipio_destino_id).first()
    # Cargar los valores guardados en el formulario
    form.exhorto_origen_id.data = exh_exhorto.exhorto_origen_id
    form.estado_origen.data = municipio_origen.estado.nombre
    form.municipio_origen.data = municipio_origen.nombre
    form.juzgado_origen.data = juzgado_origen.clave
    form.numero_expediente_origen.data = exh_exhorto.numero_expediente_origen
    form.numero_oficio_origen.data = exh_exhorto.numero_oficio_origen
    form.tipo_juicio_asunto_delitos.data = exh_exhorto.tipo_juicio_asunto_delitos
    form.juez_exhortante.data = exh_exhorto.juez_exhortante
    form.fojas.data = exh_exhorto.fojas
    form.dias_responder.data = exh_exhorto.dias_responder
    form.tipo_diligenciacion_nombre.data = exh_exhorto.tipo_diligenciacion_nombre
    form.fecha_origen.data = exh_exhorto.fecha_origen
    form.observaciones.data = exh_exhorto.observaciones
    form.folio_seguimiento.data = exh_exhorto.folio_seguimiento
    form.materia.data = exh_exhorto.materia.nombre
    form.estado_destino.data = municipio_destino.estado.nombre
    form.municipio_destino.data = municipio_destino.nombre
    form.remitente.data = exh_exhorto.remitente
    form.exh_area.data = exh_exhorto.exh_area.id
    form.numero_exhorto.data = exh_exhorto.numero_exhorto
    form.estado.data = exh_exhorto.estado  # Read only
    # Entregar
    return render_template("exh_exhortos/transfer.jinja2", form=form, exh_exhorto=exh_exhorto)
