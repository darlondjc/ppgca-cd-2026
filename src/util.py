import os
from dotenv import load_dotenv
from datetime import datetime, timezone


def normalize_datetime(valor: str) -> datetime:
    dt = datetime.fromisoformat(valor)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def load_api_variables():
    load_dotenv()  # carrega .env para os.environ
    api_key = os.getenv("API_KEY", "").strip()
    api_base_url = os.getenv("API_BASE_URL", "").strip()

    if not api_base_url:
        raise EnvironmentError(
            "Variável de ambiente API_BASE_URL é obrigatória e deve estar preenchida"
        )

    # if not api_key:
    #     print("API_KEY não informada. Seguindo sem header de autenticação.")

    return api_key, api_base_url