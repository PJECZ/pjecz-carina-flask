"""
Alimentar Roles
"""

import csv
import sys
from pathlib import Path

import click

from carina.blueprints.roles.models import Rol
from carina.extensions import database
from lib.safe_string import safe_string

ROLES_CSV = "seed/roles_permisos.csv"


def alimentar_roles():
    """Alimentar Roles"""
    ruta = Path(ROLES_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        sys.exit(1)
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        sys.exit(1)
    sesion = database.session
    click.echo("Alimentando roles: ", nl=False)
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            rol_id = int(row["rol_id"])
            nombre = safe_string(row["nombre"], save_enie=True)
            estatus = row["estatus"]
            if rol_id != contador + 1:
                click.echo(click.style(f"  AVISO: rol_id {rol_id} no es consecutivo", fg="red"))
                sys.exit(1)
            sesion.add(
                Rol(
                    nombre=nombre,
                    estatus=estatus,
                )
            )
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    sesion.commit()
    sesion.close()
    click.echo()
    click.echo(click.style(f"  {contador} roles alimentados.", fg="green"))
