"""
ExhExhorto_Videos, modelos
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

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
    titulo: Mapped[str] = mapped_column(String(256))

    # Descripción del video/audiencia realizada
    descripcion: Mapped[Optional[str]] = mapped_column(Text(1024))

    # Fecha (o fecha hora) en que se realizó el video y/o audiencia.
    fecha: Mapped[Optional[datetime]]

    # URL que el usuario final podrá accesar para poder visualizar el video
    url_acceso: Mapped[str] = mapped_column(String(512))

    def __repr__(self):
        """Representación"""
        return f"<ExhExhortoVideo {self.id}>"
