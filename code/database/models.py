from sqlalchemy import Column, ForeignKey, Integer, String, PrimaryKeyConstraint
from code.database.database import Base

class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    short_description = Column(String, index=True)
    price = Column(String, index=True)
    developer = Column(String, index=True)
    header_image = Column(String, index=True)
    background_image = Column(String, index=True)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class AppCategory(Base):
    __tablename__ = "app_categories"

    app_id = Column(Integer, ForeignKey("apps.id"), index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), index=True)

    __table_args__ = (
        PrimaryKeyConstraint("app_id", "category_id"),  # Composite primary key
    )

class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class AppGenre(Base):
    __tablename__ = "app_genres"

    app_id = Column(Integer, ForeignKey("apps.id"), index=True)
    genre_id = Column(Integer, ForeignKey("genres.id"), index=True)

    __table_args__ = (
        PrimaryKeyConstraint("app_id", "genre_id"),  # Composite primary key
    )

class Tags(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class AppTags(Base):
    __tablename__ = "app_tags"

    app_id = Column(Integer, ForeignKey("apps.id"), index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), index=True)

    __table_args__ = (
        PrimaryKeyConstraint("app_id", "tag_id"),  # Composite primary key
    )