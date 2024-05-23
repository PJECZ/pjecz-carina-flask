"""
Exh Exhortos, modelos
"""

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from lib.universal_mixin import UniversalMixin

from carina.extensions import database


class ExhExhorto(database.Model, UniversalMixin):
    """ExhExhorto"""

    ESTADOS = {
        "PENDIENTE": "Pendiente",
        "RECIBIDO": "Recibido",
    }

    REMITENTES = {
        "INTERNO": "Interno",
        "EXTERNO": "Externo",
    }

    # Nombre de la tabla
    __tablename__ = "exh_exhortos"

    # Clave primaria
    id = Column(Integer, primary_key=True)

    # UUID identificador con el que el PJ exhortante identifica el exhorto que envía
    exhorto_origen_id = Column(String(64), nullable=False, unique=True)

    # Identificador INEGI del Municipio del Estado del PJ exhortado al que se quiere enviar el Exhorto
    municipio_destino_id = Column(Integer, nullable=False)

    # Clave de la materia (el que se obtuvo en la consulta de materias del PJ exhortado) al que el Exhorto hace referencia
    materia_id = Column(Integer, ForeignKey("materias.id"), index=True, nullable=False)
    materia = relationship("Materia", back_populates="exh_exhortos")

    # Identificador INEGI del Estado de origen del Municipio donde se ubica el Juzgado del PJ exhortante
    # estado_origen_id = Column(Integer, ForeignKey("estados.id"), index=True, nullable=False)
    # estado_origen = relationship("Estado", back_populates="exhortos")

    # Identificador INEGI del Municipio donde está localizado el Juzgado del PJ exhortante
    municipio_origen_id = Column(Integer, ForeignKey("municipios.id"), index=True, nullable=False)
    municipio_origen = relationship("Municipio", back_populates="exh_exhortos_origenes")

    # Identificador propio del Juzgado/Área que envía el Exhorto
    juzgado_origen_id = Column(String(64))

    # Nombre del Juzgado/Área que envía el Exhorto
    juzgado_origen_nombre = Column(String(256), nullable=False)

    # El número de expediente (o carpeta procesal, carpeta...) que tiene el asunto en el Juzgado de Origen
    numero_expediente_origen = Column(String(256), nullable=False)

    # El número del oficio con el que se envía el exhorto, el que corresponde al control interno del Juzgado de origen
    numero_oficio_origen = Column(String(256))

    # Nombre del tipo de Juicio, o asunto, listado de los delitos (para materia Penal) que corresponde al Expediente del cual el Juzgado envía el Exhorto
    tipo_juicio_asunto_delitos = Column(String(256), nullable=False)

    # Nombre completo del Juez del Juzgado o titular del Área que envía el Exhorto
    juez_exhortante = Column(String(256))

    # Número de fojas que contiene el exhorto. El valor 0 significa "No Especificado"
    fojas = Column(Integer, nullable=False)

    # Cantidad de dias a partir del día que se recibió en el Poder Judicial exhortado que se tiene para responder el Exhorto. El valor de 0 significa "No Especificado"
    dias_responder = Column(Integer, nullable=False)

    # Nombre del tipo de diligenciación que le corresponde al exhorto enviado. Este puede contener valores como "Oficio", "Petición de Parte"
    tipo_diligenciacion_nombre = Column(String(256))

    # Fecha y hora en que el Poder Judicial exhortante registró que se envió el exhorto en su hora local. En caso de no enviar este dato, el Poder Judicial exhortado puede tomar su fecha hora local.
    fecha_origen = Column(DateTime, nullable=False)

    # Texto simple que contenga información extra o relevante sobre el exhorto.
    observaciones = Column(String(1024))

    # Hijos
    # PersonaParte[] NO Contiene la definición de las partes del Expediente
    exh_exhortos_partes = relationship("ExhExhortoParte", back_populates="exh_exhorto")
    # ArchivoARecibir[] SI Colección de los datos referentes a los archivos que se van a recibir el Poder Judicial exhortado en el envío del Exhorto.
    exh_exhortos_archivos = relationship("ExhExhortoArchivo", back_populates="exh_exhorto")

    # GUID/UUID... que sea único
    folio_seguimiento = Column(String(64), nullable=False, unique=True)

    # Área de recepción
    exh_area_id = Column(Integer, ForeignKey("exh_areas.id"), index=True, nullable=False)
    exh_area = relationship("ExhArea", back_populates="exh_exhortos")

    # Estado de recepción del documento
    estado = Column(Enum(*ESTADOS, name="exh_exhortos_estados", native_enum=False), nullable=True)

    # Campo para saber si es un proceso interno o extorno
    remitente = Column(Enum(*REMITENTES, name="exh_exhortos_remitentes", native_enum=False), nullable=True)

    # Juzgado/Área al que se turna el Exhorto y hará el correspondiente proceso de este

    # Número de Exhorto con el que se radica en el Juzgado/Área que se turnó el exhorto. Este número sirve para que el usuario pueda indentificar su exhorto dentro del Juzgado/Área donde se turnó.
    numero_exhorto = Column(String(256))

    def __repr__(self):
        """Representación"""
        return f"<ExhExhorto {self.id}>"
