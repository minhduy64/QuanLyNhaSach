from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Enum, DateTime
from sqlalchemy.orm import relationship
from app import db, app
from enum import Enum as RoleEnum
from flask_login import UserMixin
from datetime import datetime


class UserRole(RoleEnum):
    ADMIN = 1
    STAFF = 2
    CUSTOMER = 3


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dehkjrhjw/image/upload/v1732357374/admin_ezrocx.jpg')
    user_role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    # Add relationships
    book_imports = relationship('BookImport', backref='staff', lazy=True)
    orders = relationship('Order', backref='customer', lazy=True)


class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True)
    books = relationship('Book', backref='category', lazy=True)

    def __str__(self):
        return self.name


class Book(db.Model):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, default=0)
    image = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    quantity_in_stock = Column(Integer, default=0)

    # Add relationships
    import_details = relationship('BookImportDetail', backref='book', lazy=True)
    order_details = relationship('OrderDetail', backref='book', lazy=True)

    def __str__(self):
        return self.title


class BookImport(db.Model):
    __tablename__ = 'book_import'

    id = Column(Integer, primary_key=True, autoincrement=True)
    import_date = Column(DateTime, default=datetime.now, nullable=False)
    staff_id = Column(Integer, ForeignKey(User.id), nullable=False)
    total_quantity = Column(Integer, default=0)
    notes = Column(String(255))

    # Relationship with import details
    details = relationship('BookImportDetail', backref='import_receipt', lazy=True,
                           cascade="all, delete-orphan")

    def calculate_total_quantity(self):
        self.total_quantity = sum(detail.quantity for detail in self.details)


class BookImportDetail(db.Model):
    __tablename__ = 'book_import_detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    import_id = Column(Integer, ForeignKey('book_import.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    quantity = Column(Integer, nullable=False)  # Số lượng

    def update_book_stock(self):
        if self.book:
            self.book.quantity_in_stock += self.quantity


class Order(db.Model):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey(User.id), nullable=False)
    order_date = Column(DateTime, default=datetime.now().date())
    status = Column(String(20), default='pending')  # pending, paid, cancelled
    payment_method = Column(String(20))  # online, offline

    # Relationship with order details
    details = relationship('OrderDetail', backref='order', lazy=True,
                           cascade="all, delete-orphan")


class OrderDetail(db.Model):
    __tablename__ = 'order_detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    def update_book_stock(self):
        if self.book:
            self.book.quantity_in_stock -= self.quantity


def init_db():
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            import hashlib
            admin = User(
                name='admin',
                username='admin',
                password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                user_role=UserRole.ADMIN
            )
            db.session.add(admin)


        categories = ['Văn học', 'Kỹ năng sống', 'Kinh tế', 'Thiếu nhi']
        for cate_name in categories:
            if not Category.query.filter_by(name=cate_name).first():
                category = Category(name=cate_name)
                db.session.add(category)

        books = [
            {
                "title": "Nhà Giả Kim",
                "author": "Paulo Coelho",
                "image": "https://res.cloudinary.com/dehkjrhjw/image/upload/v1732361940/nhagiakim_cnfihh.jpg",
                "category_id": 1,
                "quantity_in_stock": 50,
                "price": 88000
            },
            {
                "title": "Đắc Nhân Tâm",
                "author": "Dale Carnegie",
                "category_id": 2,
                "quantity_in_stock": 100,
                "price": 76000
            },
            {
                "title": "Think and Grow Rich",
                "author": "Napoleon Hill",
                "category_id": 3,
                "quantity_in_stock": 75,
                "price": 120000
            },
            {
                "title": "Doraemon Tập 1",
                "author": "Fujiko F. Fujio",
                "category_id": 4,
                "quantity_in_stock": 150,
                "price": 25000
            }
        ]

        for book_data in books:
            book = Book(**book_data)
            db.session.add(book)

        db.session.commit()


if __name__ == '__main__':
    init_db()
