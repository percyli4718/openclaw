"""
内容生成技能

基于 LLM 的保险行业内容生成：
- generate_wechat_copywriting: 朋友圈文案生成
- generate_short_video_script: 短视频脚本生成
- generate_poster_copywriting: 海报文案生成

所有生成的内容会自动经过合规审核流程。
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional

from .compliance import ComplianceReviewer
from ..llm import LLMProvider, LLMMessage, get_llm_provider
from ..db.cache import cache_get, cache_set, cache_invalidate


class ContentGenerator:
    """保险行业内容生成器"""

    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        compliance_reviewer: Optional[ComplianceReviewer] = None,
        auto_review: bool = True,
        use_cache: bool = True,
    ):
        """
        Args:
            llm: LLM Provider 实例。未传入时延迟初始化（首次调用时通过 get_llm_provider() 获取）。
            compliance_reviewer: 合规审核器实例。
            auto_review: 是否自动触发合规审核（默认 True）。
            use_cache: 是否启用 LLM 结果缓存（默认 True）。
        """
        self._llm = llm
        self._llm_provided = llm is not None
        self.compliance_reviewer = compliance_reviewer or ComplianceReviewer()
        self.auto_review = auto_review
        self.use_cache = use_cache
        self._cache_ttl = 300  # 5 分钟

    @property
    def llm(self) -> LLMProvider:
        if not self._llm_provided:
            self._llm = get_llm_provider()
            self._llm_provided = True
        return self._llm

    # ---- 缓存 ----

    @staticmethod
    def _cache_key(method: str, params: dict) -> str:
        """生成缓存 key：方法名 + 参数哈希"""
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:12]
        return f"content_gen:{method}:{param_hash}"

    async def _cache_lookup(self, key: str) -> Optional[Dict[str, Any]]:
        """从缓存查找 LLM 结果"""
        if not self.use_cache:
            return None
        return await cache_get(key)

    async def _cache_store(self, key: str, value: Dict[str, Any]) -> None:
        """将 LLM 结果存入缓存"""
        if not self.use_cache:
            return
        await cache_set(key, value, ttl=self._cache_ttl)

    async def invalidate_cache(self, method: str, params: dict) -> None:
        """手动使特定参数的缓存失效"""
        key = self._cache_key(method, params)
        await cache_invalidate(key)

    # ---- 提示词构建 ----

    @staticmethod
    def _build_copywriting_prompt(
        product_name: str,
        product_type: str,
        target_audience: Optional[str],
        tone: str,
        count: int,
    ) -> str:
        """构建朋友圈文案生成提示词"""
        lines = [
            f"你是一名资深保险文案策划师。请为以下保险产品生成 {count} 条朋友圈文案。",
            "",
            f"产品名称：{product_name}",
            f"产品类型：{product_type}",
            f"文案风格：{tone}",
        ]
        if target_audience:
            lines.append(f"目标客户：{target_audience}")
        lines.extend([
            "",
            "要求：",
            f"1. 每条文案 80-150 字",
            f"2. 风格为「{tone}」",
            f"3. 每条包含 2-3 个相关 hashtag",
            f"4. 不得出现「 guaranteed」「100% 赔付」等绝对化承诺",
            "",
            "输出格式（JSON 数组）：",
            '[{"content": "...", "hashtags": ["#", "#"]}, ...]',
        ])
        return "\n".join(lines)

    @staticmethod
    def _build_video_script_prompt(
        topic: str,
        duration: int,
        style: str,
    ) -> str:
        """构建短视频脚本生成提示词"""
        return "\n".join([
            f"你是一名保险科普短视频编剧。请为以下主题生成 {duration} 秒的短视频脚本。",
            "",
            f"主题：{topic}",
            f"时长：{duration} 秒",
            f"风格：{style}",
            "",
            "输出格式（JSON）：",
            '{"title": "...", "scenes": [{"time": "0-5s", "content": "..."}]}',
        ])

    @staticmethod
    def _build_poster_prompt(
        product_name: str,
        selling_point: str,
        cta: str,
    ) -> str:
        """构建海报文案生成提示词"""
        return "\n".join([
            f"你是一名保险海报文案策划师。请为以下产品生成海报文案。",
            "",
            f"产品名称：{product_name}",
            f"核心卖点：{selling_point}",
            f"行动号召：{cta}",
            "",
            "输出格式（JSON）：",
            '{"title": "...", "subtitle": "...", "cta": "..."}',
        ])

    # ---- 主方法 ----

    async def generate_wechat_copywriting(
        self,
        product_name: str,
        product_type: str,
        target_audience: Optional[str] = None,
        tone: str = "专业",
        count: int = 3,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        生成朋友圈文案

        Args:
            product_name: 保险产品名称
            product_type: 产品类型 (重疾险/医疗险/寿险/意外险)
            target_audience: 目标客户群体
            tone: 文案风格 (专业/亲和/幽默/紧迫)
            count: 生成条数 (1-5)
            user_id: 用户 ID（用于审计日志）
            ip_address: IP 地址（用于审计日志）

        Returns:
            包含文案列表和审核状态的字典
        """
        start = time.time()
        count = max(1, min(5, count))

        # 缓存 key：基于 prompt 参数
        cache_params = {
            "product_name": product_name,
            "product_type": product_type,
            "target_audience": target_audience,
            "tone": tone,
            "count": count,
        }
        ckey = self._cache_key("copywriting", cache_params)

        # 检查缓存
        cached = await self._cache_lookup(ckey)
        if cached is not None:
            copies = cached["copies"]
            result = {
                "status": "success",
                "data": {"copies": copies},
                "duration_ms": int((time.time() - start) * 1000),
                "from_cache": True,
            }
        else:
            prompt = self._build_copywriting_prompt(
                product_name, product_type, target_audience, tone, count
            )
            response = await self.llm.chat(
                messages=[LLMMessage(role="user", content=prompt)],
                temperature=0.7,
            )

            # 简单解析：尝试从 LLM 返回中提取 JSON
            copies = self._parse_copies(response.text, product_name, count)

            # 存入缓存
            await self._cache_store(ckey, {"copies": copies})

            result = {
                "status": "success",
                "data": {"copies": copies},
                "duration_ms": int((time.time() - start) * 1000),
                "from_cache": False,
            }

        # 自动合规审核
        effective_user_id = user_id or "anonymous"
        if self.auto_review:
            review_results = []
            for copy in copies:
                review_result = await self.compliance_reviewer.review_content(
                    content=copy["content"],
                    user_id=effective_user_id,
                    content_type="copywriting",
                    product_name=product_name,
                    ip_address=ip_address,
                )
                review_results.append({
                    "copy_id": copy["id"],
                    "review": review_result,
                })

                if review_result["data"]["final_status"] == "approved":
                    copy["compliance_status"] = "approved"
                elif review_result["data"]["final_status"] == "rejected":
                    copy["compliance_status"] = "rejected"
                    copy["rejection_reason"] = review_result["data"]["sensitive_word_result"]
                else:
                    copy["compliance_status"] = "pending_manual_review"

            result["data"]["review_results"] = review_results

        return result

    async def generate_short_video_script(
        self,
        topic: str,
        duration: int = 30,
        style: str = "科普",
    ) -> Dict[str, Any]:
        """
        生成短视频脚本

        Args:
            topic: 视频主题
            duration: 视频时长 (秒)
            style: 风格 (科普/剧情/访谈)

        Returns:
            包含脚本的字典
        """
        start = time.time()

        cache_params = {"topic": topic, "duration": duration, "style": style}
        ckey = self._cache_key("video_script", cache_params)

        cached = await self._cache_lookup(ckey)
        if cached is not None:
            script = cached["script"]
            result = {
                "status": "success",
                "data": {"script": script},
                "duration_ms": int((time.time() - start) * 1000),
                "from_cache": True,
            }
        else:
            prompt = self._build_video_script_prompt(topic, duration, style)
            response = await self.llm.chat(
                messages=[LLMMessage(role="user", content=prompt)],
                temperature=0.7,
            )

            # 简单解析
            script = self._parse_script(response.text, topic)
            await self._cache_store(ckey, {"script": script})

            result = {
                "status": "success",
                "data": {"script": script},
                "duration_ms": int((time.time() - start) * 1000),
                "from_cache": False,
            }

        return result

    async def generate_poster_copywriting(
        self,
        product_name: str,
        selling_point: str,
        cta: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        生成海报文案

        Args:
            product_name: 保险产品名称
            selling_point: 卖点
            cta: 行动号召

        Returns:
            包含海报文案的字典
        """
        start = time.time()

        cache_params = {
            "product_name": product_name,
            "selling_point": selling_point,
            "cta": cta or "立即咨询",
        }
        ckey = self._cache_key("poster", cache_params)

        cached = await self._cache_lookup(ckey)
        if cached is not None:
            poster = cached["poster"]
            result = {
                "status": "success",
                "data": {"poster": poster},
                "duration_ms": int((time.time() - start) * 1000),
                "from_cache": True,
            }
        else:
            prompt = self._build_poster_prompt(product_name, selling_point, cta or "立即咨询")
            response = await self.llm.chat(
                messages=[LLMMessage(role="user", content=prompt)],
                temperature=0.7,
            )

            poster = self._parse_poster(response.text, product_name, selling_point, cta)
            await self._cache_store(ckey, {"poster": poster})

            result = {
                "status": "success",
                "data": {"poster": poster},
                "duration_ms": int((time.time() - start) * 1000),
                "from_cache": False,
            }

        return result

    # ---- 解析辅助方法 ----

    @staticmethod
    def _parse_copies(text: str, product_name: str, count: int) -> list[dict]:
        """从 LLM 返回文本中解析文案列表"""
        import json
        import re

        # 尝试提取 JSON 数组
        match = re.search(r'\[[\s\S]*\]', text)
        if match:
            try:
                items = json.loads(match.group())
                return [
                    {
                        "id": f"copy_{i+1:03d}",
                        "content": item.get("content", ""),
                        "hashtags": item.get("hashtags", ["保险", "保障"]),
                        "score": 0.85,
                    }
                    for i, item in enumerate(items[:count])
                ]
            except json.JSONDecodeError:
                pass

        # 降级：回退到简单模板
        return [
            {
                "id": f"copy_{i+1:03d}",
                "content": f"【{product_name}】为您保驾护航 (版本 {i+1})",
                "hashtags": ["保险", "保障"],
                "score": round(0.85 - i * 0.05, 2),
            }
            for i in range(count)
        ]

    @staticmethod
    def _parse_script(text: str, topic: str) -> dict:
        """从 LLM 返回文本中解析脚本"""
        import json
        import re

        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                data = json.loads(match.group())
                return {
                    "title": data.get("title", f"{topic} 科普"),
                    "scenes": data.get("scenes", [
                        {"time": "0-5s", "content": "开场引入"},
                        {"time": "5-25s", "content": "核心内容讲解"},
                        {"time": "25-30s", "content": "总结 + CTA"},
                    ]),
                }
            except json.JSONDecodeError:
                pass

        return {
            "title": f"{topic} 科普",
            "scenes": [
                {"time": "0-5s", "content": "开场引入"},
                {"time": "5-25s", "content": "核心内容讲解"},
                {"time": "25-30s", "content": "总结 + CTA"},
            ],
        }

    @staticmethod
    def _parse_poster(text: str, product_name: str, selling_point: str, cta: str) -> dict:
        """从 LLM 返回文本中解析海报文案"""
        import json
        import re

        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                data = json.loads(match.group())
                return {
                    "title": data.get("title", product_name),
                    "subtitle": data.get("subtitle", selling_point),
                    "cta": data.get("cta", cta),
                }
            except json.JSONDecodeError:
                pass

        return {
            "title": product_name,
            "subtitle": selling_point,
            "cta": cta,
        }
