"""
CLI Exh Exhortos
"""

import sys
import time
from datetime import datetime

import click
import requests

from carina.app import create_app
from carina.blueprints.exh_exhortos.models import ExhExhorto
from carina.blueprints.exh_externos.models import ExhExterno
from carina.extensions import database

app = create_app()
app.app_context().push()
database.app = app

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
        exh_exhortos.append(exh_exhorto)

    # Validar que haya exhortos
    if len(exh_exhortos) == 0:
        click.echo("No hay exhortos para consultar")
        sys.exit(1)

    # Bucle de exhortos RECIBIDO CON EXITO
    contador_respondidos = 0
    for exh_exhorto in exh_exhortos:
        # Si por_consultar_tiempo_anterior mas SEGUNDOS_ESPERA_ENTRE_INTENTOS es mayor al tiempo actual, entonces continuar

        # Intentar consultar el exhorto
        click.echo(f"  Consultando el exhorto {exh_exhorto.folio_seguimiento}")

        # Si el exhorto se consulta con éxito, entonces cambiar el estado a RESPONDIDO

        # Actualizar el consultar_tiempo_anterior
        # exh_exhorto.consultar_tiempo_anterior = datetime.now()

        # Incrementar consultar_intentos
        # exh_exhorto.consultar_intentos += 1

        # Si el exhorto excede CANTIDAD_MAXIMA_INTENTOS, entonces cambiar el estado a NO FUE RESPONDIDO
        # if exh_exhorto.consultar_intentos > CANTIDAD_MAXIMA_INTENTOS:
        #     exh_exhorto.estado = "NO FUE RESPONDIDO"

        # Guardar los cambios
        # exh_exhorto.save()

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
        exh_exhortos.append(exh_exhorto)

    # Validar que haya exhortos
    if len(exh_exhortos) == 0:
        click.echo("No hay exhortos para enviar")
        sys.exit(1)

    # Bucle de exhortos POR ENVIAR
    contador_recibidos_con_exito = 0
    for exh_exhorto in exh_exhortos:
        # Si por_enviar_tiempo_anterior mas SEGUNDOS_ESPERA_ENTRE_INTENTOS es mayor al tiempo actual, entonces continuar
        if exh_exhorto.por_enviar_tiempo_anterior is not None:
            tiempo_actual = datetime.now()
            tiempo_espera = exh_exhorto.por_enviar_tiempo_anterior + SEGUNDOS_ESPERA_ENTRE_INTENTOS
            if tiempo_actual < tiempo_espera:
                continue

        # Intentar enviar el exhorto
        click.echo(f"  Enviando exhorto {exh_exhorto.exhorto_origen_id}")

        # Si el exhorto se envía con éxito, entonces cambiar el estado a RECIBIDO CON EXITO

        # A partir de aqui, el exhorto NO se pudo enviar con éxito

        # Actualizar el por_enviar_tiempo_anterior
        exh_exhorto.por_enviar_tiempo_anterior = datetime.now()

        # Incrementar por_enviar_intentos
        exh_exhorto.por_enviar_intentos += 1

        # Si el exhorto excede CANTIDAD_MAXIMA_INTENTOS, entonces cambiar el estado a INTENTOS AGOTADOS
        if exh_exhorto.por_enviar_intentos > CANTIDAD_MAXIMA_INTENTOS:
            exh_exhorto.estado = "INTENTOS AGOTADOS"

        # Guardar los cambios
        exh_exhorto.save()

        # Pausa de 2 segundos
        time.sleep(2)

    # Mensaje final
    click.echo(f"Se enviaron {contador_recibidos_con_exito} con éxito.")


cli.add_command(consultar)
cli.add_command(enviar)
