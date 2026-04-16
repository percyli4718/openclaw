"""
合规审核技能

基于 Hermes Agent 的保险行业合规审核：
- sensitive_word_filter: 敏感词过滤
- ai_semantic_review: AI 语义审核
- audit_log: 审计日志记录
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json
import logging
import re

logger = logging.getLogger(__name__)


class ComplianceReviewer:
    """保险行业合规审核器"""

    def __init__(
        self,
        sensitive_words_path: Optional[str] = None,
        audit_log_path: Optional[str] = None
    ):
        """
        初始化合规审核器

        Args:
            sensitive_words_path: 敏感词库文件路径
            audit_log_path: 审计日志文件路径
        """
        self.sensitive_words = self._load_sensitive_words(sensitive_words_path)
        self.audit_log_path = audit_log_path or "audit_logs.jsonl"

    def _load_sensitive_words(self, path: Optional[str]) -> List[str]:
        """
        加载敏感词库

        Args:
            path: 敏感词库文件路径

        Returns:
            敏感词列表
        """
        # 默认敏感词库（保险行业合规）
        default_words = [
            # 绝对化用语
            "最", "第一", "顶级", "极致", "永久", "绝对", "100%",
            "首选", "最佳", "最好", "最强", "最全", "最新",
            # 虚假承诺
            "保本", "稳赚", "零风险", "无风险", " guaranteed",
            "必赔", "肯定", "一定", "保证", "承诺",
            # 收益率相关
            "年化", "收益率", "回报", "收益", "分红",
            # 同业对比
            "比 XX 好", "优于", "超过", "领先",
            # 医疗建议
            "治愈", "疗效", "治疗", "康复", "神医",
            # 其他违规
            "内部消息", "特殊渠道", "关系", "后门"
        ]

        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    custom_words = [line.strip() for line in f if line.strip()]
                    return default_words + custom_words
            except FileNotFoundError:
                logger.warning(f"敏感词库文件不存在：{path}，使用默认词库")

        return default_words

    def add_sensitive_word(self, word: str) -> None:
        """
        添加敏感词到词库

        Args:
            word: 敏感词
        """
        if word not in self.sensitive_words:
            self.sensitive_words.append(word)
            logger.info(f"添加敏感词：{word}")

    def remove_sensitive_word(self, word: str) -> None:
        """
        从词库移除敏感词

        Args:
            word: 敏感词
        """
        if word in self.sensitive_words:
            self.sensitive_words.remove(word)
            logger.info(f"移除敏感词：{word}")

    def sensitive_word_filter(
        self,
        content: str,
        replacement: str = "*"
    ) -> Dict[str, Any]:
        """
        敏感词过滤

        Args:
            content: 待审核内容
            replacement: 替换字符

        Returns:
            {
                "status": "success",
                "data": {
                    "original": str,
                    "filtered": str,
                    "sensitive_words_found": [{"word": str, "position": int}],
                    "is_sensitive": bool
                },
                "duration_ms": int
            }
        """
        import time
        start_time = time.time()

        sensitive_found = []
        filtered_content = content

        for word in self.sensitive_words:
            pattern = re.compile(re.escape(word))
            matches = list(pattern.finditer(content))

            if matches:
                for match in matches:
                    sensitive_found.append({
                        "word": word,
                        "position": match.start()
                    })
                # 替换敏感词
                filtered_content = pattern.sub(
                    replacement * len(word),
                    filtered_content
                )

        duration_ms = int((time.time() - start_time) * 1000)

        return {
            "status": "success",
            "data": {
                "original": content,
                "filtered": filtered_content,
                "sensitive_words_found": sensitive_found,
                "is_sensitive": len(sensitive_found) > 0
            },
            "duration_ms": duration_ms
        }

    async def ai_semantic_review(
        self,
        content: str,
        content_type: str = "copywriting",
        product_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI 语义审核

        TODO: 集成 Hermes Agent 进行深度语义分析
        当前为占位符实现

        Args:
            content: 待审核内容
            content_type: 内容类型 (copywriting/script/poster)
            product_name: 保险产品名称

        Returns:
            {
                "status": "success",
                "data": {
                    "review_result": "approved|rejected|pending",
                    "risk_score": float,
                    "risk_categories": [str],
                    "suggestions": [str]
                },
                "duration_ms": int
            }
        """
        import time
        start_time = time.time()

        # TODO: 调用 Hermes Agent 进行 AI 语义审核
        # 当前为简单规则检查

        risk_categories = []
        suggestions = []
        risk_score = 0.0

        # 检查数字合规（收益率、金额等）
        number_pattern = r'\d+(\.\d+)?%'
        if re.search(number_pattern, content):
            risk_categories.append("数字声明")
            suggestions.append("请确保所有百分比数据有官方依据")
            risk_score += 0.3

        # 检查保险产品名称准确性
        if product_name and product_name not in content:
            risk_categories.append("产品名称缺失")
            suggestions.append("建议明确提及保险产品全称")
            risk_score += 0.1

        # 检查是否有免责声明
        if "免责" not in content and "风险" not in content:
            risk_categories.append("免责声明缺失")
            suggestions.append("建议添加免责声明或风险提示")
            risk_score += 0.2

        # 检查联系方式
        contact_patterns = [r"1[3-9]\d{9}", r"微信", r"电话", r"QQ"]
        has_contact = any(re.search(p, content) for p in contact_patterns)
        if not has_contact:
            suggestions.append("建议添加联系方式以便客户咨询")

        # 判定审核结果
        if risk_score >= 0.7:
            review_result = "rejected"
        elif risk_score >= 0.3:
            review_result = "pending"
        else:
            review_result = "approved"

        duration_ms = int((time.time() - start_time) * 1000)

        return {
            "status": "success",
            "data": {
                "review_result": review_result,
                "risk_score": min(risk_score, 1.0),
                "risk_categories": risk_categories,
                "suggestions": suggestions,
                "ai_model": "hermes-agent-placeholder",
                "requires_manual_review": review_result == "pending"
            },
            "duration_ms": duration_ms
        }

    def log_audit(
        self,
        user_id: str,
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        review_status: str = "pending",
        reviewer_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        审计日志记录

        Args:
            user_id: 用户 ID
            action: 操作类型 (generate_copywriting/review_approve/review_reject)
            input_data: 输入数据
            output_data: 输出数据
            review_status: 审核状态 (pending/approved/rejected)
            reviewer_id: 审核人 ID（人工审核时）
            ip_address: IP 地址

        Returns:
            审计日志记录
        """
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"

        audit_log = {
            "audit_log": {
                "user_id": user_id,
                "action": action,
                "input": input_data,
                "output": output_data,
                "review_status": review_status,
                "reviewer_id": reviewer_id,
                "timestamp": timestamp,
                "ip_address": ip_address or "unknown"
            }
        }

        # 写入审计日志文件（JSONL 格式）
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_log, ensure_ascii=False) + "\n")
            logger.debug(f"审计日志已记录：{audit_log['audit_log']['action']}")
        except Exception as e:
            logger.error(f"审计日志写入失败：{e}")

        return audit_log

    async def review_content(
        self,
        content: str,
        user_id: str,
        content_type: str = "copywriting",
        product_name: Optional[str] = None,
        ip_address: Optional[str] = None,
        auto_approve_threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        完整审核流程（敏感词过滤 + AI 语义审核 + 审计日志）

        Args:
            content: 待审核内容
            user_id: 用户 ID
            content_type: 内容类型
            product_name: 保险产品名称
            ip_address: IP 地址
            auto_approve_threshold: 自动通过的风险阈值

        Returns:
            {
                "status": "success",
                "data": {
                    "review_id": str,
                    "final_status": "approved|rejected|pending",
                    "sensitive_word_result": {...},
                    "ai_review_result": {...},
                    "requires_manual_review": bool
                },
                "audit_log": {...}
            }
        """
        import uuid
        import time
        start_time = time.time()

        review_id = str(uuid.uuid4())

        # Step 1: 敏感词过滤
        sensitive_result = self.sensitive_word_filter(content)

        # Step 2: AI 语义审核
        ai_result = await self.ai_semantic_review(
            content,
            content_type=content_type,
            product_name=product_name
        )

        # Step 3: 综合判定
        is_sensitive = sensitive_result["data"]["is_sensitive"]
        ai_status = ai_result["data"]["review_result"]
        ai_risk_score = ai_result["data"]["risk_score"]

        # 敏感词直接拒绝
        if is_sensitive:
            final_status = "rejected"
            requires_manual_review = False
        # AI 拒绝则拒绝
        elif ai_status == "rejected":
            final_status = "rejected"
            requires_manual_review = True
        # AI 待定则待定
        elif ai_status == "pending":
            final_status = "pending"
            requires_manual_review = True
        # AI 风险低于阈值则自动通过
        elif ai_risk_score <= auto_approve_threshold:
            final_status = "approved"
            requires_manual_review = False
        else:
            final_status = "pending"
            requires_manual_review = True

        duration_ms = int((time.time() - start_time) * 1000)

        # Step 4: 审计日志
        audit_log = self.log_audit(
            user_id=user_id,
            action="review_content",
            input_data={
                "content": content,
                "content_type": content_type,
                "product_name": product_name
            },
            output_data={
                "review_id": review_id,
                "final_status": final_status,
                "sensitive_word_result": sensitive_result["data"],
                "ai_review_result": ai_result["data"]
            },
            review_status=final_status,
            ip_address=ip_address
        )

        return {
            "status": "success",
            "data": {
                "review_id": review_id,
                "final_status": final_status,
                "sensitive_word_result": sensitive_result["data"],
                "ai_review_result": ai_result["data"],
                "requires_manual_review": requires_manual_review
            },
            "audit_log": audit_log,
            "duration_ms": duration_ms
        }

    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        review_status: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        查询审计日志

        Args:
            user_id: 用户 ID 过滤
            action: 操作类型过滤
            review_status: 审核状态过滤
            start_time: 开始时间 (ISO 格式)
            end_time: 结束时间 (ISO 格式)
            limit: 返回数量限制

        Returns:
            审计日志列表
        """
        logs = []

        try:
            with open(self.audit_log_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        audit_data = log_entry.get("audit_log", {})

                        # 过滤条件
                        if user_id and audit_data.get("user_id") != user_id:
                            continue
                        if action and audit_data.get("action") != action:
                            continue
                        if review_status and audit_data.get("review_status") != review_status:
                            continue

                        timestamp = audit_data.get("timestamp", "")
                        if start_time and timestamp < start_time:
                            continue
                        if end_time and timestamp > end_time:
                            continue

                        logs.append(log_entry)

                        if len(logs) >= limit:
                            break

                    except json.JSONDecodeError:
                        continue

        except FileNotFoundError:
            logger.warning(f"审计日志文件不存在：{self.audit_log_path}")

        # 按时间倒序
        logs.sort(
            key=lambda x: x.get("audit_log", {}).get("timestamp", ""),
            reverse=True
        )

        return logs


class ComplianceStatus:
    """审核状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ContentType:
    """内容类型枚举"""
    COPYWRITING = "copywriting"
    SCRIPT = "script"
    POSTER = "poster"
