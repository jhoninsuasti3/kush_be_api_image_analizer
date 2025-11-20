"""DynamoDB client configuration and initialization.

This module provides a configured DynamoDB client for the application.
Supports both AWS DynamoDB and DynamoDB Local for development.
"""

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.exceptions import DatabaseConnectionException
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_dynamodb_resource():  # type: ignore[no-untyped-def]
    """Get a configured DynamoDB resource.

    Returns:
        DynamoDB resource instance.

    Raises:
        DatabaseConnectionException: If connection to DynamoDB fails.

    Example:
        >>> dynamodb = get_dynamodb_resource()
        >>> table = dynamodb.Table('users')
    """
    try:
        # Configuration for DynamoDB
        config = {
            "region_name": settings.aws_region,
        }

        # Add credentials if provided (for local development)
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            config["aws_access_key_id"] = settings.aws_access_key_id
            config["aws_secret_access_key"] = settings.aws_secret_access_key

        # Add endpoint URL if provided (for DynamoDB Local)
        if settings.dynamodb_endpoint_url:
            config["endpoint_url"] = settings.dynamodb_endpoint_url
            logger.info(
                "dynamodb_local_connection",
                endpoint=settings.dynamodb_endpoint_url,
            )

        dynamodb = boto3.resource("dynamodb", **config)

        # Test connection
        try:
            list(dynamodb.tables.all())
            logger.info("dynamodb_connected", region=settings.aws_region)
        except Exception as e:
            logger.error("dynamodb_connection_test_failed", error=str(e))
            raise

        return dynamodb

    except Exception as e:
        logger.error("dynamodb_connection_failed", error=str(e))
        raise DatabaseConnectionException(f"Failed to connect to DynamoDB: {e}") from e


def get_users_table():  # type: ignore[no-untyped-def]
    """Get the users table.

    Returns:
        DynamoDB users table resource.

    Raises:
        DatabaseConnectionException: If table doesn't exist or connection fails.
    """
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(settings.dynamodb_users_table)

        # Verify table exists by loading its metadata
        table.load()

        logger.debug(
            "users_table_loaded",
            table_name=settings.dynamodb_users_table,
            status=table.table_status,
        )

        return table

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            error_msg = f"Table '{settings.dynamodb_users_table}' not found"
            logger.error("users_table_not_found", table_name=settings.dynamodb_users_table)
            raise DatabaseConnectionException(error_msg) from e
        raise
    except Exception as e:
        logger.error("users_table_load_failed", error=str(e))
        raise DatabaseConnectionException(f"Failed to load users table: {e}") from e


def get_analysis_table():  # type: ignore[no-untyped-def]
    """Get the image analysis table.

    Returns:
        DynamoDB image analysis table resource.

    Raises:
        DatabaseConnectionException: If table doesn't exist or connection fails.
    """
    try:
        dynamodb = get_dynamodb_resource()
        table_name = settings.dynamodb_analysis_table
        table = dynamodb.Table(table_name)

        # Verify table exists by loading its metadata
        table.load()

        logger.debug(
            "analysis_table_loaded",
            table_name=table_name,
            status=table.table_status,
        )

        return table

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            error_msg = f"Table '{settings.dynamodb_analysis_table}' not found"
            logger.error("analysis_table_not_found", table_name=settings.dynamodb_analysis_table)
            raise DatabaseConnectionException(error_msg) from e
        raise
    except Exception as e:
        logger.error("analysis_table_load_failed", error=str(e))
        raise DatabaseConnectionException(f"Failed to load analysis table: {e}") from e
