# API Revisiones CITV

API en FastAPI que consulta las revisiones técnicas vehiculares (CITV) del MTC Perú por placa. Resuelve el captcha del portal con OpenAI Vision y reintenta si falla.

## Requisitos

- Python 3.12+
- Clave de API de OpenAI (`OPENAI_API_KEY`)

## Configuración

```bash
cp .env.example .env
# Edita .env y coloca tu OPENAI_API_KEY
```

Variables disponibles:

| Variable | Default | Descripción |
|---|---|---|
| `OPENAI_API_KEY` | — | Requerida para leer el captcha |
| `HOST` | `0.0.0.0` | Host del servidor |
| `PORT` | `8000` | Puerto del servidor |
| `CAPTCHA_MAX_RETRIES` | `3` | Reintentos si el captcha falla |

## Uso local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

La API queda en `http://localhost:8000`. Documentación interactiva: `/docs`.

## Docker

```bash
docker compose up --build -d
```

Healthcheck en `/health`.

## Endpoints

### `GET /health`

```json
{ "status": "ok" }
```

### `GET /revisiones/{placa}`

```bash
curl http://localhost:8000/revisiones/T2K867
```

### `GET /revisiones?placa=`

```bash
curl "http://localhost:8000/revisiones?placa=T2K867"
```

### `POST /revisiones`

```bash
curl -X POST http://localhost:8000/revisiones \
  -H "Content-Type: application/json" \
  -d '{"placa":"T2K867"}'
```

La placa debe tener entre 5 y 8 caracteres alfanuméricos.

### Respuesta de ejemplo

```json
{
  "placa": "T2K867",
  "total": 1,
  "captcha_usado": "123456",
  "intentos": 1,
  "revisiones": [
    {
      "placa": "T2K867",
      "nro_certificado": "...",
      "vigencia_inicio": "...",
      "vigencia_final": "...",
      "resultado": "...",
      "estado": "...",
      "centro_certificador": "...",
      "direccion": "...",
      "tipo_ambito": "...",
      "tipo_servicio": "...",
      "tipo_documento": "...",
      "observacion": "..."
    }
  ]
}
```

## Cómo funciona

1. Abre sesión en el portal CITV del MTC.
2. Obtiene el captcha y lo resuelve con OpenAI (`gpt-4o-mini` por defecto).
3. Consulta la placa y normaliza el resultado.
4. Si el captcha es inválido, reintenta hasta `CAPTCHA_MAX_RETRIES`.
