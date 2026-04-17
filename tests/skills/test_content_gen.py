"""
内容生成技能测试
"""

import pytest
from baoke_tong.skills.content_gen import ContentGenerator
from baoke_tong.skills.compliance import ComplianceReviewer
from tests.mock_llm import MockLLMProvider


class TestContentGenerator:
    """内容生成器测试"""

    def setup_method(self):
        """每个测试前的准备"""
        self.mock_llm = MockLLMProvider()
        self.generator = ContentGenerator(llm=self.mock_llm)

    @pytest.mark.asyncio
    async def test_generate_wechat_copywriting(self):
        """测试生成朋友圈文案"""
        self.mock_llm.set_responses([
            '[{"content": "文案1", "hashtags": ["保险"]}, {"content": "文案2", "hashtags": ["保障"]}, {"content": "文案3", "hashtags": ["健康"]}]',
        ])
        result = await self.generator.generate_wechat_copywriting(
            product_name="健康保",
            product_type="重疾险",
            target_audience="25-40 岁白领",
            tone="专业",
            count=3,
        )

        assert result["status"] == "success"
        assert "data" in result
        assert "copies" in result["data"]
        assert len(result["data"]["copies"]) == 3

    @pytest.mark.asyncio
    async def test_generate_short_video_script(self):
        """测试生成短视频脚本"""
        self.mock_llm.set_responses([
            '{"title": "重疾险科普", "scenes": [{"time": "0-5s", "content": "开场"}]}',
        ])
        result = await self.generator.generate_short_video_script(
            topic="重疾险如何选择",
            duration=60,
            style="科普",
        )

        assert result["status"] == "success"
        assert "data" in result
        assert "script" in result["data"]

    @pytest.mark.asyncio
    async def test_generate_poster_copywriting(self):
        """测试生成海报文案"""
        self.mock_llm.set_responses([
            '{"title": "健康保", "subtitle": "保额高", "cta": "立即咨询"}',
        ])
        result = await self.generator.generate_poster_copywriting(
            product_name="健康保",
            selling_point="保额高，保费低",
            cta="立即咨询",
        )

        assert result["status"] == "success"
        assert "data" in result
        assert "poster" in result["data"]


class TestContentGeneratorWithCompliance:
    """内容生成器（带合规审核）测试"""

    def setup_method(self):
        self.mock_llm = MockLLMProvider()
        self.reviewer = ComplianceReviewer()
        self.generator = ContentGenerator(
            llm=self.mock_llm,
            compliance_reviewer=self.reviewer,
            auto_review=True,
        )

    @pytest.mark.asyncio
    async def test_generate_with_auto_review(self):
        """测试生成内容并自动审核"""
        self.mock_llm.set_responses([
            '[{"content": "文案1", "hashtags": ["保险"]}]',
        ])
        result = await self.generator.generate_wechat_copywriting(
            product_name="健康保",
            product_type="重疾险",
            user_id="user_001",
            ip_address="192.168.1.1",
        )

        assert result["status"] == "success"
        assert "copies" in result["data"]
        assert "review_results" in result["data"]

    @pytest.mark.asyncio
    async def test_generate_without_review(self):
        """测试生成内容但不审核"""
        self.mock_llm.set_responses([
            '[{"content": "文案1", "hashtags": ["保险"]}]',
        ])
        self.generator.auto_review = False

        result = await self.generator.generate_wechat_copywriting(
            product_name="健康保",
            product_type="重疾险",
            user_id="user_001",
        )

        assert result["status"] == "success"
        assert "review_results" not in result["data"]


class TestContentGeneratorEdgeCases:
    """内容生成器边界测试"""

    def setup_method(self):
        self.mock_llm = MockLLMProvider()
        self.generator = ContentGenerator(llm=self.mock_llm)

    @pytest.mark.asyncio
    async def test_generate_single_copy(self):
        """测试生成单条文案"""
        self.mock_llm.set_responses([
            '[{"content": "文案1", "hashtags": ["保险"]}]',
        ])
        result = await self.generator.generate_wechat_copywriting(
            product_name="健康保",
            product_type="重疾险",
            count=1,
        )

        assert result["status"] == "success"
        assert len(result["data"]["copies"]) == 1

    @pytest.mark.asyncio
    async def test_generate_max_copies(self):
        """测试生成最大数量文案"""
        self.mock_llm.set_responses([
            '[{"content": "文案1", "hashtags": ["#1"]}, {"content": "文案2", "hashtags": ["#2"]}, {"content": "文案3", "hashtags": ["#3"]}, {"content": "文案4", "hashtags": ["#4"]}, {"content": "文案5", "hashtags": ["#5"]}]',
        ])
        result = await self.generator.generate_wechat_copywriting(
            product_name="健康保",
            product_type="重疾险",
            count=5,
        )

        assert result["status"] == "success"
        assert len(result["data"]["copies"]) == 5

    @pytest.mark.asyncio
    async def test_different_tones(self):
        """测试不同文案风格"""
        tones = ["专业", "亲和", "幽默", "紧迫"]
        for tone in tones:
            self.mock_llm.set_responses([
                '[{"content": f"文案-{tone}", "hashtags": ["保险"]}]',
            ])
            result = await self.generator.generate_wechat_copywriting(
                product_name="健康保",
                product_type="重疾险",
                tone=tone,
                count=1,
            )
            assert result["status"] == "success"
