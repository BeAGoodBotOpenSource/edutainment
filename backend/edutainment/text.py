import inspect
import json
import logging
import os
from abc import ABC, abstractmethod
from json import JSONDecodeError
from string import Template

import openai
import yaml
from dotenv import find_dotenv, load_dotenv

logger = logging.getLogger(__name__)

_ = load_dotenv(find_dotenv())


class BaseLessonText(ABC):
    """Represents a lesson for learning an article.

    Assumes that an article can be learned by breaking it into topics and then learning
    about those topics through a series of lessons, each lesson followed by a question
    to reinforce understanding.
    """

    def __init__(self, article_text: str) -> None:
        """Initialize with cleaned text from article."""
        self.article_text = article_text

    @abstractmethod
    def get_topics(self) -> list[str]:
        """Return a list of topics relevant for learning the article.

        Returns:
        --------
        list[str]
            A list of relevant topics.

        Raises:
        -------
        KeyError: Expected key missing in model-generated json.
        JSONDecodeError: Model-generated response not formatted as json.
        """
        pass

    @abstractmethod
    def get_lessons(self, topic) -> list[dict[str, str]]:
        """Return a lesson plan for learning about a topic.

        Returns:
        --------
        list[dict[str, str]]
            A list of lessons, each a dictionary. Formatted like this:

            [
                {
                    "lesson": "lesson 1 (explanatory paragraph)",
                    "question": "question 1",
                    "right_answer": "right answer explanation 1"
                    "wrong_answer": "wrong answer explanation 1"
                    "right_answer_explanation": "explain why right answer is better than wrong answer"
                },
                ...
            ]

        Raises:
        -------
        KeyError: Expected key missing in model-generated json.
        JSONDecodeError: Model-generated response not formatted as json.
        """
        pass


class GPTLessonText(BaseLessonText):
    def __init__(
        self,
        article_text: str,
        model="gpt-3.5-turbo-16k",
        temperature=0.6,
        prompt_yml="llm_prompts.yml",
    ) -> None:
        """Initialize with cleaned text from article."""

        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.article_text = article_text
        self.model = model
        self.temperature = temperature
        with open("llm_prompts.yml") as f:
            self.prompts = yaml.safe_load(f)[self.model]

    def get_topics(self):
        system_prompt = self.prompts["system_prompt"]
        topics_prompt = Template(self.prompts["topics_prompt"]).substitute(
            article=self.article_text
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": topics_prompt},
        ]
        topics_response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )

        topics_response_content = topics_response.choices[0].message.content.strip()
        try:
            topics_json = json.loads(topics_response_content)["topics"]

            topics = []
            for t in topics_json:
                if t["relevance_to_subject"] in ["medium", "high"]:
                    topics.append(t["topic"])
        except KeyError as e:
            logger.error(
                "Expected key missing in GPT-generated json:\n%s",
                str(topics_json),
            )
            raise KeyError("Expected key missing in GPT-generated json.") from e
        except json.JSONDecodeError as e:
            logger.error(
                "GPT response not formatted as json:\n%s",
                str(topics_response_content),
            )
            raise KeyError("GPT response not formatted as json.") from e
        return topics

    def get_lessons(self, topic):
        system_prompt = self.prompts["system_prompt"]
        lessons_prompt = Template(self.prompts["lessons_prompt"]).substitute(
            article=self.article_text,
            topic=topic,
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": lessons_prompt},
        ]
        lessons_response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        lessons_response_content = lessons_response.choices[0].message.content.strip()

        try:
            lessons_json = json.loads(lessons_response_content)["instruction"]
        except KeyError as e:
            logger.error(
                "Expected key missing in GPT-generated json:\n%s",
                str(lessons_json),
            )
            raise KeyError("Expected key missing in GPT-generated json.") from e
        except json.JSONDecodeError as e:
            logger.error(
                "GPT response not formatted as json:",
                lessons_response_content,
            )
            raise KeyError("GPT response not formatted as json.") from e

        return lessons_json


class ClaudeLessonText(BaseLessonText):
    def get_topics(self):
        pass
