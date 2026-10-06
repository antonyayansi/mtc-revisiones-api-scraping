from __future__ import annotations

import re
from typing import Any

from app.captcha import solve_captcha
from app.config import settings
from app.mtc_client import CaptchaInvalidoError, MtcClient, parse_revisiones

PLACA_RE = re.compile(r"^[A-Z0-9]{5,8}$")


def normalize_placa(placa: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", placa).upper()
    if not PLACA_RE.match(cleaned):
        raise ValueError("Placa inválida. Use 5 a 8 caracteres alfanuméricos.")
    return cleaned


def consultar_revisiones(placa: str) -> dict[str, Any]:
    placa = normalize_placa(placa)
    last_error: Exception | None = None

    with MtcClient() as client:
        client.init_session()

        for attempt in range(1, settings.captcha_max_retries + 1):
            try:
                image_b64 = client.refresh_captcha()
                captcha = solve_captcha(image_b64)
                raw = client.consultar_placa(placa, captcha)
                revisiones = parse_revisiones(raw)
                return {
                    "placa": placa,
                    "total": len(revisiones),
                    "captcha_usado": captcha,
                    "intentos": attempt,
                    "revisiones": revisiones,
                }
            except CaptchaInvalidoError as exc:
                last_error = exc
                continue
            except ValueError as exc:
                # OpenAI no leyó bien el captcha; reintentar
                last_error = exc
                continue

    raise RuntimeError(
        f"No se pudo consultar la placa tras {settings.captcha_max_retries} intentos: {last_error}"
    )
