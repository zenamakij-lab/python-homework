import logging
import time

logger = logging.getLogger('bookstore')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()
        response = self.get_response(request)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        user_name = getattr(request.user, 'email', 'Anonymous')
        groups = ', '.join(sorted(group.name for group in getattr(request.user, 'groups', []).all())) if request.user.is_authenticated else 'Anonymous'

        logger.info(
            'Request %s %s by %s in %s ms | groups=%s | status=%s',
            request.method,
            request.path,
            user_name,
            elapsed_ms,
            groups,
            response.status_code,
        )
        return response
