import base64
import re

from openai import OpenAI

from app.config import settings

CAPTCHA_PROMPT = (
    "Lee el captcha de esta imagen. Contiene exactamente 6 dígitos numéricos. "
    "Responde SOLO con esos 6 dígitos, sin espacios ni texto adicional."
)


def solve_captcha(image_base64: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("Falta OPENAI_API_KEY en el archivo .env")

    client = OpenAI(api_key=settings.openai_api_key)
    mime = _detect_mime(image_base64)

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": CAPTCHA_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{image_base64}",
                        },
                    },
                ],
            }
        ],
        max_tokens=20,
        temperature=0,
    )

    raw = (response.choices[0].message.content or "").strip()
    digits = re.sub(r"\D", "", raw)
    if len(digits) != 6:
        raise ValueError(f"Captcha ilegible o respuesta inválida de OpenAI: {raw!r}")
    return digits


def _detect_mime(image_base64: str) -> str:
    try:
        header = base64.b64decode(image_base64[:32])
    except Exception:
        return "image/png"
    if header.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if header.startswith(b"\x89PNG"):
        return "image/png"
    return "image/png"
