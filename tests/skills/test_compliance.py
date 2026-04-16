"""
合规审核技能测试
"""

import pytest
import asyncio
import os
import json
from pathlib import Path

from baoke_tong.skills.compliance import (
    ComplianceReviewer,
    ComplianceStatus,
    ContentType
)


class TestSensitiveWordFilter:
    """敏感词过滤测试"""

    def setup_method(self):
        """每个测试前的准备"""
        self.reviewer = ComplianceReviewer()

    def test_sensitive_word_found(self):
        """测试检测到敏感词"""
        content = "这是最好的保险产品，收益率 100%"
        result = self.reviewer.sensitive_word_filter(content)

        assert result["status"] == "success"
        assert result["data"]["is_sensitive"] is True
        assert len(result["data"]["sensitive_words_found"]) > 0

        # 检查是否包含"最"和"100%"
        words = [item["word"] for item in result["data"]["sensitive_words_found"]]
        assert "最" in words or "100%" in words

    def test_no_sensitive_word(self):
        """测试没有敏感词"""
        content = "这是一款专业的保险产品，为您提供全面保障"
        result = self.reviewer.sensitive_word_filter(content)

        assert result["status"] == "success"
        assert result["data"]["is_sensitive"] is False
        assert len(result["data"]["sensitive_words_found"]) == 0

    def test_filter_replacement(self):
        """测试敏感词替换"""
        content = "这是最好的产品"
        result = self.reviewer.sensitive_word_filter(content, replacement="*")

        assert "最" not in result["data"]["filtered"]
        assert "*" in result["data"]["filtered"]

    def test_custom_sensitive_word(self):
        """测试添加自定义敏感词"""
        self.reviewer.add_sensitive_word("测试敏感词")
        content = "这是一个测试敏感词例子"
        result = self.reviewer.sensitive_word_filter(content)

        assert result["data"]["is_sensitive"] is True
        assert any(item["word"] == "测试敏感词" for item in result["data"]["sensitive_words_found"])

    def test_remove_sensitive_word(self):
        """测试移除敏感词"""
        # 先添加
        self.reviewer.add_sensitive_word("临时敏感词")
        # 再移除
        self.reviewer.remove_sensitive_word("临时敏感词")

        content = "这是一个临时敏感词例子"
        result = self.reviewer.sensitive_word_filter(content)

        # 移除后不应该再检测到
        assert result["data"]["is_sensitive"] is False


class TestAISemanticReview:
    """AI 语义审核测试"""

    def setup_method(self):
        self.reviewer = ComplianceReviewer()

    @pytest.mark.asyncio
    async def test_high_risk_content(self):
        """测试高风险内容"""
        content = "购买本产品，年化收益率 15%，稳赚不赔，保本保息"
        result = await self.reviewer.ai_semantic_review(content)

        assert result["status"] == "success"
        assert result["data"]["review_result"] in ["rejected", "pending"]
        assert result["data"]["risk_score"] > 0.3

    @pytest.mark.asyncio
    async def test_low_risk_content(self):
        """测试低风险内容"""
        content = "保险是一种风险管理工具，可以为您提供保障"
        result = await self.reviewer.ai_semantic_review(content)

        assert result["status"] == "success"
        assert result["data"]["review_result"] == "approved"
        assert result["data"]["risk_score"] <= 0.3

    @pytest.mark.asyncio
    async def test_missing_disclaimer(self):
        """测试缺失免责声明"""
        content = "立即购买，限时优惠"
        result = await self.reviewer.ai_semantic_review(content)

        assert "免责声明缺失" in result["data"]["risk_categories"]


class TestAuditLog:
    """审计日志测试"""

    def setup_method(self):
        self.test_log_path = "/tmp/test_audit_logs.jsonl"
        # 清理之前的测试日志
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)
        self.reviewer = ComplianceReviewer(audit_log_path=self.test_log_path)

    def teardown_method(self):
        """每个测试后的清理"""
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)

    def test_log_audit(self):
        """测试记录审计日志"""
        log = self.reviewer.log_audit(
            user_id="user_001",
            action="generate_copywriting",
            input_data={"content": "测试内容"},
            output_data={"result": "approved"},
            review_status="approved",
            ip_address="192.168.1.1"
        )

        assert "audit_log" in log
        assert log["audit_log"]["user_id"] == "user_001"
        assert log["audit_log"]["action"] == "generate_copywriting"
        assert log["audit_log"]["review_status"] == "approved"

        # 验证日志已写入文件
        with open(self.test_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 1

    def test_get_audit_logs(self):
        """测试查询审计日志"""
        # 先写入多条日志
        self.reviewer.log_audit(
            user_id="user_001",
            action="generate_copywriting",
            input_data={},
            output_data={},
            review_status="approved"
        )
        self.reviewer.log_audit(
            user_id="user_002",
            action="review_approve",
            input_data={},
            output_data={},
            review_status="rejected"
        )

        # 查询所有日志
        logs = self.reviewer.get_audit_logs()
        assert len(logs) == 2

        # 按用户 ID 过滤
        logs = self.reviewer.get_audit_logs(user_id="user_001")
        assert len(logs) == 1
        assert logs[0]["audit_log"]["user_id"] == "user_001"

        # 按审核状态过滤
        logs = self.reviewer.get_audit_logs(review_status="approved")
        assert len(logs) == 1


class TestReviewContent:
    """完整审核流程测试"""

    def setup_method(self):
        self.test_log_path = "/tmp/test_review_audit_logs.jsonl"
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)
        self.reviewer = ComplianceReviewer(audit_log_path=self.test_log_path)

    def teardown_method(self):
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)

    @pytest.mark.asyncio
    async def test_content_with_sensitive_words(self):
        """测试包含敏感词的内容"""
        content = "这是最好的保险产品，第一品牌"
        result = await self.reviewer.review_content(
            content=content,
            user_id="user_001",
            ip_address="192.168.1.1"
        )

        assert result["status"] == "success"
        assert result["data"]["final_status"] == "rejected"
        assert result["data"]["requires_manual_review"] is False

    @pytest.mark.asyncio
    async def test_normal_content(self):
        """测试正常内容"""
        content = "保险是一种风险管理工具"
        result = await self.reviewer.review_content(
            content=content,
            user_id="user_001",
            ip_address="192.168.1.1"
        )

        assert result["status"] == "success"
        assert result["data"]["final_status"] == "approved"

    @pytest.mark.asyncio
    async def test_audit_log_created(self):
        """测试审计日志已创建"""
        content = "测试内容"
        result = await self.reviewer.review_content(
            content=content,
            user_id="user_001"
        )

        # 验证返回中包含审计日志
        assert "audit_log" in result

        # 验证日志文件中有记录
        logs = self.reviewer.get_audit_logs()
        assert len(logs) >= 1


class TestContentGeneratorIntegration:
    """内容生成器集成测试"""

    def setup_method(self):
        self.test_log_path = "/tmp/test_content_gen_logs.jsonl"
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)

        self.reviewer = ComplianceReviewer(audit_log_path=self.test_log_path)

        from baoke_tong.skills.content_gen import ContentGenerator
        self.generator = ContentGenerator(
            compliance_reviewer=self.reviewer,
            auto_review=True
        )

    def teardown_method(self):
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)

    @pytest.mark.asyncio
    async def test_generate_with_auto_review(self):
        """测试生成内容并自动审核"""
        result = await self.generator.generate_wechat_copywriting(
            product_name="健康保",
            product_type="重疾险",
            user_id="user_001",
            ip_address="192.168.1.1"
        )

        assert result["status"] == "success"
        assert "copies" in result["data"]
        assert "review_results" in result["data"]

        # 检查审核结果
        review_results = result["data"]["review_results"]
        assert len(review_results) > 0

    @pytest.mark.asyncio
    async def test_generate_without_review(self):
        """测试生成内容但不审核"""
        self.generator.auto_review = False

        result = await self.generator.generate_wechat_copywriting(
            product_name="健康保",
            product_type="重疾险",
            user_id="user_001"
        )

        assert result["status"] == "success"
        assert "review_results" not in result["data"]


class TestComplianceStatusEnum:
    """枚举类测试"""

    def test_compliance_status_values(self):
        """测试审核状态枚举值"""
        assert ComplianceStatus.PENDING == "pending"
        assert ComplianceStatus.APPROVED == "approved"
        assert ComplianceStatus.REJECTED == "rejected"

    def test_content_type_values(self):
        """测试内容类型枚举值"""
        assert ContentType.COPYWRITING == "copywriting"
        assert ContentType.SCRIPT == "script"
        assert ContentType.POSTER == "poster"
