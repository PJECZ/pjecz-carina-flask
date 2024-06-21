"""
CLI Exh Exhortos
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta

import click
import requests
from dotenv import load_dotenv

from carina.app import create_app
from carina.blueprints.estados.models import Estado
from carina.blueprints.exh_exhortos.models import ExhExhorto
from carina.blueprints.exh_externos.models import ExhExterno
from carina.blueprints.municipios.models import Municipio
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
@click.option("--probar", is_flag=True, help="Modo de pruebas, no actualiza la base de datos, solo muestra en pantalla")
def consultar(folio_seguimiento: str, probar: bool = False):
    """Consultar un exhorto o todos los exhortos con estado RECIBIDO CON EXITO"""

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

    # Bucle de exhortos
    contador_respondidos = 0
    for exh_exhorto in exh_exhortos:
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
@click.option("--probar", is_flag=True, help="Modo de pruebas, no envía los exhortos, solo los consulta y muestra en pantalla")
def enviar(exhorto_origen_id: str, probar: bool = False):
    """Enviar un exhorto o todos los exhortos con estado POR ENVIAR"""

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
            click.echo(click.style(f"ERROR: No existe el exhorto con ID {exhorto_origen_id}", fg="red"))
            sys.exit(1)
        if exh_exhorto.estado != "POR ENVIAR":
            click.echo(click.style(f"ERROR: El exhorto con ID {exhorto_origen_id} no está en estado POR ENVIAR", fg="red"))
            sys.exit(1)
        exh_exhortos.append(exh_exhorto)

    # Validar que haya exhortos
    if len(exh_exhortos) == 0:
        click.echo(click.style("AVISO: No hay exhortos para enviar", fg="yellow"))
        sys.exit(0)

    # Definir el tiempo actual
    tiempo_actual = datetime.now()

    # Bucle de exhortos POR ENVIAR
    contador_recibidos_con_exito = 0
    for exh_exhorto in exh_exhortos:
        # Si por_enviar_tiempo_anterior mas SEGUNDOS_ESPERA_ENTRE_INTENTOS es mayor al tiempo actual, entonces se omite
        # if (
        #     exh_exhorto.por_enviar_tiempo_anterior is not None
        #     and tiempo_actual < exh_exhorto.por_enviar_tiempo_anterior + timedelta(seconds=SEGUNDOS_ESPERA_ENTRE_INTENTOS)
        # ):
        #     continue

        # Mostrar mensaje de que está enviando el exhorto
        click.echo(f"Enviando exhorto {exh_exhorto.exhorto_origen_id}...")

        # Consultar el Estado de destino a partir del ID del Municipio en municipio_destino_id
        municipio = Municipio.query.get(exh_exhorto.municipio_destino_id)
        if municipio is None:
            click.echo(click.style(f"AVISO: No existe el municipio con ID {exh_exhorto.municipio_destino_id}", fg="yellow"))
            continue
        estado = Estado.query.get(municipio.estado_id)
        if estado is None:
            click.echo(click.style(f"AVISO: No existe el estado con ID {municipio.estado_id}", fg="yellow"))
            continue

        # Consultar el ExhExterno con el ID del Estado, tomar solo el primero
        exh_externo = ExhExterno.query.filter_by(estado_id=estado.id).first()
        if exh_externo is None:
            click.echo(click.style(f"AVISO: No hay datos en exh_externos del estado {estado.nombre}", fg="yellow"))
            continue

        # Si exh_externo no tiene API-key
        if exh_externo.api_key is None or exh_externo.api_key == "":
            click.echo(click.style(f"AVISO: No tiene API-key en exh_externos el estado {estado.nombre}", fg="yellow"))
            continue

        # Si exh_externo no tiene endpoint para enviar exhortos
        if exh_externo.endpoint_recibir_exhorto is None or exh_externo.endpoint_recibir_exhorto == "":
            click.echo(click.style(f"AVISO: No tiene endpoint para enviar exhortos el estado {estado.nombre}", fg="yellow"))
            continue

        # Si exh_externo no tiene endpoint para enviar archivos
        if exh_externo.endpoint_recibir_exhorto_archivo is None or exh_externo.endpoint_recibir_exhorto_archivo == "":
            click.echo(click.style(f"AVISO: No tiene endpoint para enviar archivos el estado {estado.nombre}", fg="yellow"))
            continue

        # Consultar el municipio de municipio_destino_id para enviar su clave INEGI
        municipio_destino = Municipio.query.get(exh_exhorto.municipio_destino_id)
        if municipio_destino is None:
            click.echo(click.style(f"AVISO: No existe municipio_destino_id {exh_exhorto.municipio_destino_id}", fg="yellow"))
            continue

        # Bucle para juntar los datos de las partes
        partes = []
        for exh_exhorto_parte in exh_exhorto.exh_exhortos_partes:
            partes.append(
                {
                    "nombre": str(exh_exhorto_parte.nombre),
                    "apellidoPaterno": str(exh_exhorto_parte.apellido_paterno),
                    "apellidoMaterno": str(exh_exhorto_parte.apellido_materno),
                    "genero": str(exh_exhorto_parte.genero),
                    "esPersonaMoral": bool(exh_exhorto_parte.es_persona_moral),
                    "tipoParte": int(exh_exhorto_parte.tipo_parte),
                    "tipoParteNombre": str(exh_exhorto_parte.tipo_parte_nombre),
                }
            )

        # Bucle para juntar los datos de los archivos exh_exhortos_archivos
        archivos = []
        for exh_exhorto_archivo in exh_exhorto.exh_exhortos_archivos:
            archivos.append(
                {
                    "nombreArchivo": str(exh_exhorto_archivo.nombre_archivo),
                    "hashSha1": str(exh_exhorto_archivo.hash_sha1),
                    "hashSha256": str(exh_exhorto_archivo.hash_sha256),
                    "tipoDocumento": int(exh_exhorto_archivo.tipo_documento),
                }
            )

        # Definir los datos del exhorto
        datos_exhorto = {
            "exhortoOrigenId": str(exh_exhorto.exhorto_origen_id),
            "municipioDestinoId": int(municipio_destino.clave),
            "materiaClave": str(exh_exhorto.materia.clave),
            "estadoOrigenId": int(exh_exhorto.municipio_origen.estado.clave),
            "municipioOrigenId": int(exh_exhorto.municipio_origen.clave),
            "juzgadoOrigenId": str(exh_exhorto.juzgado_origen_id),
            "juzgadoOrigenNombre": str(exh_exhorto.juzgado_origen_nombre),
            "numeroExpedienteOrigen": str(exh_exhorto.numero_expediente_origen),
            "numeroOficioOrigen": str(exh_exhorto.numero_oficio_origen),
            "tipoJuicioAsuntoDelitos": str(exh_exhorto.tipo_juicio_asunto_delitos),
            "juezExhortante": str(exh_exhorto.juez_exhortante),
            "partes": partes,
            "fojas": int(exh_exhorto.fojas),
            "diasResponder": int(exh_exhorto.dias_responder),
            "tipoDiligenciacionNombre": str(exh_exhorto.tipo_diligenciacion_nombre),
            "fechaOrigen": exh_exhorto.fecha_origen.strftime("%Y-%m-%dT%H:%M:%S"),
            "observaciones": str(exh_exhorto.observaciones),
            "archivos": archivos,
        }

        # Mostrar datos_exhorto en pantalla
        if probar is True:
            click.echo(json.dumps(datos_exhorto, indent=2))

        # Enviar el exhorto
        comunicado_con_exito = False
        recibido_con_exito = False
        if probar is False:
            # Enviar el exhorto
            try:
                response = requests.post(
                    exh_externo.endpoint_recibir_exhorto,
                    headers={"X-Api-Key": exh_externo.api_key},
                    timeout=TIMEOUT,
                    json=datos_exhorto,
                )
                response.raise_for_status()
                comunicado_con_exito = True
                respuesta = response.json()
                if not "success" in respuesta:
                    click.echo(click.style("AVISO: La respuesta no tiene 'success' al enviar el exhorto", fg="yellow"))
                else:
                    recibido_con_exito = bool(respuesta["success"])
            except requests.exceptions.ConnectionError:
                click.echo(click.style("AVISO: No hubo respuesta del servidor al enviar el exhorto", fg="yellow"))
            except requests.exceptions.HTTPError as error:
                click.echo(click.style(f"AVISO: Status Code {str(error)} al enviar el exhorto", fg="yellow"))
            except requests.exceptions.RequestException:
                click.echo(click.style("AVISO: Inesperado al enviar el exhorto", fg="yellow"))

            # Si se recibió con éxito...
            if recibido_con_exito is True:
                if "message" in respuesta:
                    click.echo(click.style(f"Se recibió con éxito el exhorto: {str(respuesta['message'])}", fg="green"))
                else:
                    click.echo(click.style("Se recibió con éxito el exhorto.", fg="green"))

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
                if "message" in respuesta:
                    click.echo(f"Se RECHAZO el envio del exhorto: {str(respuesta['message'])}")
                if "errors" in respuesta:
                    click.echo(f"Y regresa estos errores: {str(respuesta['errors'])}")
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
            # Enviar el archivo
            if probar is False:
                try:
                    response = requests.post(
                        exh_externo.endpoint_recibir_exhorto_archivo,
                        headers={"X-Api-Key": exh_externo.api_key},
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
        if probar is False and archivo_enviado_con_exito is False:
            exh_exhorto.estado = "RECHAZADO"
            exh_exhorto.save()
            if "message" in respuesta:
                click.echo(f"Se RECHAZO el envio del archivo: {str(respuesta['message'])}")
            if "errors" in respuesta:
                click.echo(f"Y regresa estos errores: {str(respuesta['errors'])}")
            continue

        # Se envió con éxito, cambiar el estado del exhorto a RECIBIDO CON EXITO
        if probar is False:
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
