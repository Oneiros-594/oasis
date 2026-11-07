from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AICharacter(Base):
    __tablename__ = "ai_characters"
    __table_args__ = (
        UniqueConstraint(
            "id",
            "owner_user_id",
            name="uq_ai_characters_id_owner_user_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    personality: Mapped[str] = mapped_column(Text, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)

    avatar_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        default="llama3.2:3b",
        nullable=False,
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )