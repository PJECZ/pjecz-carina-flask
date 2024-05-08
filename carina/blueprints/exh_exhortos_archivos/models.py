"""
Exh Exhortos Archivos, modelos
"""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from lib.universal_mixin import UniversalMixin

from carina.extensions import database


class ExhExhortoAchivo(database.Model, UniversalMixin):
    """ExhExhortoAchivo"""

    ESTADOS = {
        "PENDIENTE": "Pendiente",
        "RECIBIDO": "Recibido",
    }

    # Nombre de la tabla
    __tablename__ = "exh_exhortos_archivos"

    # Clave primaria
    id = Column(Integer, primary_key=True)

    # Clave foránea
    exh_exhorto_id = Column(Integer, ForeignKey("exh_exhortos.id"), index=True, nullable=False)
    exh_exhorto = relationship("ExhExhorto", back_populates="exh_exhortos_archivos")

    # Nombre del archivo, como se enviará. Este debe incluir el la extensión del archivo.
    nombre_archivo = Column(String(256), nullable=False)

    # Hash SHA1 en hexadecimal que corresponde al archivo a recibir. Esto para comprobar la integridad del archivo.
    hash_sha1 = Column(String(256))

    # Hash SHA256 en hexadecimal que corresponde al archivo a recibir. Esto para comprobar la integridad del archivo.
    hash_sha256 = Column(String(256))

    # Identificador del tipo de documento que representa el archivo:
    # 1 = Oficio
    # 2 = Acuerdo
    # 3 = Anexo
    tipo_documento = Column(Integer, nullable=False)

    # URL del archivo en Google Storage
    url = Column(String(512), nullable=False, default="", server_default="")

    # Estado de recepción del documento
    estado = Column(Enum(*ESTADOS, name="exh_exhortos_archivos_estados", native_enum=False), nullable=True)

    # Tamaño del archivo recibido en bytes
    tamano = Column(Integer, nullable=False)

    # Fecha y hora de recepción del documento
    fecha_hora_recepcion = Column(DateTime, nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<ExhExhortoAchivo {self.id}>"
