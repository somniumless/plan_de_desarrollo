from app import db
from app.auditoria.models import Auditoria, ResultadoAccion
from flask import request, current_app
from flask_login import current_user
from datetime import datetime
import json

def registrar_auditoria(
    accion: str,
    entidad_afectada: str,
    id_entidad: str = None,
    detalles: dict = None,
    resultado: ResultadoAccion = ResultadoAccion.EXITO,
    usuario_id: str = None
):
    try:
        if usuario_id is None:
            if current_user and current_user.is_authenticated:
                usuario_id = current_user.usuario_id
            else:
                usuario_id = "ANONYMOUS"

        ip_origen = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent') if request else None

        if detalles:
            cleaned_detalles = {}
            for k, v in detalles.items():
                if isinstance(v, (datetime, ResultadoAccion)):
                    cleaned_detalles[k] = str(v)
                elif isinstance(v, (list, dict, str, int, float, bool, type(None))):
                    cleaned_detalles[k] = v
                else:
                    if hasattr(v, 'to_dict') and callable(getattr(v, 'to_dict')):
                        cleaned_detalles[k] = v.to_dict()
                    else:
                        cleaned_detalles[k] = str(v)
            detalles = cleaned_detalles

        nuevo_registro = Auditoria(
            usuario_id=usuario_id,
            accion=accion,
            entidad_afectada=entidad_afectada,
            id_entidad=id_entidad,
            fecha_accion=datetime.utcnow(),
            detalles=detalles,
            ip_origen=ip_origen,
            user_agent=user_agent,
            resultado=resultado
        )
        db.session.add(nuevo_registro)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"ERROR al registrar auditoría para '{accion}' en '{entidad_afectada}': {e}", exc_info=True)