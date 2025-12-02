import logging
from common.utils import get_client_ip

logger = logging.getLogger(__name__)

class UserContextFilter(logging.Filter):
    """
    Garantit que les attributs personnalisés (user_id, username, ip)
    existent dans l'objet LogRecord, en utilisant None par défaut s'ils sont absents.
    Ceci est crucial pour éviter les KeyError dans le Formatter défini dans settings.py.
    """
    def filter(self, record):
        if not hasattr(record, 'user_id'):
            record.user_id = None
        if not hasattr(record, 'username'):
            record.username = None
        if not hasattr(record, 'username') or record.username is None or record.username == "":
            record.username = "None"
        return True

class RequestLoggingMiddleware:
    """
    Middleware pour journaliser les requêtes d'erreur avec les informations de l'utilisateur.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = None
        try:
            response = self.get_response(request)
            self.process_response(request, response)
            return response
        except Exception as e:
            self.process_exception(request, e)
            raise

    def _get_log_info(self, request):
        """Récupère les informations de l'utilisateur et l'IP."""
        user = getattr(request, 'user', None)

        return {
            'user_id': getattr(user, 'user_id', None),
            'username': getattr(user, 'username', None),
            'ip': get_client_ip(request),
        }

    def process_response(self, request, response):
        info = self._get_log_info(request)

        if getattr(request, '_exception_logged', False):
            return response

        if response.status_code >= 400:
            log_message = f"{response.status_code} {request.method} {request.get_full_path()}"

            if response.status_code < 500:
                logger.warning(log_message, extra=info)
            else:
                logger.error(log_message, extra=info)

        return response

    def process_exception(self, request, exception):
        info = self._get_log_info(request)

        logger.error(
            f"Exception: {exception} sur {request.method} {request.get_full_path()}",
            extra=info,
            exc_info=True # Indique de logger la pile d'appel complète
        )

        log_message_final = f"500 {request.method} {request.get_full_path()}"
        logger.error(log_message_final, extra=info)

        request._exception_logged = True

        return None