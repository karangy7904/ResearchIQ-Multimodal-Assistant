import boto3
from concurrent.futures import ThreadPoolExecutor
from langchain_aws import ChatBedrockConverse, BedrockEmbeddings
from app.config import settings

class FastBedrockEmbeddings(BedrockEmbeddings):
    """High-throughput BedrockEmbeddings that parallelizes per-chunk Bedrock Titan calls."""
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if self._inferred_provider == "cohere":
            return self._embed_cohere_documents(texts)
        if not texts:
            return []
        if len(texts) == 1:
            return [self.embed_query(texts[0])]
        with ThreadPoolExecutor(max_workers=min(len(texts), 16)) as executor:
            return list(executor.map(self.embed_query, texts))

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
    return FastBedrockEmbeddings(
        model_id=settings.bedrock_embed_model,
        region_name=settings.aws_region,
    )

def get_table_embeddings():
    """Cohere Embed English v3 for tables and charts."""
    return BedrockEmbeddings(
        model_id=settings.bedrock_table_embed_model,
        region_name=settings.aws_region,
    )
