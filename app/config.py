from pydantic_settings import BaseSettings, SettingsConfigDict 

class Settings(BaseSettings):
    aws_region: str = "ap-south-1"
    s3_bucket: str = ""
    bedrock_chat_model: str = "apac.amazon.nova-pro-v1:0"
    bedrock_embed_model: str = "amazon.titan-embed-text-v2:0"
    bedrock_table_embed_model: str = "cohere.embed-english-v3"
    bedrock_guardrail_id: str = ""
    bedrock_guardrail_version: str = ""
    openai_api_key: str = ""
    autogen_model: str = "gpt-4o-mini"
    chroma_dir: str = "./data/chroma"
    upload_dir: str = "./data/uploads"
    max_upload_mb: int = 50
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "ResearchIQ"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
