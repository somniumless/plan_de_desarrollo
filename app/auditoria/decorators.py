from functools import wraps
from flask import request
from flask_login import current_user 

from app.auditoria.utils import registrar_auditoria, ResultadoAccion

def audit_action(accion, entidad_afectada_name, id_param_name=None, obj_id_attr=None, include_args_in_details=None, include_obj_attrs_in_details=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            usuario_id = current_user.usuario_id if current_user.is_authenticated else "ANONYMOUS"

            detalles = {}
            if request.is_json:
                detalles['data'] = request.get_json()
            if include_args_in_details:
                for arg_name in include_args_in_details:
                    if arg_name in kwargs:
                        detalles[arg_name] = kwargs[arg_name]
                    elif arg_name == 'data' and request.is_json:
                        detalles['request_body'] = request.get_json() 

            id_entidad_auditoria = None
            obj_afectado = None 

            try:
                response = f(*args, **kwargs)

                if request.method in ['POST', 'PUT']:
                    if obj_id_attr:
                        if isinstance(response, tuple) and isinstance(response[0], dict):
                            if obj_id_attr in response[0]:
                                id_entidad_auditoria = response[0][obj_id_attr]
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
                        for arg in args:
                            if hasattr(arg, id_param_name) and getattr(arg, id_param_name) == id_entidad_auditoria:
                                obj_afectado = arg
                                break
                        if not obj_afectado:
                               for kwarg_val in kwargs.values():
                                   if hasattr(kwarg_val, id_param_name) and getattr(kwarg_val, id_param_name) == id_entidad_auditoria:
                                       obj_afectado = kwarg_val
                                       break
                        
                if request.method == 'DELETE' and id_param_name and id_param_name in kwargs:
                    id_entidad_auditoria = kwargs[id_param_name]

                if include_obj_attrs_in_details and obj_afectado:
                    for attr_name in include_obj_attrs_in_details:
                        if hasattr(obj_afectado, attr_name):
                            attr_value = getattr(obj_afectado, attr_name)
                            if isinstance(attr_value, enum.Enum):
                                detalles[attr_name] = attr_value.value
                            else:
                                detalles[attr_name] = attr_value

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