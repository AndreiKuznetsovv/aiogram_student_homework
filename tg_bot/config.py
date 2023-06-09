from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class BotConfig:
    token: str
    teacher_password: str


@dataclass
class Config:
    tg_bot: BotConfig
    db: DbConfig


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=BotConfig(
            token=env.str('BOT_TOKEN'),
            teacher_password=env.str('TEACHER_PASSWORD'),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        )
    )
