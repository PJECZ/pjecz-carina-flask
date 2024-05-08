"""
Municipios, modelos
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from lib.universal_mixin import UniversalMixin

from carina.extensions import database


class Municipio(database.Model, UniversalMixin):
    """Municipio"""

    # Nombre de la tabla
    __tablename__ = "municipios"

    # Clave primaria
    id = Column(Integer, primary_key=True)

    # Clave foránea
    estado_id = Column(Integer, ForeignKey("estados.id"), index=True, nullable=False)
    estado = relationship("Estado", back_populates="municipios")

    # Columnas
    clave = Column(String(16), unique=True, nullable=False)
    descripcion = Column(String(256), nullable=False)

    # Hijos
    exh_exhortos_origenes = relationship("ExhExhorto", back_populates="municipio_origen")

    def __repr__(self):
        """Representación"""
        return f"<Municipio {self.estado.clave}{self.clave}>"
