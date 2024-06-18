"""
Exh Externos, tareas en el fondo
"""

import logging
from datetime import datetime
from pathlib import Path

import pytz

from carina.app import create_app
from carina.blueprints.exh_externos.models import ExhExterno
from carina.extensions import database
from lib.exceptions import MyAnyError
from lib.tasks import set_task_error, set_task_progress

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("logs/exh_externos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()
database.app = app


def probar_endpoints(exh_externo_id: int) -> tuple[str, str, str]:
    """Probar endpoints"""
    bitacora.info("Inicia probar endpoints")

    # Elaborar mensaje_termino
    mensaje_termino = "Probar endpoints ha terminado"
    bitacora.info(mensaje_termino)

    # Entregar mensaje_termino, nombre_archivo y url_publica
    return mensaje_termino, "", ""


def lanzar_probar_endpoints(exh_externo_id: int):
    """Lanzar tarea en el fondo para probar externos"""

    # Iniciar la tarea en el fondo
    set_task_progress(0, "Inicia probar externos")

    # Ejecutar
    try:
        mensaje_termino, nombre_archivo, url_publica = probar_endpoints(exh_externo_id)
    except MyAnyError as error:
        mensaje_error = str(error)
        set_task_error(mensaje_error)
        return mensaje_error

    # Terminar la tarea en el fondo
    set_task_progress(100, mensaje_termino, nombre_archivo, url_publica)

    # Entregar mensaje de termino
    return mensaje_termino
