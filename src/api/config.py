from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_url: str = "sqlite:///database.db"
    test_db_url:str
    testing: bool = False

    model_config = SettingsConfigDict(env_file=".dev.env")
    def get_db_url(self):
        if self.testing:
            return self.test_db_url
        return self.db_url

settings = Settings()