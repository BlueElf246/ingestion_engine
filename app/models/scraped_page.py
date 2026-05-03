from sqlalchemy import Column, Integer, MetaData, Table, Text, TIMESTAMP, func

metadata = MetaData()

scraped_pages = Table(
    "scraped_pages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("url", Text, nullable=False, unique=True),
    Column("title", Text),
    Column("content", Text),
    Column(
        "scraped_at",
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
)
