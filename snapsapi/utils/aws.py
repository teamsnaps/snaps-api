import logging
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import uuid
from datetime import datetime, UTC
import os


def get_file_extension(file_name: str) -> str:
    _, ext = os.path.splitext(file_name)
    return ext.lstrip('.').lower()


def build_posts_image_object_name(user_uid: str, file_name: str) -> str:
    now = datetime.now(UTC)
    ext = get_file_extension(file_name)
    return f"/media/posts/user_{user_uid}/{now:%Y/%m/%d}/{uuid.uuid4()}.{ext}"


def build_user_profile_image_object_name(user_uid: str, file_name: str) -> str:
    ext = get_file_extension(file_name)
    return f"/media/users/user_{user_uid}/{uuid.uuid4()}.{ext}"


# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
def create_presigned_post(
        bucket_name: str, object_name: str, fields=None, conditions=None, expiration=3600
):
    """Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    try:
        response = s3_client.generate_presigned_post(
            bucket_name,
            object_name,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response
