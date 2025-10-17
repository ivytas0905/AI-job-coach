from abc import ABC, abstractmethod
from typing import List, Optional,Dict, Any, Protocol, TypedDict
from .models import Resume

class LlmProviderPort(ABC):
    """LLM提供商接口"""
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """生成文本"""
        pass

class ResumeParserPort(ABC):
    """简历解析器接口"""
    
    @abstractmethod
    async def parse(self, file_content: bytes, filename: str) -> Resume:
        """解析简历文件，返回Resume对象"""
        pass

class ResumeOptimizerPort(ABC):
    """简历优化器接口"""
    
    @abstractmethod
    async def optimize(
        self, 
        resume: Resume, 
        target_position: str
    ) -> tuple[Resume, int, List[str]]:
        """
        优化简历
        返回: (优化后的简历, ATS分数, 建议列表)
        """
        pass