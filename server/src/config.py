from pathlib import Path

from dynaconf import Dynaconf, Validator


CURRENT_PATH = Path(__file__).parent

settings = Dynaconf(
    envvar_prefix="CONDOMINIO",
    settings_files=["settings.toml", f"{CURRENT_PATH}/.secrets.toml"],
    validators=[
        Validator('CPF', default=''),
        Validator('SENHA', default=''),
        Validator('NOME', default=''),
        Validator('DEST_PATH', default='/tmp/'),
    ],
)
