import openai
import os


class API:

    def __init__(self, model, key, temp=1, top_p=1) -> None:
        self.api_key = key
        self.model = model
        self.temp = temp
        self.top_p = top_p

    def response(self, mes, n):
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=mes,
            stream=False,
            n=n,
            top_p=self.top_p,
            temperature=self.temp,
        )
        choices = response.get("choices")
        contents = []
        for choice in choices:
            contents.append(choice["message"]["content"])
        return contents
