"""This module contains the s3 functionality."""

from aiobotocore.session import get_session
from pydantic import AnyUrl

from backend.core.settings import settings

session = get_session()


creds = {
    "service_name": "s3",
    "endpoint_url": settings.s3_url,
    "aws_access_key_id": settings.access_key,
    "aws_secret_access_key": settings.secret_key,
}


async def upload_bytes(bucket: str, file: bytes, name: str) -> AnyUrl:
    """Загружает файл из байтов (оперативы)"""
    async with session.create_client(**creds) as s3_client:
        await s3_client.put_object(Bucket=bucket, Key=name, Body=file)
        return AnyUrl(
            await s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": name},
                ExpiresIn=36000,
            )
        )
