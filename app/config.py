from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    vpc_id: str
    subnet_id: str
    ami_id: str
    key_pair_name: str  # Optional: for SSH access to the workers

    class Config:
        env_file = ".env"

settings = Settings()
