"""
Materias, vistas
"""

import json

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from carina.blueprints.materias.models import Materia
from carina.blueprints.permisos.models import Permiso
from carina.blueprints.usuarios.decorators import permission_required
from lib.datatables import get_datatable_parameters, output_datatable_json

MODULO = "MATERIAS"

materias = Blueprint("materias", __name__, template_folder="templates")


@materias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@materias.route("/materias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Materias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Materia.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    # Ordenar y paginar
    registros = consulta.order_by(Materia.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "clave": resultado.clave,
                "nombre": resultado.nombre,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@materias.route("/materias")
def list_active():
    """Listado de Materias activas"""
    return render_template(
        "materias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Materias",
        estatus="A",
    )


@materias.route("/materias/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Materias inactivas"""
    return render_template(
        "materias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Materias inactivos",
        estatus="B",
    )


@materias.route("/materias/<int:materia_id>")
def detail(materia_id):
    """Detalle de una Materia"""
    materia = Materia.query.get_or_404(materia_id)
    return render_template("materias/detail.jinja2", materia=materia)
