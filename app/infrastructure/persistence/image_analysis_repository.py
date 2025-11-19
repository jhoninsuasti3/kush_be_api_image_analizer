"""DynamoDB implementation of IImageAnalysisRepository.

This module provides the concrete implementation of the image analysis repository
using AWS DynamoDB as the persistence layer.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from boto3.dynamodb.conditions import Key

from app.core.exceptions import DatabaseException
from app.core.logging import get_logger
from app.domain.models import ImageAnalysis, Tag
from app.domain.ports import IImageAnalysisRepository
from app.infrastructure.persistence.dynamodb_client import get_analysis_table

logger = get_logger(__name__)


class DynamoDBImageAnalysisRepository(IImageAnalysisRepository):
    """DynamoDB implementation of the image analysis repository.

    This class provides CRUD operations for image analysis records using DynamoDB
    as the persistence layer.
    """

    def __init__(self, table: Any | None = None) -> None:
        """Initialize the repository with a DynamoDB table."""
        self.table = table or get_analysis_table()

    def create(self, analysis: ImageAnalysis) -> ImageAnalysis:
        """Create a new image analysis record in DynamoDB.

        Args:
            analysis: The analysis record to create.

        Returns:
            ImageAnalysis: The created analysis record.

        Raises:
            DatabaseException: If database operation fails.
        """
        try:
            # Prepare item for DynamoDB
            # Convert tags to dict format for DynamoDB
            tags_dict = [{"label": tag.label, "confidence": Decimal(str(tag.confidence))} for tag in analysis.tags]

            item = {
                "analysis_id": analysis.analysis_id,
                "user_email": analysis.user_email,
                "file_name": analysis.file_name,
                "file_size": analysis.file_size,
                "content_type": analysis.content_type,
                "tags": tags_dict,
                "analyzed_at": analysis.analyzed_at.isoformat(),
                # Unix timestamp for sorting (DynamoDB Sort Key)
                "analyzed_at_timestamp": int(analysis.analyzed_at.timestamp()),
            }

            # Put item in DynamoDB
            self.table.put_item(Item=item)

            logger.info(
                "analysis_record_created",
                analysis_id=analysis.analysis_id,
                user_email=analysis.user_email,
                tags_count=len(analysis.tags),
            )
            return analysis

        except Exception as e:
            logger.error("analysis_create_failed", analysis_id=analysis.analysis_id, error=str(e))
            raise DatabaseException(f"Failed to create analysis record: {e}") from e

    def get_by_id(self, analysis_id: str) -> ImageAnalysis | None:
        """Get an analysis record by ID from DynamoDB.

        Args:
            analysis_id: The unique analysis identifier.

        Returns:
            ImageAnalysis | None: The analysis record if found, None otherwise.

        Raises:
            DatabaseException: If database operation fails.
        """
        try:
            response = self.table.get_item(Key={"analysis_id": analysis_id})

            if "Item" not in response:
                logger.debug("analysis_not_found", analysis_id=analysis_id)
                return None

            item = response["Item"]
            return self._item_to_analysis(item)

        except Exception as e:
            logger.error("analysis_get_failed", analysis_id=analysis_id, error=str(e))
            raise DatabaseException(f"Failed to get analysis record: {e}") from e

    def get_by_user_email(self, user_email: str, limit: int = 10) -> list[ImageAnalysis]:
        """Get analysis records for a specific user.

        Args:
            user_email: The user's email address.
            limit: Maximum number of records to return (default: 10).

        Returns:
            list[ImageAnalysis]: List of analysis records, ordered by analyzed_at descending.

        Raises:
            DatabaseException: If database operation fails.
        """
        try:
            # Query using GSI (Global Secondary Index) on user_email
            response = self.table.query(
                IndexName="user_email-index",
                KeyConditionExpression=Key("user_email").eq(user_email),
                ScanIndexForward=False,  # Sort descending (newest first)
                Limit=limit,
            )

            items = response.get("Items", [])
            analyses = [self._item_to_analysis(item) for item in items]

            logger.debug("analyses_retrieved_for_user", user_email=user_email, count=len(analyses))
            return analyses

        except Exception as e:
            logger.error("analyses_get_by_user_failed", user_email=user_email, error=str(e))
            raise DatabaseException(f"Failed to get analyses for user: {e}") from e

    def delete(self, analysis_id: str) -> bool:
        """Delete an analysis record by ID from DynamoDB.

        Args:
            analysis_id: The unique analysis identifier.

        Returns:
            bool: True if the record was deleted, False if not found.

        Raises:
            DatabaseException: If database operation fails.
        """
        try:
            # Check if analysis exists before deleting
            existing = self.get_by_id(analysis_id)
            if not existing:
                logger.debug("analysis_not_found_for_delete", analysis_id=analysis_id)
                return False

            # Delete item from DynamoDB
            self.table.delete_item(Key={"analysis_id": analysis_id})

            logger.info("analysis_deleted", analysis_id=analysis_id)
            return True

        except Exception as e:
            logger.error("analysis_delete_failed", analysis_id=analysis_id, error=str(e))
            raise DatabaseException(f"Failed to delete analysis record: {e}") from e

    def _item_to_analysis(self, item: dict[str, Any]) -> ImageAnalysis:
        """Convert DynamoDB item to ImageAnalysis model.

        Args:
            item: DynamoDB item dictionary.

        Returns:
            ImageAnalysis: The converted analysis model.
        """
        # Convert tags from DynamoDB format (with Decimal) to Tag model
        tags = [Tag(label=tag["label"], confidence=float(tag["confidence"])) for tag in item["tags"]]

        return ImageAnalysis(
            analysis_id=item["analysis_id"],
            user_email=item["user_email"],
            file_name=item["file_name"],
            file_size=item["file_size"],
            content_type=item["content_type"],
            tags=tags,
            analyzed_at=datetime.fromisoformat(item["analyzed_at"]),
        )
