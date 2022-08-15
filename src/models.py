from flask_sqlalchemy import SQLAlchemy

from src.utils import serialize

db = SQLAlchemy()

book_tag = db.Table(
    "book_tag",
    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id"),
        primary_key=True,
    ),
    db.Column(
        "book_id",
        db.Integer,
        db.ForeignKey("books.id"),
        primary_key=True,
    ),
)

book_category = db.Table(
    "book_category",
    db.Column(
        "category_id",
        db.Integer,
        db.ForeignKey("categories.id"),
        primary_key=True,
    ),
    db.Column(
        "book_id",
        db.Integer,
        db.ForeignKey("books.id"),
        primary_key=True,
    ),
)

book_author = db.Table(
    "book_author",
    db.Column(
        "author_id",
        db.Integer,
        db.ForeignKey("authors.id"),
        primary_key=True,
    ),
    db.Column(
        "book_id",
        db.Integer,
        db.ForeignKey("books.id"),
        primary_key=True,
    ),
)

order_book = db.Table(
    "order_book",
    db.Column(
        "order_id",
        db.Integer,
        db.ForeignKey("orders.id"),
        primary_key=True,
    ),
    db.Column(
        "book_id",
        db.Integer,
        db.ForeignKey("books.id"),
        primary_key=True,
    ),
)


class BookModel(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    authors = db.relationship("AuthorModel", secondary=book_author, backref="books")
    publish_date = db.Column(db.Date, nullable=False)
    publisher = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text())
    categories = db.relationship("CategoryModel", secondary=book_category, backref="books")
    tags = db.relationship("TagModel", secondary=book_tag, backref="books")
    price = db.Column(db.Float())

    def get_full_info(self):
        book_data = serialize(self)
        book_data.update({"authors": serialize(self.authors)})
        book_data.update({"categories": serialize(self.categories)})
        book_data.update({"tags": serialize(self.tags)})
        return book_data


class BaseUserModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(256), nullable=False)
    birth_date = db.Column(db.Date)


class AuthorModel(BaseUserModel):
    __tablename__ = "authors"
    bio = db.Column(db.Text())


class UserModel(BaseUserModel):
    __tablename__ = "users"
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(128))


class TagModel(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)


class CategoryModel(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)


class OrderModel(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(128), unique=True, nullable=False)
    books = db.relationship("BookModel", secondary=order_book, backref="orders")
    ship_date = db.Column(db.Date, nullable=False)
    complete = db.Column(db.Boolean, default=False)
