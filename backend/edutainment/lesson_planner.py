import datetime
import logging
import os
import traceback

import sqlalchemy
from dotenv import find_dotenv, load_dotenv
from flask import Flask

from edutainment.models import Customer, CustomerSession, Article, ArticleTopic, CustomerArticleTopic, Lesson, LessonCompletion

from edutainment.narration import get_narration
from edutainment.text import GPTLessonText
from server import app, db

logger = logging.getLogger(__name__)

with app.app_context():
    metadata = db.MetaData()
    metadata.reflect(bind=db.engine)
    
    article_topics = db.Table("article_topics", metadata)
    articles = db.Table("articles", metadata)
    lesson_completions = db.Table("lesson_completions", metadata)
    lessons = db.Table("lessons", metadata)
    user_article_topics = db.Table("user_article_topics", metadata)
    user_sessions = db.Table("user_sessions", metadata)
    users = db.Table("users", metadata)

    def get_or_create(session, model, **kwargs):
        # Exclude primary key fields from the filter_by method
        filter_args = {k: v for k, v in kwargs.items() if not k.endswith('_id')}
        
        instance = session.query(model).filter_by(**filter_args).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            session.add(instance)
            try:
                session.flush()
            except sqlalchemy.exc.IntegrityError:
                session.rollback()
                # Re-query the database to get the existing instance
                instance = session.query(model).filter_by(**filter_args).first()
                if instance is None:
                    # If instance is still None, raise the original IntegrityError
                    raise
            return instance


    def to_dict(obj):
        return {
            c.key: getattr(obj, c.key) for c in sqlalchemy.inspect(obj).mapper.column_attrs
        }


    class LessonPlan:
        """Represents an entire LessonPlan, including text, audio, and video

        TODO: allow article search by session? Article ID?
        TODO: asynchronous processing?
        """

        def __init__(
            self,
            session_id: str,
            article_filename: str,  # TODO: handle missing article
            article_text: str,  # TODO: handle missing article
            age: int = None,
            debug: bool = False,
        ) -> None:
            with app.app_context():
                try:
                    with db.session.begin():
                        self.debug = debug
                        self.customer = get_or_create(
                            db.session,
                            Customer,
                            customer_id=session_id,
                            debug=self.debug,
                        )
                        self.customer.year_of_birth = datetime.date.today().year - age if age else None

                        self.customer_session = get_or_create(
                            db.session,
                            CustomerSession,
                            customer_session_id=session_id,
                            customer_id=self.customer.customer_id,
                            debug=self.debug,
                        )

                        self.article = get_or_create(
                            db.session,
                            Article,
                            filename=article_filename,
                            content=article_text,
                            debug=self.debug,
                        )
                        self.text_generator = GPTLessonText(article_text)
                        logging.info("Attempting to commit to the database.")
                    db.session.commit()
                    saved_customer = db.session.query(Customer).get(self.customer.customer_id)
                    if not saved_customer:
                        logging.error("Customer not saved in __init__")
                    logging.info("Commit successful.")
                except Exception as e:
                    logging.error(f"Database commit failed in __init__: {e}")
                    db.session.rollback()


        def get_topics(self):
            """Return list of topics"""
            with app.app_context():
                try:
                    with db.session.begin():
                        self.article = db.session.merge(self.article)
                        self.topics = self.text_generator.get_topics()
                        for t in self.topics:
                            _ = get_or_create(
                                db.session,
                                ArticleTopic,
                                article_id=self.article.article_id,
                                topic_name=t,
                                debug=self.debug,
                            )
                        db.session.commit()
                        return self.topics
                except Exception as e:
                    logging.error(f"Database commit failed in get_topics: {e}")
                    db.session.rollback()

        def get_lessons(self, topic_name: str, topic_expertise: str = "intermediate"):
            with app.app_context():
                try:
                    with db.session.begin():
                        # Fetch the topic
                        topic = db.session.query(ArticleTopic).filter_by(topic_name=topic_name).first()

                        # Create the topic if it does not exist
                        if not topic:
                            topic = get_or_create(
                                db.session,
                                ArticleTopic,
                                article_id=self.article.article_id,
                                topic_name=topic_name,
                                debug=self.debug,
                            )

                        # Fetch or create the CustomerArticleTopic entry
                        customer_artice_topic = get_or_create(
                            db.session,
                            CustomerArticleTopic,
                            article_topic_id=topic.article_topic_id,
                            customer_id=self.customer.customer_id,
                            topic_expertise=topic_expertise,
                            debug=self.debug,
                        )

                        # Query for existing lessons in the database
                        lessons = (
                            db.session.query(Lesson)
                            .filter_by(article_topic_id=topic.article_topic_id)
                            .all()
                        )

                        # If no lessons are found in the database, generate them using the text_generator
                        if not lessons:
                            generated_lessons = self.text_generator.get_lessons(topic_name)
                            for i, l in enumerate(generated_lessons):
                                try:
                                    narration_file_name = get_narration(l["lesson"], topic.article_topic_id)
                                    print(narration_file_name)
                                except Exception as e:
                                    logging.error(f"Unable to get narration: {e}")
                                lesson = get_or_create(
                                    db.session,
                                    Lesson,
                                    article_topic_id=topic.article_topic_id,
                                    lesson_content=l["lesson"],
                                    question=l["question"],
                                    right_answer=l["right_answer"],
                                    wrong_answer=l["wrong_answer"],
                                    narration_file=narration_file_name if narration_file_name else None,
                                    right_answer_explanation=l["right_answer_explanation"],
                                    order_num=i,
                                    debug=self.debug,
                                )
                                lessons.append(lesson)

                        # Convert the lessons to dictionary format
                        lessons_dict = [to_dict(lesson) for lesson in lessons]

                        # Commit the session
                        db.session.commit()
                        return lessons_dict  
                except Exception as e:
                    logging.error(f"Database commit failed in get_lessons: {e}")
                    db.session.rollback()



    class LessonProgress:
        def __init__(self, lesson_id, customer_session_id):
            self.lesson_progress = get_or_create(
                db.session,
                LessonProgress,
                lesson_id=lesson_id,
                customer_session_id=customer_session_id,
                debug=self.debug,
            )

        def update_progress(self, lesson_complete: bool, answer_correct: bool):
            self.lesson_progress.lesson_complete = lesson_complete
            self.lesson_progress.answer_correct = answer_correct
            db.session.commit()
