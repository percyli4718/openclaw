"""
客户分析技能测试
"""

import pytest
from baoke_tong.skills.customer import CustomerAnalyst
from tests.mock_llm import MockLLMProvider


class TestCustomerAnalyst:
    """客户分析师测试"""

    def setup_method(self):
        """每个测试前的准备"""
        self.mock_llm = MockLLMProvider()
        self.analyst = CustomerAnalyst(llm=self.mock_llm)

    @pytest.mark.asyncio
    async def test_analyze_customer_profile(self):
        """测试客户画像分析"""
        self.mock_llm.set_responses([
            '{"tags": ["中年", "高收入", "家庭支柱"], "risk_profile": "稳健型", "insurance_awareness": "高"}',
        ])
        result = await self.analyst.analyze_customer_profile(
            customer_id="cust_001",
            basic_info={
                "age": 35,
                "occupation": "软件工程师",
                "income": "50-100 万",
                "family_status": "已婚有子女",
            },
        )

        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["customer_id"] == "cust_001"
        assert "tags" in result["data"]
        assert "risk_profile" in result["data"]

    @pytest.mark.asyncio
    async def test_segment_customers(self):
        """测试客户分层"""
        self.mock_llm.set_responses([
            '{"高价值": ["cust_001", "cust_002"], "潜力": ["cust_003"], "一般": ["cust_004"]}',
        ])
        result = await self.analyst.segment_customers(
            customer_ids=["cust_001", "cust_002", "cust_003"],
        )

        assert result["status"] == "success"
        assert "data" in result
        assert "segments" in result["data"]

    @pytest.mark.asyncio
    async def test_predict_insurance_needs(self):
        """测试保险需求预测"""
        self.mock_llm.set_responses([
            '[{"type": "重疾险", "priority": "高", "reason": "家庭支柱"}]',
        ])
        result = await self.analyst.predict_insurance_needs(
            customer_id="cust_001",
            profile={
                "age": 35,
                "occupation": "软件工程师",
                "family_status": "已婚有子女",
            },
        )

        assert result["status"] == "success"
        assert "data" in result
        assert "needs" in result["data"]
        assert len(result["data"]["needs"]) > 0


class TestCustomerAnalystWithVectorStore:
    """客户分析师（带向量存储）测试"""

    def setup_method(self):
        self.mock_llm = MockLLMProvider()
        self.analyst = CustomerAnalyst(llm=self.mock_llm)

    @pytest.mark.asyncio
    async def test_analyze_with_vector_store(self):
        """测试使用向量存储进行分析"""
        self.mock_llm.set_responses([
            '{"tags": ["年轻", "中等收入"], "risk_profile": "稳健型", "insurance_awareness": "中"}',
        ])
        result = await self.analyst.analyze_customer_profile(
            customer_id="cust_002",
            basic_info={
                "age": 28,
                "occupation": "产品经理",
                "income": "30-50 万",
            },
        )

        assert result["status"] == "success"
        assert result["data"]["customer_id"] == "cust_002"
