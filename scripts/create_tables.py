#!/usr/bin/env python3
"""Script to create DynamoDB tables for the application.

This script creates the necessary tables for local development or AWS deployment.
"""

import sys

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)


def create_users_table() -> bool:
    """Create the users table in DynamoDB.

    Returns:
        bool: True if table was created, False if it already exists.
    """
    try:
        # Configure DynamoDB client
        config = {
            "region_name": settings.aws_region,
        }

        if settings.aws_access_key_id and settings.aws_secret_access_key:
            config["aws_access_key_id"] = settings.aws_access_key_id
            config["aws_secret_access_key"] = settings.aws_secret_access_key

        if settings.dynamodb_endpoint_url:
            config["endpoint_url"] = settings.dynamodb_endpoint_url

        dynamodb = boto3.resource("dynamodb", **config)

        # Check if table exists
        existing_tables = list(dynamodb.tables.all())
        existing_table_names = [table.name for table in existing_tables]

        if settings.dynamodb_users_table in existing_table_names:
            logger.info(
                "table_already_exists",
                table_name=settings.dynamodb_users_table,
            )
            print(f"✅ Table '{settings.dynamodb_users_table}' already exists")
            return False

        # Create table
        table = dynamodb.create_table(
            TableName=settings.dynamodb_users_table,
            KeySchema=[
                {"AttributeName": "email", "KeyType": "HASH"},  # Partition key
            ],
            AttributeDefinitions=[
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",  # On-demand billing
        )

        # Wait for table to be created
        table.meta.client.get_waiter("table_exists").wait(TableName=settings.dynamodb_users_table)

        logger.info(
            "table_created_successfully",
            table_name=settings.dynamodb_users_table,
            status=table.table_status,
        )

        print(f"✅ Table '{settings.dynamodb_users_table}' created successfully")
        return True

    except ClientError as e:
        logger.error(
            "table_creation_failed",
            table_name=settings.dynamodb_users_table,
            error=str(e),
        )
        print(f"❌ Error creating table: {e}")
        return False

    except Exception as e:
        logger.error(
            "unexpected_error",
            error=str(e),
        )
        print(f"❌ Unexpected error: {e}")
        return False


def create_analysis_table() -> bool:
    """Create the image analysis table in DynamoDB.

    Returns:
        bool: True if table was created, False if it already exists.
    """
    try:
        # Configure DynamoDB client
        config = {
            "region_name": settings.aws_region,
        }

        if settings.aws_access_key_id and settings.aws_secret_access_key:
            config["aws_access_key_id"] = settings.aws_access_key_id
            config["aws_secret_access_key"] = settings.aws_secret_access_key

        if settings.dynamodb_endpoint_url:
            config["endpoint_url"] = settings.dynamodb_endpoint_url

        dynamodb = boto3.resource("dynamodb", **config)

        # Check if table exists
        existing_tables = list(dynamodb.tables.all())
        existing_table_names = [table.name for table in existing_tables]

        if settings.dynamodb_analysis_table in existing_table_names:
            logger.info(
                "table_already_exists",
                table_name=settings.dynamodb_analysis_table,
            )
            print(f"✅ Table '{settings.dynamodb_analysis_table}' already exists")
            return False

        # Create table
        table = dynamodb.create_table(
            TableName=settings.dynamodb_analysis_table,
            KeySchema=[
                {"AttributeName": "analysis_id", "KeyType": "HASH"},  # Partition key
            ],
            AttributeDefinitions=[
                {"AttributeName": "analysis_id", "AttributeType": "S"},
                {"AttributeName": "user_email", "AttributeType": "S"},
                {"AttributeName": "analyzed_at_timestamp", "AttributeType": "N"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "user_email-index",
                    "KeySchema": [
                        {"AttributeName": "user_email", "KeyType": "HASH"},
                        {"AttributeName": "analyzed_at_timestamp", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",  # On-demand billing
        )

        # Wait for table to be created
        table.meta.client.get_waiter("table_exists").wait(TableName=settings.dynamodb_analysis_table)

        logger.info(
            "table_created_successfully",
            table_name=settings.dynamodb_analysis_table,
            status=table.table_status,
        )

        print(f"✅ Table '{settings.dynamodb_analysis_table}' created successfully")
        return True

    except ClientError as e:
        logger.error(
            "table_creation_failed",
            table_name=settings.dynamodb_analysis_table,
            error=str(e),
        )
        print(f"❌ Error creating table: {e}")
        return False

    except Exception as e:
        logger.error(
            "unexpected_error",
            error=str(e),
        )
        print(f"❌ Unexpected error: {e}")
        return False


def main() -> int:
    """Main function to create all tables.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    print("🚀 Creating DynamoDB tables...")
    print(f"📍 Region: {settings.aws_region}")
    print(f"📍 Endpoint: {settings.dynamodb_endpoint_url or 'AWS DynamoDB'}")
    print(f"📍 Users Table: {settings.dynamodb_users_table}")
    print(f"📍 Analysis Table: {settings.dynamodb_analysis_table}")
    print()

    users_success = create_users_table()
    analysis_success = create_analysis_table()

    print()
    if users_success or analysis_success:
        print("✅ All tables created successfully!")
        return 0
    else:
        print("⚠️  All tables already existed or creation failed")
        return 0  # Still return 0 if tables exist


if __name__ == "__main__":
    sys.exit(main())
