"""
CLI Exh Exhortos
"""

import sys

import click

from carina.app import create_app
from carina.blueprints.exh_exhortos.tasks import consultar as task_consultar
from carina.blueprints.exh_exhortos.tasks import enviar as task_enviar
from carina.extensions import database
from lib.exceptions import MyAnyError

app = create_app()
app.app_context().push()
database.app = app


@click.group()
def cli():
    """Exh Exhortos"""


@click.command()
@click.option("--folio_seguimiento", type=str, help="folio de seguimiento de un exhorto")
def consultar(folio_seguimiento: str):
    """Consultar un exhorto o todos los exhortos con estado RECIBIDO CON EXITO"""

    # Ejecutar la tarea
    try:
        mensaje_termino, _, _ = task_consultar(folio_seguimiento)
    except MyAnyError as error:
        click.echo(click.style(str(error), fg="red"))
        sys.exit(1)

    # Mensaje de termino
    click.echo(click.style(mensaje_termino, fg="green"))


@click.command()
@click.option("--exhorto_origen_id", type=str, help="Exhorto origen ID")
def enviar(exhorto_origen_id: str = ""):
    """Enviar un exhorto o todos los exhortos con estado POR ENVIAR"""

    # Ejecutar la tarea
    try:
        mensaje_termino, _, _ = task_enviar(exhorto_origen_id)
    except MyAnyError as error:
        click.echo(click.style(str(error), fg="red"))
        sys.exit(1)

    # Mensaje de termino
    click.echo(click.style(mensaje_termino, fg="green"))


cli.add_command(consultar)
cli.add_command(enviar)
