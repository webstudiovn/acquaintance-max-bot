from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger
from sqlalchemy.dialects.postgresql import UUID
import uuid
    

class Channel(Base):
    __tablename__ = "channels"
    pk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)