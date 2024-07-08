"""
ExhExhorto_Videos, modelos
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import now

from lib.universal_mixin import UniversalMixin
from carina.extensions import database


class ExhExhortoVideo(database.Model, UniversalMixin):
    """ExhExhortoVideo"""

    # Nombre de la tabla
    __tablename__ = "exh_exhortos_videos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    # El titulo del video, esto para que pueda identificarse
    titulo: Mapped[str] = mapped_column(String(16))

    # Descripción del video/audiencia realizada
    descripcion: Mapped[Optional[str]] = mapped_column(String(256))

    # Fecha (o fecha hora) en que se realizó el video y/o audiencia.
    fecha: Mapped[Optional[datetime]] = mapped_column(DateTime, default=now())

    # URL que el usuario final podrá accesar para poder visualizar el video
    url_acceso: Mapped[Optional[str]] = mapped_column(String(1024))

    def __repr__(self):
        """Representación"""
        return f"<ExhExhortoVideo {self.id}>"
