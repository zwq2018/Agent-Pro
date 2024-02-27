import os
import openai
import dashscope
import replicate
from http import HTTPStatus


class GPT35API:

    def __init__(self) -> None:
        openai.api_key = "YOUR KEY"

    def response(self, mes):
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=mes,
            top_p=0.95,
            temperature=1,
        )
        return response.get("choices")[0]["message"]["content"]


class GPT4API:

    def __init__(self) -> None:
        openai.api_key = "YOUR KEY"

    def response(self, mes):
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=mes,
            top_p=0.95,
            temperature=1,
        )
        return response.get("choices")[0]["message"]["content"]


class llama2_70b_chatAPI:

    def response(self, mes):
        os.environ["REPLICATE_API_TOKEN"] = "YOUR KEY"
        system_prompt = ""
        prompt = ""
        for item in mes:
            if item.get('role') == 'system':
                system_prompt = item.get('content')
            if item.get('role') == 'user':
                prompt = item.get('content')
        try:
            iterator = replicate.run(
                "meta/llama-2-70b-chat",
                input={
                    "system_prompt": system_prompt,
                    "prompt": prompt,
                    "temperature": 1,
                    "top_p": 0.95,
                    "max_new_tokens": 4000,
                },
            )
            result_string = ''.join(text for text in iterator)
        except replicate.exceptions.ModelError as e:
            with open("/replicate_modelerror_times.txt", "a") as f:
                f.write("llama2_70b_chat:replicate_modelerror_times\n")
            print(e)
        except Exception as e:
            with open("Exception.txt", "a") as f:
                f.write("llama2_70b_chat:Exception_times\n")
            print(e)
        return result_string


class QwenAPI:

    def __init__(self) -> None:
        dashscope.api_key = 'YOUR KEY'

    def response(self, mes):
        response = dashscope.Generation.call(
            'qwen-72b-chat',
            messages=mes,
            temperature=1,
            top_p=0.95,
            result_format='message',
        )
        if response.status_code == HTTPStatus.OK:
            data_res = response['output']['choices'][0]['message']['content']
            return data_res
        else:
            print(
                'Request id: %s, Status code: %s, error code: %s, error message: %s'
                % (response.request_id, response.status_code, response.code,
                   response.message))
