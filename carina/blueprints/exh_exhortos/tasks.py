"""
Exh Exhortos, tareas en el fondo
"""

import logging
from datetime import datetime
from pathlib import Path

import pytz

from carina.app import create_app
from carina.blueprints.exh_exhortos.models import ExhExhorto
from carina.extensions import database
from lib.exceptions import MyAnyError
from lib.tasks import set_task_error, set_task_progress

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("logs/exh_exhortos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()
database.app = app


def consultar(exh_exhorto_id: int) -> tuple[str, str, str]:
    """Consultar exhortos"""
    bitacora.info("Inicia consultar exhortos")

    # Elaborar mensaje_termino
    mensaje_termino = "Consultar exhortos ha terminado"
    bitacora.info(mensaje_termino)

    # Entregar mensaje_termino, nombre_archivo y url_publica
    return mensaje_termino, "", ""


def lanzar_consultar(exh_exhorto_id):
    """Lanzar tarea en el fondo para consultar exhortos"""

    # Iniciar la tarea en el fondo
    set_task_progress(0, "Inicia consultar exhortos")

    # Ejecutar
    try:
        mensaje_termino, nombre_archivo, url_publica = consultar(exh_exhorto_id)
    except MyAnyError as error:
        mensaje_error = str(error)
        set_task_error(mensaje_error)
        return mensaje_error

    # Terminar la tarea en el fondo
    set_task_progress(100, mensaje_termino, nombre_archivo, url_publica)

    # Entregar mensaje de termino
    return mensaje_termino


def enviar(exh_exhorto_id: int) -> tuple[str, str, str]:
    """Enviar exhortos"""
    bitacora.info("Inicia enviar exhortos")

    # Elaborar mensaje_termino
    mensaje_termino = "Enviar exhortos ha terminado"
    bitacora.info(mensaje_termino)

    # Entregar mensaje_termino, nombre_archivo y url_publica
    return mensaje_termino, "", ""


def lanzar_enviar(exh_exhorto_id):
    """Lanzar tarea en el fondo para enviar exhortos"""

    # Iniciar la tarea en el fondo
    set_task_progress(0, "Inicia enviar exhortos")

    # Ejecutar
    try:
        mensaje_termino, nombre_archivo, url_publica = enviar(exh_exhorto_id)
    except MyAnyError as error:
        mensaje_error = str(error)
        set_task_error(mensaje_error)
        return mensaje_error

    # Terminar la tarea en el fondo
    set_task_progress(100, mensaje_termino, nombre_archivo, url_publica)

    # Entregar mensaje de termino
    return mensaje_termino
