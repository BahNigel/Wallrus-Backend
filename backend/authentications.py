from django.contrib.auth import get_user_model, authenticate
from oauth2_provider.oauth2_validators import OAuth2Validator
from django.http import HttpRequest



USER_MODEL = get_user_model()


class CustomOAuth2Validator(OAuth2Validator): 
    """ Primarily extend the functionality of token generation """

    def validate_user(self, username, password, client, request, *args, **kwargs):
        
        try:
            email = username.split('@')
            if len(email)==1:
                user = USER_MODEL.objects.filter(phone=username)[0]
                if user.check_password(password) and user.is_active:
                    request.user = user
                    return True
        except Exception as e:
            print(e)
            print('email - password verification failed')
            pass
        http_request = HttpRequest()
        http_request.path = request.uri
        http_request.method = request.http_method
        getattr(http_request, request.http_method).update(dict(request.decoded_body))
        http_request.META = request.headers
        u = authenticate(http_request, username=username, password=password)
        if u is not None and u.is_active:
            request.user = u
            return True
        return False