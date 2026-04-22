import sys
from typing import Literal
from pydantic import BaseModel, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import dotenv


request_reader_types = Literal['yml']
ai_client_types = Literal['claude']
transformer_types = Literal['markdown']
schedule_mode_types = Literal['daily', 'weekly', 'multi_weekly']


dotenv.load_dotenv()

class ScheduleConfig(BaseModel):
    mode: schedule_mode_types
    hour: int
    minute: int = 0
    day_of_week: int | None = None
    days_of_week: list[int] | None = None

    @model_validator(mode='after')
    def validate_days(self) -> 'ScheduleConfig':
        if self.mode == 'weekly' and self.day_of_week is None:
            raise ValueError('day_of_week is required for mode "weekly"')
        if self.mode == 'multi_weekly' and not self.days_of_week:
            raise ValueError('days_of_week is required and must be non-empty for mode "multi_weekly"')
        return self


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter='__')

    token: str
    chat_id: int
    article_count: int
    yaml_path: str
    request_reader: request_reader_types
    ai_client: ai_client_types
    transformer: transformer_types
    schedule: ScheduleConfig


try:
    CONFIG = Config()
except ValidationError as e:
    print(f'Configuration error: missing or invalid environment variables.\n{e}', file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f'Unexpected error while loading configuration: {e}', file=sys.stderr)
    sys.exit(1)
