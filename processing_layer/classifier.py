from ollama import chat




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