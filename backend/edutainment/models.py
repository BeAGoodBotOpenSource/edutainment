import uuid
from datetime import datetime

from flask import Flask
from server import db, app


with app.app_context():
    class Customer(db.Model):
        customer_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        customername = db.Column(db.String(255))
        year_of_birth = db.Column(db.Integer)
        debug = db.Column(db.Boolean, default=False)
        date_created = db.Column(db.Date, default=datetime.utcnow)

        # Relationships
        customer_sessions = db.relationship(
            "CustomerSession", backref="customer", lazy=True
        )
        customer_article_topic = db.relationship(
            "CustomerArticleTopic", backref="customer", lazy=True
        )

    class CustomerArticleTopic(db.Model):
        customer_article_topic_id = db.Column(
            db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
        )
        article_topic_id = db.Column(
            db.String(36), db.ForeignKey("article_topic.article_topic_id"), nullable=False
        )
        customer_id = db.Column(
            db.String(36), db.ForeignKey("customer.customer_id"), nullable=False
        )
        topic_expertise = db.Column(db.String(255))
        debug = db.Column(db.Boolean, default=False)
        date_created = db.Column(db.Date, default=datetime.utcnow)

        # Relationships
        article_topics = db.relationship(
            "ArticleTopic", backref="customer_article_topic", lazy=True
        )


    class CustomerSession(db.Model):
        customer_session_id = db.Column(
            db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
        )
        customer_id = db.Column(
            db.String(36), db.ForeignKey("customer.customer_id"), nullable=False
        )
        debug = db.Column(db.Boolean, default=False)
        date_created = db.Column(db.Date, default=datetime.utcnow)

        # Relationships
        lesson_completions = db.relationship(
            "LessonCompletion", backref="customer", lazy=True
        )


    class Article(db.Model):
        article_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        filename = db.Column(db.String(255), nullable=False)
        content = db.Column(db.Text, nullable=False)
        # embeddings = db.Column(db.PickleType, nullable=False)
        debug = db.Column(db.Boolean, default=False)
        date_created = db.Column(db.Date, default=datetime.utcnow)

        # Relationships
        article_topics = db.relationship("ArticleTopic", backref="article", lazy=True)


    class ArticleTopic(db.Model):
        article_topic_id = db.Column(
            db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
        )
        article_id = db.Column(
            db.String(36), db.ForeignKey("article.article_id"), nullable=False
        )
        topic_name = db.Column(db.String(255), nullable=False)
        debug = db.Column(db.Boolean, default=False)
        date_created = db.Column(db.Date, default=datetime.utcnow)

        # Relationships
        lessons = db.relationship("Lesson", backref="article_topic", lazy=True)


    class Lesson(db.Model):
        lesson_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        article_topic_id = db.Column(
            db.String(36), db.ForeignKey("article_topic.article_topic_id"), nullable=False
        )
        lesson_content = db.Column(db.Text, nullable=False)
        question = db.Column(db.Text, nullable=False)
        right_answer = db.Column(db.Text, nullable=False)
        wrong_answer = db.Column(db.Text, nullable=False)
        right_answer_explanation = db.Column(db.Text, nullable=False)
        order_num = db.Column(db.Integer, nullable=False)
        debug = db.Column(db.Boolean, default=False)
        narration_file = db.Column(db.String(256))  
        video_file = db.Column(db.String(256))  
        date_created = db.Column(db.Date, default=datetime.utcnow)

        # Relationships
        lesson_completions = db.relationship(
            "LessonCompletion", backref="lesson", lazy=True
        )


    class LessonCompletion(db.Model):
        lesson_completion_id = db.Column(
            db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
        )
        customer_session_id = db.Column(
            db.String(36),
            db.ForeignKey("customer_session.customer_session_id"),
            nullable=False,
        )
        lesson_id = db.Column(
            db.String(36), db.ForeignKey("lesson.lesson_id"), nullable=False
        )
        lesson_complete = db.Column(db.Boolean, nullable=False)
        answer_correct = db.Column(db.Boolean, nullable=False)
        debug = db.Column(db.Boolean, default=False)
        date_created = db.Column(db.Date, default=datetime.utcnow)


    # if __name__ == "__main__":
    #     db.create_all()
