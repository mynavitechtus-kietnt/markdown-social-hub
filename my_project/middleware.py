"""
Custom Middleware for Markdown Social Hub.
"""

import time
import logging
from django.http import JsonResponse

logger = logging.getLogger("my_project")


class RequestLoggingMiddleware:
    """
    Ghi log cho mỗi request đến API.
    - INFO cho 2xx/3xx
    - WARNING cho 4xx
    - ERROR cho 5xx
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        status_code = response.status_code

        # Chỉ log request đến /api/
        if request.path.startswith("/api/"):
            log_msg = (
                f"[{request.method}] {request.path} "
                f"→ {status_code} ({duration:.3f}s) "
                f"user={getattr(request, 'user', 'anonymous')}"
            )

            if status_code >= 500:
                logger.error(log_msg)
            elif status_code >= 400:
                logger.warning(log_msg)
            else:
                logger.info(log_msg)

        response["X-Request-Duration"] = f"{duration:.3f}s"
        return response


class GlobalExceptionMiddleware:
    """
    Bắt tất cả exception chưa được xử lý trong view.
    Ghi log ERROR với toàn bộ traceback và trả về JSON response nhất quán.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error(
            f"Unhandled exception on [{request.method}] {request.path}: "
            f"{type(exception).__name__}: {str(exception)}",
            exc_info=True,
        )

        from django.conf import settings

        return JsonResponse(
            {
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Đã xảy ra lỗi không mong đợi phía server.",
                    "detail": (
                        str(exception) if settings.DEBUG else "Internal Server Error"
                    ),
                },
            },
            status=500,
        )
