"""
Exh Exhortos Videos, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from carina.blueprints.bitacoras.models import Bitacora
from carina.blueprints.exh_exhortos.models import ExhExhorto
from carina.blueprints.exh_exhortos_videos.models import ExhExhortoVideo
from carina.blueprints.modulos.models import Modulo
from carina.blueprints.permisos.models import Permiso
from carina.blueprints.usuarios.decorators import permission_required
from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string

MODULO = "EXH EXHORTOS VIDEOS"

exh_exhortos_videos = Blueprint("exh_exhortos_videos", __name__, template_folder="templates")


@exh_exhortos_videos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@exh_exhortos_videos.route("/exh_exhortos_videos")
def list_active():
    """Listado de Videos activos"""
    return "TODO: Listado de Videos activos"
