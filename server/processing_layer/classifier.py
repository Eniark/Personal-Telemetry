from ollama import chat
from enums import EventCategories

class HardCodedClassifier:
    activity_map = {
        "Steam.exe": EventCategories.GAMING,
        "Telegram.exe": EventCategories.SOCIAL_MEDIA,
        "Code.exe": EventCategories.STUDYING,
    }

class MLClassifier:
    pass


class LLMClassifier:
    def classify(self, event = None):
        response = chat(
            model="qwen3:4b",
            messages=[
                {
                    "role": "user",
                    "content": "Categorize Chrome - Stack Overflow"
                }
            ]
        )

        print(response.message.content)


llm = LLMClassifier()
llm.classify()