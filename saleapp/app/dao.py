from app.models import Category, Book, User
from app import app, db
import hashlib
import cloudinary.uploader
from datetime import datetime, timedelta


def load_categories():
    return Category.query.order_by('id').all()


def load_books(cate_id=None, kw=None, page=1):
    query = Book.query

    if kw:
        query = query.filter(Book.title.contains(kw))

    if cate_id:
        query = query.filter(Book.category_id == cate_id)

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    return query.all()


def import_books(staff_id, books_data):
    # Check minimum total import quantity
    total_import_quantity = sum(b['quantity'] for b in books_data)
    if total_import_quantity < 150:
        return False, "Minimum import quantity must be 150"

    # Validate each book's current quantity
    for book_data in books_data:
        book = Book.query.get(book_data['book_id'])
        if not book:
            return False, f"Book with id {book_data['book_id']} not found"

        # Check if current book quantity is already 300 or more
        if book.quantity >= 300:
            return False, f"Cannot import book '{book.title}' - current quantity ({book.quantity}) is already 300 or more"

        # Check if import would exceed 300 limit
        new_quantity = book.quantity + book_data['quantity']
        if new_quantity > 300:
            return False, f"Cannot import {book_data['quantity']} units of '{book.title}' - would exceed 300 limit (current: {book.quantity})"


def count_books():
    return Book.query.count()


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_user(name, username, password, avatar=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User(name=name, username=username, password=password)
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()
