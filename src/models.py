import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()

book_tag = db.Table(
    "book_tag",
    db.Column(
        "tag_id",
        UUID(as_uuid=True),
        db.ForeignKey("tags.id"),
        primary_key=True,
        default=uuid.uuid4(),
    ),
    db.Column(
        "book_id",
        UUID(as_uuid=True),
        db.ForeignKey("books.id"),
        primary_key=True,
        default=uuid.uuid4(),
    ),
)

book_category = db.Table(
    "book_category",
    db.Column(
        "tag_id",
        UUID(as_uuid=True),
        db.ForeignKey("categories.id"),
        primary_key=True,
        default=uuid.uuid4(),
    ),
    db.Column(
        "book_id",
        UUID(as_uuid=True),
        db.ForeignKey("books.id"),
        primary_key=True,
        default=uuid.uuid4(),
    ),
)

book_author = db.Table(
    "book_author",
    db.Column(
        "author_id",
        UUID(as_uuid=True),
        db.ForeignKey("authors.id"),
        primary_key=True,
        default=uuid.uuid4(),
    ),
    db.Column(
        "book_id",
        UUID(as_uuid=True),
        db.ForeignKey("books.id"),
        primary_key=True,
        default=uuid.uuid4(),
    ),
)

order_book = db.Table(
    "order_book",
    db.Column(
        "order_id",
        UUID(as_uuid=True),
        db.ForeignKey("orders.id"),
        primary_key=True,
        default=uuid.uuid4(),
    ),
    db.Column(
        "book_id",
        UUID(as_uuid=True),
        db.ForeignKey("books.id"),
        primary_key=True,
        default=uuid.uuid4(),
    ),
    db.Column("quantity", db.Integer(), nullable=False, default=0),
)


class BookModel(db.Model):
    __tablename__ = "books"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name = db.Column(db.String(512), nullable=False)
    author = db.relationship("AuthorModel", secondary=book_category, backref="books")
    publish_date = db.Column(db.Date, nullable=False)
    publisher = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text())
    category = db.relationship(
        "CategoryModel", secondary=book_category, backref="books"
    )
    tags = db.relationship("TagModel", secondary=book_tag, backref="books")
    book_cover = db.Column(db.LargeBinary, nullable=False)
    price = db.Column(db.Float(), nullable=False, default=0)

    def __init__(self, name, author):
        self.name = name
        self.email = author

    def __repr__(self):
        return f'{self.author + " - " + self.name}'


class BaseUserModel(db.Model):
    __abstract__ = True
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    birth_date = db.Column(db.Date)

    def __init__(self, first_name, last_name, birth_date):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date

    def __repr__(self):
        return f'{self.first_name + " " + self.last_name}'


class AuthorModel(BaseUserModel):
    __tablename__ = "authors"
    bio = db.Column(db.Text())


class UserModel(BaseUserModel):
    __tablename__ = "users"
    email = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(128))


class TagModel(db.Model):
    __tablename__ = "tags"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name = db.Column(db.String(128), unique=True, nullable=False)


class CategoryModel(db.Model):
    __tablename__ = "categories"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    name = db.Column(db.String(128), unique=True, nullable=False)


class OrderModel(db.Model):
    __tablename__ = "orders"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    order_number = db.Column(db.String(128), unique=True, nullable=False)
    book = db.relationship("BookModel", secondary=order_book, backref="orders")
    ship_date = db.Column(db.Date, nullable=False)
    complete = db.Column(db.Boolean)
