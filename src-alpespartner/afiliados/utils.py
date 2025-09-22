import os

def broker_host() -> str:
    # Usa el mismo patrón que Campañas; en docker compose el servicio se llama "broker"
    return os.getenv("BROKER_HOST", "broker")
