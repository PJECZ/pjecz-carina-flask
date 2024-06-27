"""
Exh Externos, tareas en el fondo
"""

import logging

import requests

from carina.app import create_app
from carina.blueprints.exh_externos.models import ExhExterno
from carina.extensions import database
from lib.exceptions import MyAnyError, MyEmptyError, MyNotExistsError
from lib.safe_string import safe_clave
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

TIMEOUT = 30  # 30 segundos


def probar_endpoints(clave: str) -> tuple[str, str, str]:
    """Probar endpoints"""
    bitacora.info("Inicia probar_endpoints")

    # Limpiar clave
    clave = safe_clave(clave)

    # Si no se proporciona la clave, entonces se van a probar todos los exh externos
    exh_externos = []
    if clave == "":
        bitacora.info("Por probar TODOS los externos")
        exh_externos = ExhExterno.query.filter_by(estatus="A").all()
    else:
        # Consultar exh externo a partir de la clave
        exh_externo = ExhExterno.query.filter_by(clave=safe_clave(clave)).filter_by(estatus="A").first()
        if exh_externo is None:
            mensaje_advertencia = f"ERROR: No existe o ha sido eliminado el externo con clave {clave}"
            bitacora.warning(mensaje_advertencia)
            raise MyNotExistsError(mensaje_advertencia)
        exh_externos.append(exh_externo)

    # Validar que haya exh externos
    if len(exh_externos) == 0:
        mensaje_advertencia = "No hay externos para probar"
        bitacora.warning(mensaje_advertencia)
        raise MyEmptyError(mensaje_advertencia)

    # Probar endpoints de consultar materias
    contador_exitosos = 0
    contador_total = 0
    for exh_externo in exh_externos:
        if exh_externo.api_key == "":
            continue
        if exh_externo.endpoint_consultar_materias == "":
            continue
        bitacora.info("Probando %s...", exh_externo.clave)
        mensaje_advertencia = ""
        contador_total += 1
        try:
            respuesta = requests.get(
                exh_externo.endpoint_consultar_materias,
                headers={"X-Api-Key": exh_externo.api_key},
                timeout=TIMEOUT,
            )
            respuesta.raise_for_status()
        except requests.exceptions.ConnectionError as error:
            mensaje_advertencia = f"Error de conexión {str(error)}"
        except requests.exceptions.Timeout:
            mensaje_advertencia = "Se acabó el tiempo de espera"
        except requests.exceptions.HTTPError as error:
            mensaje_advertencia = f"Error HTTP {str(error)}"
        except requests.exceptions.RequestException as error:
            mensaje_advertencia = f"Error de request {str(error)}"
        if mensaje_advertencia != "":
            bitacora.warning(mensaje_advertencia)
            continue
        bitacora.info("Respuesta exitosa de %s del endpoint %s", exh_externo.clave, exh_externo.endpoint_consultar_materias)
        contador_exitosos += 1

    # Elaborar mensaje_termino
    if len(exh_externos) == 1:
        if mensaje_advertencia != "":
            mensaje_termino = f"ERROR en {exh_externo.clave} a {exh_externo.endpoint_consultar_materias} {mensaje_advertencia}"
        else:
            mensaje_termino = f"Éxito en {exh_externo.clave} a {exh_externo.endpoint_consultar_materias}"
    else:
        mensaje_termino = f"{contador_exitosos} respuestas exitosas de {contador_total}"
    bitacora.info("Termina probar_endpoints con %s", mensaje_termino)

    # Entregar mensaje_termino, nombre_archivo y url_publica
    return mensaje_termino, "", ""


def lanzar_probar_endpoints(clave: str):
    """Lanzar tarea en el fondo para probar externos"""

    # Iniciar la tarea en el fondo
    set_task_progress(0, "Se ha lanzado exh_externos.probar_endpoints")

    # Ejecutar
    try:
        mensaje_termino, nombre_archivo, url_publica = probar_endpoints(clave)
    except MyAnyError as error:
        mensaje_error = str(error)
        set_task_error(mensaje_error)
        return mensaje_error

    # Terminar la tarea en el fondo
    set_task_progress(100, mensaje_termino, nombre_archivo, url_publica)

    # Entregar mensaje de termino
    return mensaje_termino
