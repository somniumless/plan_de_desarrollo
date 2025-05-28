from functools import wraps
from flask import request
from flask_login import current_user
import enum
import traceback

from app.auditoria.utils import registrar_auditoria, ResultadoAccion

def audit_action(accion, entidad_afectada_name, id_param_name=None, obj_id_attr=None, include_args_in_details=None, include_obj_attrs_in_details=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario_id = current_user.usuario_id if current_user.is_authenticated else None

            detalles = {}
            if request.method in ['POST', 'PUT'] and request.is_json:
                try:
                    detalles['data'] = request.get_json()
                except Exception as e:
                    print(f"ADVERTENCIA: No se pudo parsear el JSON del request para el método {request.method}: {e}")
                    detalles['data'] = "Error al parsear JSON" 

            if include_args_in_details:
                for arg_name in include_args_in_details:
                    if arg_name in kwargs:
                        detalles[arg_name] = kwargs[arg_name]
                    elif arg_name == 'data' and request.method in ['POST', 'PUT'] and request.is_json:
                        try:
                            detalles['request_body'] = request.get_json()
                        except Exception as e:
                            print(f"ADVERTENCIA: No se pudo parsear el JSON del request.body para el método {request.method}: {e}")
                            detalles['request_body'] = "Error al parsear JSON"

            id_entidad_auditoria = None
            obj_afectado = None

            try:
                response = f(*args, **kwargs)

                if request.method in ['POST', 'PUT']:
                    if obj_id_attr:
                        if isinstance(response, tuple) and isinstance(response[0], dict):
                            if 'data' in response[0] and isinstance(response[0]['data'], dict) and obj_id_attr in response[0]['data']:
                                id_entidad_auditoria = response[0]['data'][obj_id_attr]
                            elif obj_id_attr in response[0]:
                                id_entidad_auditoria = response[0][obj_id_attr]
                        elif isinstance(response, dict) and obj_id_attr in response:
                            id_entidad_auditoria = response[obj_id_attr]
                        if not id_entidad_auditoria:
                            for arg in args:
                                if hasattr(arg, obj_id_attr):
                                    id_entidad_auditoria = getattr(arg, obj_id_attr)
                                    obj_afectado = arg
                                    break
                            if not id_entidad_auditoria:
                                for kwarg_val in kwargs.values():
                                    if hasattr(kwarg_val, obj_id_attr):
                                        id_entidad_auditoria = getattr(kwarg_val, obj_id_attr)
                                        obj_afectado = kwarg_val
                                        break

                if id_param_name and id_param_name in kwargs:
                    id_entidad_auditoria = kwargs[id_param_name]
                    if request.method == 'DELETE' and not obj_afectado:
                        pass 

                if include_obj_attrs_in_details and obj_afectado:
                    for attr_name in include_obj_attrs_in_details:
                        if hasattr(obj_afectado, attr_name):
                            attr_value = getattr(obj_afectado, attr_name)
                            if isinstance(attr_value, enum.Enum):
                                detalles[attr_name] = attr_value.value
                            else:
                                detalles[attr_name] = str(attr_value)

                registrar_auditoria(
                    accion=accion,
                    entidad_afectada=entidad_afectada_name,
                    id_entidad=id_entidad_auditoria,
                    detalles=detalles,
                    resultado=ResultadoAccion.EXITO,
                    usuario_id=usuario_id
                )
                return response

            except Exception as e:
                traceback.print_exc()
                print(f"DEBUG: Error capturado en audit_action para {accion}: {e}")

                registrar_auditoria(
                    accion=accion,
                    entidad_afectada=entidad_afectada_name,
                    id_entidad=id_entidad_auditoria,
                    detalles={"error": str(e), "original_request_data": detalles.get('data')},
                    resultado=ResultadoAccion.FALLO,
                    usuario_id=usuario_id
                )
                raise e

        return decorated_function
    return decorator