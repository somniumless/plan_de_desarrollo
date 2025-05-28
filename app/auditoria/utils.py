from app import db
from app.auditoria.models import Auditoria, ResultadoAccion 
from flask import request, current_app
from flask_login import current_user
from datetime import datetime
import json
from enum import Enum 

def _json_serializable_value(obj):
    if isinstance(obj, Enum):
        return obj.value  
    if isinstance(obj, datetime):
        return obj.isoformat() 
    return obj

def _recursively_serialize_dict(data):
    if isinstance(data, dict):
        return {k: _recursively_serialize_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_recursively_serialize_dict(elem) for elem in data]
    else:
        return _json_serializable_value(data)

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
                usuario_id = None 

        user_agent = request.headers.get('User-Agent') if request else None 

        if detalles:
            detalles_serializable = _recursively_serialize_dict(detalles)
        else:
            detalles_serializable = None 

        nuevo_registro = Auditoria(
            usuario_id=usuario_id,
            accion=accion,
            entidad_afectada=entidad_afectada,
            id_entidad=id_entidad,
            fecha_accion=datetime.utcnow(),
            detalles=detalles_serializable, 
            user_agent=user_agent,
            resultado=resultado
        )
        db.session.add(nuevo_registro)
        db.session.commit()
    except Exception as e:
        db.session.rollback() 
        current_app.logger.error(f"ERROR al registrar auditoría para '{accion}' en '{entidad_afectada}': {e}", exc_info=True)