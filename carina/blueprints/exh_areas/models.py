"""
Exh Areas, modelos
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from lib.universal_mixin import UniversalMixin

from carina.extensions import database


class ExhArea(database.Model, UniversalMixin):
    """ExhArea"""

    # Nombre de la tabla
    __tablename__ = "exh_areas"

    # Clave primaria
    id = Column(Integer, primary_key=True)

    # Columnas
    clave = Column(String(16), unique=True, nullable=False)
    nombre = Column(String(256), unique=True, nullable=False)

    # Hijos
    exh_exhortos = relationship("ExhExhorto", back_populates="exh_area")

    def __repr__(self):
        """Representación"""
        return f"<ExhArea {self.clave}>"
