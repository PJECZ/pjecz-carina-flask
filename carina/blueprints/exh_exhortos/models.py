"""
Exh Exhortos, modelos
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now

from carina.extensions import database
from lib.universal_mixin import UniversalMixin


class ExhExhorto(database.Model, UniversalMixin):
    """ExhExhorto"""

    ESTADOS = {
        "RECIBIDO": "Recibido",
        "TRANSFIRIENDO": "Transfiriendo",
        "PROCESANDO": "Procesando",
        "RECHAZADO": "Rechazado",
        "DILIGENCIADO": "Diligenciado",
        "CONTESTADO": "Contestado",
        "PENDIENTE": "Pendiente",
        "CANCELADO": "Cancelado",
        "POR ENVIAR": "Por enviar",
        "INTENTOS AGOTADOS": "Intentos agotados",
        "RECIBIDO CON EXITO": "Recibido con exito",
        "NO FUE RESPONDIDO": "No fue respondido",
        "RESPONDIDO": "Respondido",
    }

    REMITENTES = {
        "INTERNO": "Interno",
        "EXTERNO": "Externo",
    }

    # Nombre de la tabla
    __tablename__ = "exh_exhortos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea: Juzgado/Área al que se turna el Exhorto y hará el correspondiente proceso de este
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship(back_populates="exh_exhortos")

    # Clave foránea: Área de recepción
    exh_area_id: Mapped[int] = mapped_column(ForeignKey("exh_areas.id"))
    exh_area: Mapped["ExhArea"] = relationship(back_populates="exh_areas")

    # Clave foránea: Materia (el que se obtuvo en la consulta de materias del PJ exhortado) al que el Exhorto hace referencia
    materia_id: Mapped[int] = mapped_column(ForeignKey("materias.id"))
    materia: Mapped["Materia"] = relationship(back_populates="exh_exhortos")

    # Clave foránea: Identificador INEGI del Municipio donde está localizado el Juzgado del PJ exhortante
    municipio_origen_id: Mapped[int] = mapped_column(ForeignKey("municipios.id"))
    municipio_origen: Mapped["Municipio"] = relationship(back_populates="exh_exhortos_origenes")

    # GUID/UUID... que sea único
    folio_seguimiento: Mapped[str] = mapped_column(Uuid, unique=True)

    # UUID identificador con el que el PJ exhortante identifica el exhorto que envía
    exhorto_origen_id: Mapped[str] = mapped_column(Uuid)

    # Identificador INEGI del Municipio del Estado del PJ exhortado al que se quiere enviar el Exhorto
    municipio_destino_id: Mapped[int]

    # Identificador propio del Juzgado/Área que envía el Exhorto, opcional
    juzgado_origen_id: Mapped[Optional[str]] = mapped_column(String(64))

    # Nombre del Juzgado/Área que envía el Exhorto, opcional
    juzgado_origen_nombre: Mapped[Optional[str]] = mapped_column(String(256))

    # El número de expediente (o carpeta procesal, carpeta...) que tiene el asunto en el Juzgado de Origen
    numero_expediente_origen: Mapped[str] = mapped_column(String(256))

    # El número del oficio con el que se envía el exhorto, el que corresponde al control interno del Juzgado de origen, opcional
    numero_oficio_origen: Mapped[Optional[str]] = mapped_column(String(256))

    # Nombre del tipo de Juicio, o asunto, listado de los delitos (para materia Penal)
    # que corresponde al Expediente del cual el Juzgado envía el Exhorto
    tipo_juicio_asunto_delitos: Mapped[str] = mapped_column(String(256))

    # Nombre completo del Juez del Juzgado o titular del Área que envía el Exhorto, opcional
    juez_exhortante: Mapped[Optional[str]] = mapped_column(String(256))

    # Número de fojas que contiene el exhorto. El valor 0 significa "No Especificado"
    fojas: Mapped[int] = mapped_column(Integer, default=0)

    # Cantidad de dias a partir del día que se recibió en el Poder Judicial exhortado que se tiene para responder el Exhorto.
    # El valor de 0 significa "No Especificado"
    dias_responder: Mapped[int] = mapped_column(Integer, default=0)

    # Nombre del tipo de diligenciación que le corresponde al exhorto enviado.
    # Este puede contener valores como "Oficio", "Petición de Parte", opcional
    tipo_diligenciacion_nombre: Mapped[Optional[str]] = mapped_column(String(256))

    # Fecha y hora en que el Poder Judicial exhortante registró que se envió el exhorto en su hora local.
    # En caso de no enviar este dato, el Poder Judicial exhortado puede tomar su fecha hora local.
    fecha_origen: Mapped[datetime] = mapped_column(DateTime, default=now())

    # Texto simple que contenga información extra o relevante sobre el exhorto, opcional
    observaciones: Mapped[Optional[str]] = mapped_column(String(1024))

    # Estado de recepción del documento
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="exh_exhortos_estados", native_enum=False), index=True)

    # Campo para saber si es un proceso interno o extorno
    remitente: Mapped[str] = mapped_column(Enum(*REMITENTES, name="exh_exhortos_remitentes", native_enum=False), nullable=True)

    # Número de Exhorto con el que se radica en el Juzgado/Área que se turnó el exhorto.
    # Este número sirve para que el usuario pueda indentificar su exhorto dentro del Juzgado/Área donde se turnó, opcional
    numero_exhorto: Mapped[Optional[str]] = mapped_column(String(256))

    # Hijos: PersonaParte[] NO Contiene la definición de las partes del Expediente
    exh_exhortos_partes: Mapped[List["ExhExhortoParte"]] = relationship("ExhExhortoParte", back_populates="exh_exhorto")

    # Hijos: ArchivoARecibir[] SI Colección de los datos referentes a los archivos
    # que se van a recibir el Poder Judicial exhortado en el envío del Exhorto.
    exh_exhortos_archivos: Mapped[List["ExhExhortoArchivo"]] = relationship("ExhExhortoArchivo", back_populates="exh_exhorto")

    def __repr__(self):
        """Representación"""
        return f"<ExhExhorto {self.id}>"
