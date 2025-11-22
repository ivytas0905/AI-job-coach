from typing import Protocol, TypedDict, List, Optional, Dict, Any
from .models import Resume

# ===== LLM 相关 =====
class ChatMessage(TypedDict):
    """聊天消息格式"""
    role: str  # "system" | "user" | "assistant"
    content: str

class LlmResponse(TypedDict):
    """LLM 响应（保留扩展性）"""
    text: str
    usage: Optional[Dict[str, int]]  # token 使用情况（可选）

class LlmProviderPort(Protocol):
    """LLM 提供商接口"""
    async def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:  # MVP 直接返回文本，简化使用
        """发送聊天请求，返回生成的文本"""
        ...

# ===== 解析相关 =====
class ResumeParserPort(Protocol):
    """简历解析器接口"""
    async def parse(
        self, 
        file_content: bytes, 
        filename: str
    ) -> Resume:
        """解析简历文件，返回 Resume 对象"""
        ...

# ===== 优化相关 =====
class OptimizeResult(TypedDict):
    """优化结果"""
    optimized_resume: Resume
    ats_score: int  # 0-100
    suggestions: List[str]

class ResumeOptimizerPort(Protocol):
    """简历优化器接口（合并了 scorer + rewriter）"""
    async def optimize(
        self, 
        resume: Resume, 
        target_position: str
    ) -> OptimizeResult:
        """
        优化简历
        - 分析并重写内容
        - 计算 ATS 分数
        - 生成改进建议
        """
        ...

# ===== 预留扩展接口（注释掉，需要时再启用）=====
# class AtsScorerPort(Protocol):
#     """ATS 评分器（独立拆分时使用）"""
#     async def score(self, resume: Resume, job_description: str) -> int:
#         ...
#
# class StorageRepoPort(Protocol):
#     """持久化仓库（需要保存历史时使用）"""
#     async def save_optimization(self, data: Dict[str, Any]) -> str:
#         ...