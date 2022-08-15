from datetime import datetime, timedelta

import jwt
from flask import jsonify, request
from flask_restful import Api, Resource
from werkzeug.security import check_password_hash, generate_password_hash

from src.config import BEARER_KEY
from src.middleware import token_required
from src.models import (AuthorModel, BookModel, CategoryModel, OrderModel,
                        TagModel, UserModel, db)
from src.utils import (add_bulk_data_to_instance, add_data_to_instance,
                       serialize, serialize_date)

rest_api = Api()


class AddBook(Resource):
    def post(self):
        request_data = request.get_json()

        book = BookModel()
        book.name = request_data.get("name")
        publish_date = request_data.get("publish_date")
        if publish_date:
            book.publish_date = serialize_date(publish_date)
        book.publisher = request_data.get("publisher")
        book.book_cover = request_data.get("book_cover")
        book.price = request_data.get("price")

        authors = request_data.get("authors")
        if authors is None:
            return {
                       "code": 400,
                       "success": False,
                       "message": "Add author to the book",
                   }, 400
        else:
            add_bulk_data_to_instance(book.authors, authors, AuthorModel)

        categories = request_data.get("categories")
        if categories is None:
            return {
                       "code": 400,
                       "success": False,
                       "message": "Add category to the book",
                   }, 400
        else:
            add_data_to_instance(book.categories, categories, CategoryModel)

        tags = request_data.get("tags")
        if tags is not None:
            add_data_to_instance(book.tags, tags, TagModel)

        db.session.add(book)
        db.session.commit()

        return jsonify(book.get_full_info())


class Book(Resource):
    def get(self, pk):
        book = BookModel.query.filter_by(id=pk).first()
        if book is None:
            return {"code": 404, "success": False, "message": "Book not found"}, 404

        return jsonify(book.get_full_info())

    def put(self, pk):
        book = BookModel.query.filter_by(id=pk).first()
        if not book:
            return {"code": 404, "success": False, "message": "Book not found"}, 404

        request_data = request.get_json()
        for key, value in request_data.items():
            book.__setattr__(key, value)
        db.session.commit()

        return jsonify(book.get_full_info())

    @token_required
    def delete(self, pk):
        book = BookModel.query.filter_by(id=pk).first()
        if not book:
            return {"code": 404, "success": False, "message": "Book not found."}, 404

        book_name = book.name
        db.session.delete(book)
        db.session.commit()

        return {
                   "code": 200,
                   "success": True,
                   "message": f"Book {book_name} was deleted",
               }, 200


class AddAuthor(Resource):
    def post(self):
        request_data = request.get_json()
        author = AuthorModel(**request_data)
        db.session.add(author)
        db.session.commit()

        return jsonify(serialize(author))


class AddCategory(Resource):
    def post(self):
        request_data = request.get_json()
        category = CategoryModel(**request_data)
        db.session.add(category)
        db.session.commit()

        return jsonify(serialize(category))


class AddTag(Resource):
    def post(self):
        request_data = request.get_json()
        tag = TagModel(**request_data)
        db.session.add(tag)
        db.session.commit()

        return jsonify(serialize(tag))


class SearchByAuthor(Resource):
    def get(self):
        param_value = request.args.get("author")
        authors = []
        if param_value:
            filter_data = (AuthorModel.first_name.like(f"%{param_value}%")) | (
                AuthorModel.last_name.like(f"%{param_value}%")
            )
            authors = AuthorModel.query.filter(filter_data).all()
        else:
            return {
                       "code": 400,
                       "success": False,
                       "message": "Something wrong with request",
                   }, 400

        if len(authors) == 0:
            return {"code": 404, "success": False, "message": "Authors not found"}, 404
        else:
            result = []
            for author in authors:
                if len(author.books) == 0:
                    continue
                author_data = serialize(author)
                author_data.update({"books": serialize(author.books)})
                result.append({"author": author_data})

        return jsonify(result)


class SearchByCategory(Resource):
    def get(self):
        param_value = request.args.get("category")
        categories = []
        if param_value:
            categories = CategoryModel.query.filter(CategoryModel.name.like(f"%{param_value}%")).all()
        else:
            return {
                       "code": 400,
                       "success": False,
                       "message": "Something wrong with request",
                   }, 400

        if len(categories) == 0:
            return {
                       "code": 404,
                       "success": False,
                       "message": "Categories not found",
                   }, 404
        else:
            result = []
            for category in categories:
                if len(category.books) == 0:
                    continue
                category_data = serialize(category)
                category_data.update({"books": serialize(category.books)})
                result.append({"category": category_data})

        return jsonify(result)


class SearchByTag(Resource):
    def get(self):
        param_value = request.args.get("tag")
        tags = []
        if param_value:
            tags = TagModel.query.filter(TagModel.name.like(f"%{param_value}%")).all()
        else:
            return {
                       "code": 400,
                       "success": False,
                       "message": "Something wrong with request",
                   }, 400

        if len(tags) == 0:
            return {"code": 404, "success": False, "message": "Tags not found"}, 404
        else:
            result = []
            for tag in tags:
                if len(tag.books) == 0:
                    continue
                tag_data = serialize(tag)
                tag_data.update({"books": serialize(tag.books)})
                result.append({"tag": tag_data})

        return jsonify(result)


class AddUser(Resource):
    def post(self):
        request_data = request.get_json()
        user = UserModel()
        user.first_name = request_data.get("first_name")
        user.last_name = request_data.get("last_name")
        user.birth_date = request_data.get("birth_date")
        user.username = request_data.get("username")
        user.email = request_data.get("email")
        password = request_data.get("password")
        if password:
            user.password = generate_password_hash(password)

        db.session.add(user)
        db.session.commit()

        return jsonify(serialize(user))


class User(Resource):
    def get(self, username):
        user = UserModel.query.filter_by(username=username).first()
        if user is None:
            return {"code": 404, "success": False, "message": "User not found"}, 404

        return jsonify(serialize(user))

    def put(self, username):
        user = UserModel.query.filter_by(username=username).first()
        if not user:
            return {"code": 404, "success": False, "message": "User not found"}, 404

        request_data = request.get_json()
        for key, value in request_data.items():
            if key == "password":
                value = generate_password_hash(value)
            user.__setattr__(key, value)
        db.session.commit()

        return jsonify(serialize(user))

    def delete(self, username):
        user = UserModel.query.filter_by(username=username).first()
        if not user:
            return {"code": 404, "success": False, "message": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()

        return {
                   "code": 200,
                   "success": True,
                   "message": f"User {username} was deleted",
               }, 200


class UserLogin(Resource):
    def get(self):

        username = request.args.get("username")
        password = request.args.get("password")
        if not username or not password:
            return {"code": 401, "success": False, "message": "Could not verify"}, 401

        user = UserModel.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                token = jwt.encode(
                    {"id": user.id, "exp": datetime.utcnow() + timedelta(minutes=30)},
                    BEARER_KEY,
                )
                return jsonify({"token": token})
        else:
            return {"code": 404, "success": False, "message": "User no found"}, 404

        return {"code": 401, "success": False, "message": "Wrong password"}, 401


class AddOrder(Resource):
    def post(self):
        request_data = request.get_json()
        order = OrderModel()
        order.order_number = request_data.get("order_number")
        ship_date = request_data.get("ship_date")
        if ship_date:
            order.ship_date = serialize_date(ship_date)
        order.complete = request_data.get("complete", False)

        books = request_data.get("books")
        if books is None:
            return {
                       "code": 400,
                       "success": False,
                       "message": "Add books to the order",
                   }, 400
        else:
            add_bulk_data_to_instance(order.books, books, BookModel)

        db.session.add(order)
        db.session.commit()

        order_data = serialize(order)
        order_data.update({"books": serialize(order.books)})

        return jsonify(order_data)


class Order(Resource):
    def get(self, order_number):
        order = OrderModel.query.filter_by(order_number=order_number).first()
        if order is None:
            return {"code": 404, "success": False, "message": "Order not found."}, 404

        return jsonify(serialize(order))

    def put(self, order_number):
        order = OrderModel.query.filter_by(order_number=order_number).first()
        if not order:
            return {"code": 404, "success": False, "message": "Order not found."}, 404

        request_data = request.get_json()
        for key, value in request_data.items():
            order.__setattr__(key, value)
        db.session.commit()

        return jsonify(serialize(order))

    def delete(self, order_number):
        order = OrderModel.query.filter_by(order_number=order_number).first()
        if not order:
            return {"code": 404, "success": False, "message": "Order not found."}, 404

        order_number = order.order_number
        db.session.delete(order)
        db.session.commit()

        return {
                   "code": 200,
                   "success": True,
                   "message": f"Order {order_number} was deleted",
               }, 200


rest_api.add_resource(AddBook, "/book/")
rest_api.add_resource(Book, "/book/<int:pk>")
rest_api.add_resource(SearchByAuthor, "/books/findByAuthor")
rest_api.add_resource(SearchByCategory, "/books/findByCategory")
rest_api.add_resource(SearchByTag, "/books/findByTag")
rest_api.add_resource(AddAuthor, "/author/")
rest_api.add_resource(AddCategory, "/categories/")
rest_api.add_resource(AddTag, "/tags/")
rest_api.add_resource(AddUser, "/user/")
rest_api.add_resource(UserLogin, "/user/login")
rest_api.add_resource(User, "/user/<username>")
rest_api.add_resource(AddOrder, "/order/")
rest_api.add_resource(Order, "/order/<string:order_number>")
