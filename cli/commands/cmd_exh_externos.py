"""
CLI Exh Externos
"""

import sys

import click

from carina.app import create_app
from carina.blueprints.exh_externos.tasks import probar_endpoints as task_probar_endpoints
from carina.extensions import database
from lib.exceptions import MyAnyError

app = create_app()
app.app_context().push()
database.app = app

TIMEOUT = 30  # 30 segundos


@click.group()
def cli():
    """Exh Externos"""


@click.command()
@click.option("--clave", type=str, help="Clave")
def probar_endpoints(clave):
    """Probar endpoints"""

    # Ejecutar la tarea
    try:
        mensaje_termino, _, _ = task_probar_endpoints(clave)
    except MyAnyError as error:
        click.echo(click.style(str(error), fg="red"))
        sys.exit(1)

    # Mensaje de termino
    click.echo(click.style(mensaje_termino, fg="green"))


cli.add_command(probar_endpoints)
