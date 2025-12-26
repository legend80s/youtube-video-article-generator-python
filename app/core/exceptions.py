"""
全局异常处理器
"""

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """处理 Pydantic 验证错误"""

    logger.error(f"Validation error: {exc.errors()}")

    def process_error(error: dict) -> dict:
        loc = error["loc"]
        input = error.get("input")

        return {
            "location": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"] + f" ({type(input)=})",
            "type": error["type"],
            "field": loc[-1] if loc else "unknown",
            # "input": input_val.decode()
            # if isinstance(input_val := error.get("input"), bytes)
            # else input_val,
            "input": str(input) if isinstance(input, bytes) else input,
        }

    error_details = [process_error(error) for error in exc.errors()]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "请求参数验证失败",
            "hint": "Check the `detail` field for specific errors",
            "request_id": getattr(request.state, "request_id", None),
            "detail": error_details,
        },
    )


__all__ = ["validation_exception_handler"]
