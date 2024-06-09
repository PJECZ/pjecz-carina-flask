"""
Flask App
"""

import rq
from flask import Flask
from redis import Redis

from carina.blueprints.autoridades.views import autoridades
from carina.blueprints.bitacoras.views import bitacoras
from carina.blueprints.distritos.views import distritos
from carina.blueprints.domicilios.views import domicilios
from carina.blueprints.entradas_salidas.views import entradas_salidas
from carina.blueprints.estados.views import estados
from carina.blueprints.exh_areas.views import exh_areas
from carina.blueprints.exh_exhortos.views import exh_exhortos
from carina.blueprints.exh_exhortos_archivos.views import exh_exhortos_archivos
from carina.blueprints.exh_exhortos_partes.views import exh_exhortos_partes
from carina.blueprints.exh_externos.views import exh_externos
from carina.blueprints.materias.views import materias
from carina.blueprints.modulos.views import modulos
from carina.blueprints.municipios.views import municipios
from carina.blueprints.oficinas.views import oficinas
from carina.blueprints.permisos.views import permisos
from carina.blueprints.roles.views import roles
from carina.blueprints.sistemas.views import sistemas
from carina.blueprints.usuarios.models import Usuario
from carina.blueprints.usuarios.views import usuarios
from carina.blueprints.usuarios_roles.views import usuarios_roles
from carina.extensions import csrf, database, login_manager, moment
from config.settings import Settings


def create_app():
    """Crear app"""
    # Definir app
    app = Flask(__name__, instance_relative_config=True)

    # Cargar la configuración
    app.config.from_object(Settings())

    # Redis
    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.task_queue = rq.Queue(app.config["TASK_QUEUE"], connection=app.redis, default_timeout=3000)

    # Registrar blueprints
    app.register_blueprint(autoridades)
    app.register_blueprint(bitacoras)
    app.register_blueprint(distritos)
    app.register_blueprint(domicilios)
    app.register_blueprint(entradas_salidas)
    app.register_blueprint(estados)
    app.register_blueprint(exh_areas)
    app.register_blueprint(exh_exhortos)
    app.register_blueprint(exh_exhortos_archivos)
    app.register_blueprint(exh_exhortos_partes)
    app.register_blueprint(exh_externos)
    app.register_blueprint(materias)
    app.register_blueprint(modulos)
    app.register_blueprint(municipios)
    app.register_blueprint(oficinas)
    app.register_blueprint(permisos)
    app.register_blueprint(roles)
    app.register_blueprint(sistemas)
    app.register_blueprint(usuarios)
    app.register_blueprint(usuarios_roles)

    # Inicializar extensiones
    extensions(app)

    # Inicializar autenticación
    authentication(Usuario)

    # Entregar app
    return app


def extensions(app):
    """Inicializar extensiones"""
    csrf.init_app(app)
    database.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    # socketio.init_app(app)


def authentication(user_model):
    """Inicializar Flask-Login"""
    login_manager.login_view = "usuarios.login"

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)
