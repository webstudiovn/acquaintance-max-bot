import uuid
from sqlalchemy.types import BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Boolean
from app.database.models.base import Base

class Match(Base):
    __tablename__ = "matches"
    pk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id_1: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id_2: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # кто кому поставил match
    has_match_1_to_2: Mapped[bool] = mapped_column(Boolean, default=False)
    has_match_2_to_1: Mapped[bool] = mapped_column(Boolean, default=False)

    # отправлено ли уведомление о совпадении
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)