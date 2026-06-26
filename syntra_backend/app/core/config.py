from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY:str
    OPENROUTER_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    # Tell Pydantic to read from the .env file
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = 'utf-8',
    )

# We create a single instance of this class to use throughout our app
settings = Settings()