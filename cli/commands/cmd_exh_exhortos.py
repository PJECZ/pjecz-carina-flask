"""
CLI Exh Exhortos
"""

import os
import sys
import time
from datetime import datetime

import click
import requests
from dotenv import load_dotenv

from carina.app import create_app
from carina.blueprints.exh_exhortos.models import ExhExhorto
from carina.blueprints.exh_externos.models import ExhExterno
from carina.extensions import database
from lib.exceptions import MyBucketNotFoundError, MyFileNotFoundError, MyNotValidParamError
from lib.google_cloud_storage import get_blob_name_from_url, get_file_from_gcs

app = create_app()
app.app_context().push()
database.app = app

load_dotenv()  # Take environment variables from .env

CANTIDAD_MAXIMA_INTENTOS = 3
SEGUNDOS_ESPERA_ENTRE_INTENTOS = 120  # 2 minutos
TIMEOUT = 30  # 30 segundos


@click.group()
def cli():
    """Exh Exhortos"""


@click.command()
@click.option("--folio_seguimiento", type=str, help="folio de seguimiento de un exhorto")
def consultar(folio_seguimiento: str):
    """Consultar un exhorto o todos los exhortos con estado RECIBIDO CON EXITO"""
    click.echo("Consultando exhortos...")

    # Inicializar el listado de exhortos a consultar
    exh_exhortos = []

    # Si NO viene folio_seguimiento
    if folio_seguimiento is None:
        # Consultar todos los exhortos con estado RECIBIDO CON EXITO
        exh_exhortos = ExhExhorto.query.filter_by(estado="RECIBIDO CON EXITO").filter_by(estatus="A").all()
    else:
        # Consultar el exhorto con folio_seguimiento
        exh_exhorto = ExhExhorto.query.filter_by(folio_seguimiento=folio_seguimiento).filter_by(estatus="A").first()
        if exh_exhorto is None:
            click.echo(f"ERROR: No existe el exhorto con folio de seguimiento {folio_seguimiento}")
            sys.exit(1)
        if exh_exhorto.estado != "RECIBIDO CON EXITO":
            click.echo(f"ERROR: El exhorto con folio seguimiento {folio_seguimiento} no está en estado RECIBIDO CON EXITO")
            sys.exit(1)
        exh_exhortos.append(exh_exhorto)

    # Validar que haya exhortos
    if len(exh_exhortos) == 0:
        click.echo("No hay exhortos para consultar")
        sys.exit(1)

    # Bucle de exhortos RECIBIDO CON EXITO
    contador_respondidos = 0
    for exh_exhorto in exh_exhortos:
        # Intentar consultar el exhorto
        click.echo(f"  Consultando el exhorto {exh_exhorto.folio_seguimiento}")

        # Consultar el exhorto
        try:
            response = requests.post(
                f"endpoint_consultar_exhorto/{exh_exhorto.folio_seguimiento}",
                headers={"X-Api-Key": "API-KEY-QUE-NOS-DIO-EL-ESTADO"},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            respuesta = response.json()
            if "success" not in respuesta:
                click.echo("ERROR: En la respuesta no se encontró el campo 'success' al consultar el exhorto")
                continue
        except requests.exceptions.ConnectionError:
            click.echo("ERROR: No hubo respuesta del servidor al consultar el exhorto")
            continue
        except requests.exceptions.HTTPError as error:
            click.echo("ERROR: Status Code al consultar el exhorto: " + str(error))
            continue
        except requests.exceptions.RequestException:
            click.echo("ERROR: Inesperado al consultar el exhorto")
            continue

        # Inicializar boleano para saber si ha cambiado un dato
        ha_habido_cambios = False

        # respuesta["exhortoOrigenId"]
        # respuesta["folioSeguimiento"]
        # respuesta["estadoDestinoId"]
        # respuesta["estadoDestinoNombre"]
        # respuesta["municipioDestinoId"]
        # respuesta["municipioDestinoNombre"]
        # respuesta["materiaClave"]
        # respuesta["materiaNombre"]
        # respuesta["estadoOrigenId"]
        # respuesta["estadoOrigenNombre"]
        # respuesta["municipioOrigenId"]
        # respuesta["municipioOrigenNombre"]
        # respuesta["juzgadoOrigenId"]
        # respuesta["juzgadoOrigenNombre"]
        # respuesta["numeroExpedienteOrigen"]
        # respuesta["numeroOficioOrigen"]
        # respuesta["tipoJuicioAsuntoDelitos"]
        # respuesta["juezExhortante"]
        # respuesta["partes"]
        # respuesta["fojas"]
        # respuesta["diasResponder"]
        # respuesta["tipoDiligenciacionNombre"]
        # respuesta["fechaOrigen"]
        # respuesta["observaciones"]
        # respuesta["archivos"]
        # respuesta["fechaHoraRecepcion"]
        # respuesta["municipioTurnadoId"]
        # respuesta["municipioTurnadoNombre"]
        # respuesta["areaTurnadoId"]
        # respuesta["areaTurnadoNombre"]
        # respuesta["numeroExhorto"]
        # respuesta["urlInfo"]

        # Si NO hubo cambios y se agotaron los diasResponder, cambiar el estado a NO FUE RESPONDIDO

        # Si ha habido cambios, actualizar el exhorto

        # Si ha habido cambios, cambiar el estado del exhorto a RESPONDIDO

        # Si el estado es RESPONDIDO, vamos a pedir los archivos, subirlos a Google Storage y agregar registros a exh_exhortos_archivos

        # Si el estado es RESPONDIDO, determinar si fue aceptado, parcialmente o rechazado

        # Pausa de 2 segundos
        time.sleep(2)

    # Mensaje final
    click.echo(f"Se consultaron {contador_respondidos} con éxito.")


@click.command()
@click.option("--exhorto_origen_id", type=str, help="Exhorto origen ID")
def enviar(exhorto_origen_id: str):
    """Enviar un exhorto o todos los exhortos con estado POR ENVIAR"""
    click.echo("Enviando exhortos...")

    # Inicializar el listado de exhortos a enviar
    exh_exhortos = []

    # Si NO viene exhorto_origen_id
    if exhorto_origen_id is None:
        # Consultar todos los exhortos con estado POR ENVIAR
        exh_exhortos = ExhExhorto.query.filter_by(estado="POR ENVIAR").filter_by(estatus="A").all()
    else:
        # Consultar el exhorto con exhorto_origen_id
        exh_exhorto = ExhExhorto.query.filter_by(id=exhorto_origen_id).filter_by(estatus="A").first()
        if exh_exhorto is None:
            click.echo(f"ERROR: No existe el exhorto con ID {exhorto_origen_id}")
            sys.exit(1)
        if exh_exhorto.estado != "POR ENVIAR":
            click.echo(f"ERROR: El exhorto con ID {exhorto_origen_id} no está en estado POR ENVIAR")
            sys.exit(1)
        exh_exhortos.append(exh_exhorto)

    # Validar que haya exhortos
    if len(exh_exhortos) == 0:
        click.echo("No hay exhortos para enviar")
        sys.exit(0)

    # Definir el tiempo actual
    tiempo_actual = datetime.now()

    # Bucle de exhortos POR ENVIAR
    contador_recibidos_con_exito = 0
    for exh_exhorto in exh_exhortos:
        # Si por_enviar_tiempo_anterior mas SEGUNDOS_ESPERA_ENTRE_INTENTOS es mayor al tiempo actual, entonces se omite
        if (
            exh_exhorto.por_enviar_tiempo_anterior is not None
            and tiempo_actual < exh_exhorto.por_enviar_tiempo_anterior + SEGUNDOS_ESPERA_ENTRE_INTENTOS
        ):
            continue

        # Mostrar mensaje de envío
        click.echo(f"  Enviando exhorto {exh_exhorto.exhorto_origen_id}")

        # Bucle para juntar los datos de las partes
        partes = []
        for exh_exhorto_parte in exh_exhorto.exh_exhortos_partes:
            partes.append(
                {
                    "nombre": exh_exhorto_parte.nombre,
                    "apellidoPaterno": exh_exhorto_parte.apellido_paterno,
                    "apellidoMaterno": exh_exhorto_parte.apellido_materno,
                    "genero": exh_exhorto_parte.genero,
                    "esPersonaMoral": exh_exhorto_parte.es_persona_moral,
                    "tipoParte": exh_exhorto_parte.tipo_parte,
                    "tipoParteNombre": exh_exhorto_parte.tipo_parte_nombre,
                }
            )

        # Bucle para juntar los datos de los archivos exh_exhortos_archivos
        archivos = []
        for exh_exhorto_archivo in exh_exhorto.exh_exhortos_archivos:
            archivos.append(
                {
                    "nombreArchivo": exh_exhorto_archivo.nombre_archivo,
                    "hashSha1": exh_exhorto_archivo.hash_sha1,
                    "hashSha256": exh_exhorto_archivo.hash_sha256,
                    "tipoDocumento": exh_exhorto_archivo.tipo_documento,
                }
            )

        # Definir los datos del exhorto
        datos_exhorto = {
            "exhortoOrigenId": exh_exhorto.exhorto_origen_id,
            "municipioDestinoId": exh_exhorto.municipio_destino_id,
            "materiaClave": exh_exhorto.materia.clave,
            "estadoOrigenId": exh_exhorto.municipio_origen.estado.clave,
            "municipioOrigenId": exh_exhorto.municipio_origen.clave,
            "juzgadoOrigenId": exh_exhorto.juzgado_origen_id,
            "juzgadoOrigenNombre": exh_exhorto.juzgado_origen_nombre,
            "numeroExpedienteOrigen": exh_exhorto.numero_expediente_origen,
            "numeroOficioOrigen": exh_exhorto.numero_oficio_origen,
            "tipoJuicioAsuntoDelitos": exh_exhorto.tipo_juicio_asunto_delitos,
            "juezExhortante": exh_exhorto.juez_exhortante,
            "partes": partes,
            "fojas": exh_exhorto.fojas,
            "diasResponder": exh_exhorto.dias_responder,
            "tipoDiligenciacionNombre": exh_exhorto.tipo_diligenciacion_nombre,
            "fechaOrigen": exh_exhorto.fecha_origen,
            "observaciones": exh_exhorto.observaciones,
            "archivos": archivos,
        }

        # Enviar el exhorto
        comunicado_con_exito = False
        recibido_con_exito = False
        try:
            response = requests.post(
                "https://ESTADO/EXHORTOS/ENVIAR",
                headers={"X-Api-Key": "API-KEY-QUE-NOS-DIO-EL-ESTADO"},
                timeout=TIMEOUT,
                json=datos_exhorto,
            )
            response.raise_for_status()
            comunicado_con_exito = True
            respuesta = response.json()
            if "success" not in respuesta:
                click.echo("ERROR: En la respuesta no se encontró el campo 'success' al enviar el exhorto")
                continue
            recibido_con_exito = bool(respuesta["success"])
        except requests.exceptions.ConnectionError:
            click.echo("ERROR: No hubo respuesta del servidor al enviar el exhorto")
        except requests.exceptions.HTTPError as error:
            click.echo("ERROR: Status Code al enviar el exhorto: " + str(error))
        except requests.exceptions.RequestException:
            click.echo("ERROR: Inesperado al enviar el exhorto")

        # Si NO se pudo comunicar...
        if comunicado_con_exito is False:
            # Actualizar el por_enviar_tiempo_anterior
            exh_exhorto.por_enviar_tiempo_anterior = datetime.now()
            # Incrementar por_enviar_intentos
            exh_exhorto.por_enviar_intentos += 1
            # Si el exhorto excede CANTIDAD_MAXIMA_INTENTOS, entonces cambiar el estado a INTENTOS AGOTADOS
            if exh_exhorto.por_enviar_intentos > CANTIDAD_MAXIMA_INTENTOS:
                exh_exhorto.estado = "INTENTOS AGOTADOS"
            # Guardar los cambios
            exh_exhorto.save()
            continue

        # Si NO se recibió con éxito...
        if recibido_con_exito is False:
            # Cambiar el estado a RECHAZADO
            exh_exhorto.estado = "RECHAZADO"
            exh_exhorto.save()
            if "errors" in respuesta:
                click.echo(f"ERRORES: {str(respuesta['errors'])}")
            continue

        # Mandar los archivos del exhorto con multipart/form-data
        archivo_enviado_con_exito = False
        for exh_exhorto_archivo in exh_exhorto.exh_exhortos_archivos:
            # Para cada intento de enviar el archivo, se inicializa archivo_enviado_con_exito en falso
            archivo_enviado_con_exito = False
            # Pausa de 2 segundos
            time.sleep(2)
            # Obtener el contenido del archivo desde Google Storage
            try:
                archivo_contenido = get_file_from_gcs(
                    bucket_name=os.environ.get("CLOUD_STORAGE_DEPOSITO"),
                    blob_name=get_blob_name_from_url(exh_exhorto_archivo.url),
                )
            except (MyBucketNotFoundError, MyFileNotFoundError, MyNotValidParamError) as error:
                click.echo(f"ERROR: Al tratar de bajar el archivo del storage {str(error)}")
                continue
            try:
                response = requests.post(
                    "https://ESTADO/EXHORTOS/ENVIAR_ARCHIVO",
                    headers={"X-Api-Key": "API-KEY-QUE-NOS-DIO-EL-ESTADO"},
                    timeout=TIMEOUT,
                    params={"exhortoOrigenId": exh_exhorto.exhorto_origen_id},
                    files={"archivo": (exh_exhorto_archivo.nombre_archivo, archivo_contenido, "application/pdf")},
                )
                response.raise_for_status()
                respuesta = response.json()
                if "success" not in respuesta:
                    click.echo("ERROR: En la respuesta no se encontró el campo 'success' al enviar el archivo")
                    continue
                archivo_enviado_con_exito = bool(respuesta["success"])
            except requests.exceptions.ConnectionError:
                click.echo("ERROR: No hubo respuesta del servidor al enviar el archivo")
            except requests.exceptions.HTTPError as error:
                click.echo("ERROR: Status Code al enviar el archivo: " + str(error))
            except requests.exceptions.RequestException:
                click.echo("ERROR: Inesperado al enviar el archivo")
            # Si NO fue archivo_enviado_con_exito, entonces dejar de enviar archivos
            if archivo_enviado_con_exito is False:
                break

        # Si falla archivo_enviado_con_exito
        if archivo_enviado_con_exito is False:
            exh_exhorto.estado = "RECHAZADO"
            exh_exhorto.save()
            if "errors" in respuesta:
                click.echo(f"ERRORES: {str(respuesta['errors'])}")
            continue

        # Se envió con éxito, cambiar el estado del exhorto a RECIBIDO CON EXITO
        exh_exhorto.estado = "RECIBIDO CON EXITO"
        exh_exhorto.save()

        # Pausa de 2 segundos
        time.sleep(2)

        # Incrementar contador_recibidos_con_exito
        contador_recibidos_con_exito += 1

    # Mensaje final
    click.echo(f"Se enviaron {contador_recibidos_con_exito} con éxito.")


cli.add_command(consultar)
cli.add_command(enviar)
