from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import settings

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/154.0.0.0 Safari/537.36"
)


class MtcClient:
    def __init__(self) -> None:
        self._client = httpx.Client(
            base_url=settings.mtc_base_url,
            timeout=settings.request_timeout,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "en-US,en;q=0.9",
            },
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> MtcClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def init_session(self) -> None:
        resp = self._client.get(
            "/Citv/ArConsultaCitv",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Upgrade-Insecure-Requests": "1",
            },
        )
        resp.raise_for_status()

    def refresh_captcha(self) -> str:
        resp = self._client.get(
            "/CITV/refrescarCaptcha",
            headers={
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Referer": f"{settings.mtc_base_url}/Citv/ArConsultaCitv",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("orStatus"):
            raise RuntimeError(f"No se pudo obtener el captcha: {data}")
        image_b64 = data.get("orResult")
        if not image_b64 or not isinstance(image_b64, str):
            raise RuntimeError("Respuesta de captcha sin imagen")
        return image_b64.strip()

    def consultar_placa(self, placa: str, captcha: str) -> dict[str, Any]:
        params = f"1|{placa.upper()}||{captcha}"
        resp = self._client.get(
            "/CITV/JrCITVConsultarFiltro",
            params={"pArrParametros": params},
            headers={
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Referer": f"{settings.mtc_base_url}/Citv/ArConsultaCitv",
            },
        )
        resp.raise_for_status()
        return resp.json()


def parse_revisiones(raw: dict[str, Any]) -> list[dict[str, Any]]:
    if raw.get("orStatus") is not True:
        codigo = raw.get("orCodigo")
        if codigo == "-1":
            raise CaptchaInvalidoError("El captcha ingresado no es válido")
        raise RuntimeError(raw.get("orCodigo") or "Error al consultar en MTC")

    or_result = raw.get("orResult")
    if not or_result or not isinstance(or_result, list) or not or_result[0]:
        return []

    items = json.loads(or_result[0])
    return [_normalize_item(item) for item in items]


def _normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "placa": item.get("PLACA"),
        "nro_certificado": item.get("NRO_CERTI"),
        "vigencia_inicio": item.get("REVISIONVIGENCIAINICIO"),
        "vigencia_final": item.get("REVISIONVIGENCIAFINAL"),
        "resultado": item.get("RESULTADO"),
        "estado": item.get("ESTADO"),
        "centro_certificador": item.get("SRAZONSOCENTCER"),
        "direccion": item.get("DIRECCION"),
        "tipo_ambito": item.get("TIPO_AMBITO"),
        "tipo_servicio": item.get("TIPO_SERVICIO"),
        "tipo_documento": item.get("TIPODOCUMENTO"),
        "observacion": item.get("OBSERVACION"),
    }


class CaptchaInvalidoError(Exception):
    pass
