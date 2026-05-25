from datetime import datetime

from common.database import Base
from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column


class Playback(Base):
    __tablename__ = "playbacks"
    # Indexet teszünk a user_id-ra és a torrent_id-ra a gyors dashboard lekérésekhez,
    # valamint a last_seen_at-re, mivel folyamatosan szűrni fogunk az időre!
    __table_args__ = (
        Index("ix_playback_user_torrent", "user_id", "torrent_id"),
        Index("ix_playback_last_seen", "last_seen_at"),
    )

    # A kliens (Stremio/Nuvio URL) által küldött UUID lesz a kulcs
    session_id: Mapped[str] = mapped_column(String(36), primary_key=True)

    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    torrent_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Opcionális, de hasznos: a User-Agent-ből kinyert kliens típus (stremio, nuvio, vlc)
    client_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Ezt frissíti minden egyes beérkező HTTP Range Request (heartbeat)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
