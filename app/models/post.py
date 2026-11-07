
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

if TYPE_CHECKING:
    from app.models.ai_character import AICharacter
    from app.models.user import User


class PostStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending_approval"
    PUBLISHED = "published"
    REJECTED = "rejected"


class PostVisibility(str, Enum):
    PUBLIC = "public"
    FOLLOWERS = "followers"
    PRIVATE = "private"


class Post(Base):
    __tablename__ = "posts"

    __table_args__ = (
        CheckConstraint(
            """
            (author_user_id IS NOT NULL AND author_character_id IS NULL)
            OR
            (author_user_id IS NULL AND author_character_id IS NOT NULL)
            """,
            name="ck_posts_exactly_one_author",
        ),
        CheckConstraint(
            """
            (generated_by_ai = FALSE)
            OR
            (author_character_id IS NOT NULL)
            """,
            name="ck_posts_ai_author_consistency",
        ),
        CheckConstraint(
            """
            status IN ('draft', 'pending_approval', 'published', 'rejected')
            """,
            name="ck_posts_status",
        ),
        CheckConstraint(
            """
            visibility IN ('public', 'followers', 'private')
            """,
            name="ck_posts_visibility",
        ),
        CheckConstraint(
            """
            (approved_by IS NULL AND approved_at IS NULL)
            OR
            (
                author_character_id IS NOT NULL
                AND status = 'published'
                AND approved_by IS NOT NULL
                AND approved_at IS NOT NULL
            )
            """,
            name="ck_posts_approval_pair",
        ),
        CheckConstraint(
            """
            (author_character_id IS NULL)
            OR
            (status != 'published')
            OR
            (approved_by IS NOT NULL AND approved_at IS NOT NULL)
            """,
            name="ck_posts_character_publication_approval",
        ),
        ForeignKeyConstraint(
            ["author_character_id", "approved_by"],
            ["ai_characters.id", "ai_characters.owner_user_id"],
            name="fk_posts_approval_owner",
            ondelete="RESTRICT",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    author_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    author_character_id: Mapped[int | None] = mapped_column(
        ForeignKey("ai_characters.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    status: Mapped[PostStatus] = mapped_column(
        String(30),
        default=PostStatus.DRAFT,
        nullable=False,
    )

    visibility: Mapped[PostVisibility] = mapped_column(
        String(20),
        default=PostVisibility.PUBLIC,
        nullable=False,
    )

    generated_by_ai: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    approved_by: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def submit_for_approval(self) -> None:
        if self.author_character_id is None or not self.generated_by_ai:
            raise ValueError("Only AI-generated character posts can be submitted")
        if self.status not in (None, PostStatus.DRAFT):
            raise ValueError("Only draft posts can be submitted for approval")

        self.status = PostStatus.PENDING

    def publish_by_human(self, author: User) -> None:
        if self.author_user_id != author.id or self.author_character_id is not None:
            raise PermissionError("Only the human author can publish this post")
        if self.status not in (None, PostStatus.DRAFT):
            raise ValueError("Only draft posts can be published directly")

        self.status = PostStatus.PUBLISHED

    def approve_by_owner(
        self,
        approver: User,
        character: AICharacter,
    ) -> None:
        if not self.generated_by_ai:
            raise ValueError("Only AI-generated posts can be approved")
        self._require_character_owner(approver, character)
        if self.status != PostStatus.PENDING:
            raise ValueError("Only pending posts can be approved")

        self.approved_by = approver.id
        self.approved_at = datetime.now(timezone.utc)
        self.status = PostStatus.PUBLISHED

    def reject_by_owner(
        self,
        approver: User,
        character: AICharacter,
    ) -> None:
        self._require_character_owner(approver, character)
        if self.status != PostStatus.PENDING:
            raise ValueError("Only pending posts can be rejected")

        self.status = PostStatus.REJECTED

    def _require_character_owner(
        self,
        approver: User,
        character: AICharacter,
    ) -> None:
        if self.author_character_id != character.id:
            raise ValueError("The character does not own this post")
        if character.owner_user_id != approver.id:
            raise PermissionError("Only the character owner can approve this post")
