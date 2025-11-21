
from together import Together
import os


class TogetherProvider:
    def __init__(self, api_key: str = None):
        self.client = Together(api_key=api_key or os.environ.get("TOGETHER_API_KEY"))

        # 针对不同任务的最佳模型
        self.models = {
            "resume_bullet": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "ats_analysis": "Qwen/Qwen2.5-72B-Instruct-Turbo",
            "interview": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            "quick_task": "meta-llama/Llama-3.1-8B-Instruct-Turbo"
        }

    def generate(self, prompt: str, task_type: str = "resume_bullet", **kwargs):
        response = self.client.chat.completions.create(
            model=self.models.get(task_type, self.models["resume_bullet"]),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000),
            top_p=kwargs.get("top_p", 0.9)
        )
        return response.choices[0].message.content

    def generate_with_system(self, system: str, user: str, task_type: str = "resume_bullet"):
        """带系统提示词的生成"""
        response = self.client.chat.completions.create(
            model=self.models[task_type],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
        