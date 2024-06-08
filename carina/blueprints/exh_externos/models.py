"""
Exh Externos, modelos
"""

from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from carina.extensions import database
from lib.universal_mixin import UniversalMixin


class ExhExterno(database.Model, UniversalMixin):
    """ExhExterno"""

    # Nombre de la tabla
    __tablename__ = "exh_externos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    clave = Column(String(16), unique=True, nullable=False)
    descripcion = Column(String(256), nullable=False)
    api_key = Column(String(128))

    # Columnas endpoints
    endpoint_consultar_materias = Column(String(256))
    endpoint_recibir_exhorto = Column(String(256))
    endpoint_recibir_exhorto_archivo = Column(String(256))
    endpoint_consultar_exhorto = Column(String(256))
    endpoint_recibir_respuesta_exhorto = Column(String(256))
    endpoint_recibir_respuesta_exhorto_archivo = Column(String(256))
    endpoint_actualizar_exhorto = Column(String(256))
    endpoint_recibir_promocion = Column(String(256))
    endpoint_recibir_promocion_archivo = Column(String(256))

    def __repr__(self):
        """Representación"""
        return f"<ExhExterno {self.id}>"
