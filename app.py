from contextlib import suppress
from json import dump, load
from time import perf_counter

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from calculator import InvalidValue, calculate, number


class API(FastAPI):
    request_count: int = 0

    with suppress(FileNotFoundError):
        with open("./data.json", "r") as f:
            request_count = load(f).get("request_count", 0)


app = API(title="Calcium")


class InfoResponse(BaseModel):
    endpoints: list[str]
    request_count: int


@app.get("/", response_model=InfoResponse)
async def information() -> dict[str, list[str] | int]:
    """Get information about the API."""
    return {
        "endpoints": ["/calculate"],
        "request_count": app.request_count,
    }


class SuccessfulResponse(BaseModel):
    result: number
    duration: float


class APIError(BaseModel):
    detail: str


@app.get(
    "/calculate",
    summary="Make a calculation",
    response_model=SuccessfulResponse,
    responses={400: {"model": APIError}},
)
async def api_calculate(string: str) -> dict[str, number]:
    """Make a calculation."""
    app.request_count += 1
    start = perf_counter()
    result = calculate(string)
    return {"result": result, "duration": perf_counter() - start}


@app.exception_handler(InvalidValue)
async def invalid_input(request: Request, exception: InvalidValue) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exception)})


@app.on_event("shutdown")
def shutdown() -> None:
    with open("./data.json", "w") as f:
        dump({"request_count": app.request_count}, f)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
