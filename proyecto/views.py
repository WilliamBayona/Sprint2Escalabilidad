from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # Obtener el rol del usuario si está autenticado
    user_role = None
    if request.user.is_authenticated:
        try:
            # Intentar obtener el rol de Auth0
            auth0user = request.user.social_auth.filter(provider="auth0").first()
            if auth0user:
                # El rol puede estar en los extra_data o necesitar una consulta adicional
                user_role = auth0user.extra_data.get('https://dev-y3lnnddg1z815lbo.us.auth0.com/role', 'Usuario')
        except Exception:
            user_role = "Usuario"  # Valor por defecto si no se puede obtener
    
    return render(request, 'index.html', {'user_role': user_role})

def healthCheck(request):
    return HttpResponse("Ok")
