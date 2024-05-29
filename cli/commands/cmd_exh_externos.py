"""
CLI Exh Externos
"""

import sys

import click
import requests

from lib.safe_string import safe_clave
from carina.app import create_app
from carina.blueprints.exh_externos.models import ExhExterno
from carina.extensions import database

app = create_app()
app.app_context().push()
database.app = app

TIMEOUT = 30  # 30 segundos


@click.group()
def cli():
    """Exh Externos"""


@click.command()
@click.option("--clave", type=str, help="Clave")
def probar_endpoint_consultar_materias(clave):
    """Probar endpont consultar materias"""

    # Si no se proporciona la clave, entonces se van a probar todos los exh externos
    exh_externos = []
    if clave is None:
        click.echo("Probar TODOS los exh externos")
        exh_externos = ExhExterno.query.filter_by(estatus="A").all()
    else:
        # Consultar exh externo a partir de la clave
        exh_externo = ExhExterno.query.filter_by(clave=safe_clave(clave)).filter_by(estatus="A").first()
        if exh_externo is None:
            click.echo(f"ERROR: No existe el exh externo con clave {clave}")
            sys.exit(1)
        exh_externos.append(exh_externo)

    # Validar que haya exh externos
    if len(exh_externos) == 0:
        click.echo("No hay exh externos para probar")
        sys.exit(1)

    # Mostrar en pantalla los end points de consultar materias
    exitosos = 0
    for exh_externo in exh_externos:
        if exh_externo.api_key == "":
            continue
        if exh_externo.endpoint_consultar_materias == "":
            continue
        click.echo(click.style(f"Probando {exh_externo.clave} en {exh_externo.endpoint_consultar_materias}...", fg="blue"))
        # Consultar la API usando request y mostrar mensajes cuando falla la conexión
        try:
            respuesta = requests.get(
                exh_externo.endpoint_consultar_materias,
                headers={"X-Api-Key": exh_externo.api_key},
                timeout=TIMEOUT,
            )
            respuesta.raise_for_status()
        except requests.exceptions.ConnectionError as error:
            click.echo(click.style(f"  Error de conexión {str(error)}", fg="red"))
            continue
        except requests.exceptions.Timeout:
            click.echo(click.style("  Timeout", fg="red"))
            continue
        except requests.exceptions.HTTPError as error:
            click.echo(click.style(f"  Error HTTP {str(error)}", fg="red"))
            continue
        except requests.exceptions.RequestException as error:
            click.echo(click.style(f"  Error de request {str(error)}", fg="red"))
            continue
        click.echo(click.style("  Respuesta 200", fg="green"))
        exitosos += 1

    # Mensaje de éxito
    click.echo(f"Se probaron {exitosos} end-points con éxito")


cli.add_command(probar_endpoint_consultar_materias)
