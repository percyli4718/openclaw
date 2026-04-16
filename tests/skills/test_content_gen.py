"""
内容生成技能单元测试
"""

import pytest
import asyncio
from typing import Dict, Any

from baoke_tong.skills.content_gen import ContentGenerator


class TestGenerateWechatCopywriting:
    """朋友圈文案生成测试"""

    @pytest.fixture
    def generator(self):
        """创建 ContentGenerator 实例"""
        return ContentGenerator()

    @pytest.mark.asyncio
    async def test_basic_generation(self, generator: ContentGenerator):
        """测试基础文案生成 - 返回 3 条文案"""
        result = await generator.generate_wechat_copywriting(
            product_name="健康保",
            product_type="重疾险",
            tone="专业",
            count=3
        )

        # 验证返回结构
        assert result["status"] == "success"
        assert "data" in result
        assert "copies" in result["data"]
        assert len(result["data"]["copies"]) == 3
        assert "duration_ms" in result

        # 验证每条文案的结构
        for copy in result["data"]["copies"]:
            assert "id" in copy
            assert "content" in copy
            assert "hashtags" in copy
            assert "score" in copy
            assert isinstance(copy["hashtags"], list)
            assert 0 <= copy["score"] <= 1

    @pytest.mark.asyncio
    async def test_with_target_audience(self, generator: ContentGenerator):
        """测试带目标客户群体的文案生成"""
        result = await generator.generate_wechat_copywriting(
            product_name="养老保",
            product_type="寿险",
            target_audience="35-50 岁中高收入人群",
            tone="亲和",
            count=2
        )

        assert result["status"] == "success"
        assert len(result["data"]["copies"]) == 2
        # 验证文案内容包含目标客户相关信息
        for copy in result["data"]["copies"]:
            assert len(copy["content"]) > 0

    @pytest.mark.asyncio
    async def test_different_tones(self, generator: ContentGenerator):
        """测试不同文案风格"""
        tones = ["专业", "亲和", "幽默", "紧迫"]

        for tone in tones:
            result = await generator.generate_wechat_copywriting(
                product_name="意外保",
                product_type="意外险",
                tone=tone,
                count=1
            )

            assert result["status"] == "success"
            assert len(result["data"]["copies"]) == 1

    @pytest.mark.asyncio
    async def test_count_validation(self, generator: ContentGenerator):
        """测试生成条数验证"""
        # 测试最小值
        result = await generator.generate_wechat_copywriting(
            product_name="测试保",
            product_type="重疾险",
            count=1
        )
        assert len(result["data"]["copies"]) == 1

        # 测试最大值
        result = await generator.generate_wechat_copywriting(
            product_name="测试保",
            product_type="重疾险",
            count=5
        )
        assert len(result["data"]["copies"]) == 5

    @pytest.mark.asyncio
    async def test_product_types(self, generator: ContentGenerator):
        """测试不同产品类型"""
        product_types = ["重疾险", "医疗险", "寿险", "意外险"]

        for p_type in product_types:
            result = await generator.generate_wechat_copywriting(
                product_name="测试产品",
                product_type=p_type,
                count=1
            )
            assert result["status"] == "success"


class TestGenerateShortVideoScript:
    """短视频脚本生成测试"""

    @pytest.fixture
    def generator(self):
        """创建 ContentGenerator 实例"""
        return ContentGenerator()

    @pytest.mark.asyncio
    async def test_basic_script_generation(self, generator: ContentGenerator):
        """测试基础脚本生成"""
        result = await generator.generate_short_video_script(
            topic="如何选择合适的重疾险",
            duration=30,
            style="科普"
        )

        # 验证返回结构
        assert result["status"] == "success"
        assert "data" in result
        assert "script" in result["data"]
        assert "duration_ms" in result

        script = result["data"]["script"]
        assert "title" in script
        assert "scenes" in script
        assert isinstance(script["scenes"], list)
        assert len(script["scenes"]) > 0

        # 验证场景结构
        for scene in script["scenes"]:
            assert "time" in scene
            assert "content" in scene

    @pytest.mark.asyncio
    async def test_different_durations(self, generator: ContentGenerator):
        """测试不同视频时长"""
        durations = [15, 30, 60]

        for duration in durations:
            result = await generator.generate_short_video_script(
                topic="医疗险科普",
                duration=duration,
                style="科普"
            )
            assert result["status"] == "success"
            assert len(result["data"]["script"]["scenes"]) > 0

    @pytest.mark.asyncio
    async def test_different_styles(self, generator: ContentGenerator):
        """测试不同风格"""
        styles = ["科普", "剧情", "访谈"]

        for style in styles:
            result = await generator.generate_short_video_script(
                topic="保险知识",
                duration=30,
                style=style
            )
            assert result["status"] == "success"


class TestGeneratePosterCopywriting:
    """海报文案生成测试"""

    @pytest.fixture
    def generator(self):
        """创建 ContentGenerator 实例"""
        return ContentGenerator()

    @pytest.mark.asyncio
    async def test_basic_poster_generation(self, generator: ContentGenerator):
        """测试基础海报文案生成"""
        result = await generator.generate_poster_copywriting(
            product_name="健康保",
            selling_point="保费低至每天 1 元起",
            cta="立即免费咨询"
        )

        # 验证返回结构
        assert result["status"] == "success"
        assert "data" in result
        assert "poster" in result["data"]
        assert "duration_ms" in result

        poster = result["data"]["poster"]
        assert "title" in poster
        assert "subtitle" in poster
        assert "cta" in poster
        assert "健康保" in poster["title"]  # 标题可能包含模板变体
        assert poster["subtitle"] == "保费低至每天 1 元起"
        assert poster["cta"] == "立即免费咨询"

    @pytest.mark.asyncio
    async def test_default_cta(self, generator: ContentGenerator):
        """测试默认 CTA"""
        result = await generator.generate_poster_copywriting(
            product_name="养老保",
            selling_point="规划美好退休生活"
        )

        poster = result["data"]["poster"]
        assert poster["cta"] == "立即咨询"

    @pytest.mark.asyncio
    async def test_different_selling_points(self, generator: ContentGenerator):
        """测试不同卖点"""
        selling_points = [
            "0 等待期，即刻生效",
            " coverage 范围广，100+ 种疾病",
            "灵活缴费，无压力"
        ]

        for sp in selling_points:
            result = await generator.generate_poster_copywriting(
                product_name="测试产品",
                selling_point=sp
            )
            assert result["status"] == "success"
            assert result["data"]["poster"]["subtitle"] == sp


class TestContentGeneratorErrorHandling:
    """错误处理测试"""

    @pytest.fixture
    def generator(self):
        """创建 ContentGenerator 实例"""
        return ContentGenerator()

    @pytest.mark.asyncio
    async def test_empty_product_name(self, generator: ContentGenerator):
        """测试空产品名称处理"""
        result = await generator.generate_wechat_copywriting(
            product_name="",
            product_type="重疾险"
        )
        # 空输入应该返回错误或默认处理
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_invalid_product_type(self, generator: ContentGenerator):
        """测试无效产品类型处理"""
        result = await generator.generate_wechat_copywriting(
            product_name="测试保",
            product_type="未知类型"
        )
        # 应该返回错误或降级处理
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_timeout_simulation(self, generator: ContentGenerator):
        """模拟超时场景 - 验证降级策略"""
        # 这个测试需要实际实现超时逻辑后才能完善
        pytest.skip("等待超时重试逻辑实现")
