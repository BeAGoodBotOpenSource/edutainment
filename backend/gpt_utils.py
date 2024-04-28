import config
import logging, openai

def test(string):
    query_1 = (
        f"Question using data: {string}. comes here."
    )

    logging.info('Starting GPT API call 3 via model')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": query_1}]
    )
    cleaned_dict = response.choices[0].message['content']

    logging.info("Result:")
    print(cleaned_dict) 
    return cleaned_dict
