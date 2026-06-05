
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class EncomiendaTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar datos del empleado al payload del JWT
        token['username'] = user.username
        token['email'] = user.email
        
        try:
            emp = user.empleado
            token['empleado_id'] = emp.id
            token['empleado_cod'] = emp.codigo
            token['cargo'] = emp.cargo
        except Exception:
            pass
        
        return token