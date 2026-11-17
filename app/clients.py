import boto3
from langchain_aws import ChatBedrockConverse, BedrockEmbeddings
from app.config import settings

def get_bedrock_runtime():
    return boto3.client("bedrock-runtime", region_name=settings.aws_region)

def get_s3():
    return boto3.client("s3", region_name=settings.aws_region)

def get_llm():
    return ChatBedrockConverse(
        model=settings.bedrock_chat_model,
        region_name=settings.aws_region,
        temperature=0,
        max_tokens=1800,
    )

def get_embeddings():
    return BedrockEmbeddings(
        model_id=settings.bedrock_embed_model,
        region_name=settings.aws_region,
    )

def get_table_embeddings():
    """Cohere Embed English v3 for tables and charts."""
    return BedrockEmbeddings(
        model_id=settings.bedrock_table_embed_model,
        region_name=settings.aws_region,
    )
