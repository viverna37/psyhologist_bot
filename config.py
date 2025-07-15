from dataclasses import dataclass
from environs import Env



@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    order_channel: int
    review_channel: int
    review_admin_channel: int

@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: int

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig

def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            order_channel=int(env.str("ORDER_CHANNEL")),
            review_channel=int(env.str("REVIEW_CHANNEL")),
            review_admin_channel=int(env.str("REVIEW_ADMIN_CHANNEL")),
        ),
        db=DbConfig(
            host=env.str("POSTGRESQL_HOST"),
            password=env.str("POSTGRESQL_PASSWORD"),
            user=env.str("POSTGRESQL_LOGIN"),
            database=env.str("POSTGRESQL_DATABASE"),
            port=env.int("POSTGRESQL_PORT")
        )
    )
