from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="CONDOMINIO",
    settings_files=["settings.toml", ".secrets.toml"],
    validators=[
        Validator('CPF', default=''),
        Validator('SENHA', default=''),
        Validator('NOME', default=''),
        Validator('DEST_PATH', default='/tmp/'),
    ],
)
