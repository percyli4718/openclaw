"""
客户分析技能单元测试
"""

import pytest
import asyncio
from typing import Dict, Any

from baoke_tong.skills.customer import CustomerAnalyst


class TestAnalyzeCustomerProfile:
    """客户画像分析测试"""

    @pytest.fixture
    def analyst(self):
        """创建 CustomerAnalyst 实例"""
        return CustomerAnalyst()

    @pytest.mark.asyncio
    async def test_basic_profile_analysis(self, analyst: CustomerAnalyst):
        """测试基础客户画像分析"""
        basic_info = {
            "name": "张三",
            "age": 35,
            "occupation": "软件工程师",
            "annual_income": 500000,
            "marital_status": "已婚",
            "children": 1
        }

        result = await analyst.analyze_customer_profile(
            customer_id="cust_001",
            basic_info=basic_info
        )

        # 验证返回结构
        assert result["status"] == "success"
        assert "data" in result
        assert "duration_ms" in result

        data = result["data"]
        assert data["customer_id"] == "cust_001"
        assert "tags" in data
        assert "risk_profile" in data
        assert "insurance_awareness" in data

        # 验证标签列表
        assert isinstance(data["tags"], list)
        assert len(data["tags"]) > 0

        # 验证风险偏好枚举值
        valid_risk_profiles = ["保守型", "稳健型", "平衡型", "进取型"]
        assert data["risk_profile"] in valid_risk_profiles

        # 验证保险意识枚举值
        valid_awareness = ["低", "中", "高"]
        assert data["insurance_awareness"] in valid_awareness

    @pytest.mark.asyncio
    async def test_high_income_customer(self, analyst: CustomerAnalyst):
        """测试高收入客户画像"""
        basic_info = {
            "name": "李四",
            "age": 45,
            "occupation": "企业高管",
            "annual_income": 2000000,
            "marital_status": "已婚",
            "children": 2
        }

        result = await analyst.analyze_customer_profile(
            customer_id="cust_002",
            basic_info=basic_info
        )

        assert result["status"] == "success"
        data = result["data"]

        # 高收入客户应该有相应标签
        assert "高收入" in data["tags"] or "高净值" in data["tags"]

    @pytest.mark.asyncio
    async def test_young_customer(self, analyst: CustomerAnalyst):
        """测试年轻客户画像"""
        basic_info = {
            "name": "王五",
            "age": 25,
            "occupation": "初级工程师",
            "annual_income": 150000,
            "marital_status": "单身",
            "children": 0
        }

        result = await analyst.analyze_customer_profile(
            customer_id="cust_003",
            basic_info=basic_info
        )

        assert result["status"] == "success"
        data = result["data"]

        # 年轻客户应该有相应标签
        assert "青年" in data["tags"] or "年轻" in data["tags"]

    @pytest.mark.asyncio
    async def test_family_pillar_customer(self, analyst: CustomerAnalyst):
        """测试家庭支柱型客户"""
        basic_info = {
            "name": "赵六",
            "age": 40,
            "occupation": "部门经理",
            "annual_income": 800000,
            "marital_status": "已婚",
            "children": 2
        }

        result = await analyst.analyze_customer_profile(
            customer_id="cust_004",
            basic_info=basic_info
        )

        assert result["status"] == "success"
        data = result["data"]

        # 家庭支柱应该有相应标签
        assert "家庭支柱" in data["tags"] or "中年" in data["tags"]

    @pytest.mark.asyncio
    async def test_minimal_info(self, analyst: CustomerAnalyst):
        """测试仅提供最少信息"""
        basic_info = {
            "name": "测试用户",
            "age": 30
        }

        result = await analyst.analyze_customer_profile(
            customer_id="cust_005",
            basic_info=basic_info
        )

        assert result["status"] == "success"
        data = result["data"]
        assert data["customer_id"] == "cust_005"
        assert len(data["tags"]) > 0


class TestSegmentCustomers:
    """客户分层测试"""

    @pytest.fixture
    def analyst(self):
        """创建 CustomerAnalyst 实例"""
        return CustomerAnalyst()

    @pytest.mark.asyncio
    async def test_basic_segmentation(self, analyst: CustomerAnalyst):
        """测试基础客户分层"""
        customer_ids = ["cust_001", "cust_002", "cust_003", "cust_004"]

        result = await analyst.segment_customers(
            customer_ids=customer_ids
        )

        # 验证返回结构
        assert result["status"] == "success"
        assert "data" in result
        assert "duration_ms" in result

        data = result["data"]
        assert "segments" in data

        segments = data["segments"]
        # 验证分层结构
        valid_segment_names = ["高价值", "潜力", "一般", "低价值"]
        for segment_name in segments.keys():
            assert segment_name in valid_segment_names

        # 验证所有客户都被分层
        all_segmented = []
        for customers in segments.values():
            all_segmented.extend(customers)
        assert set(all_segmented) == set(customer_ids)

    @pytest.mark.asyncio
    async def test_single_customer(self, analyst: CustomerAnalyst):
        """测试单个客户分层"""
        customer_ids = ["cust_001"]

        result = await analyst.segment_customers(
            customer_ids=customer_ids
        )

        assert result["status"] == "success"
        # 单个客户也应该被正确分层

    @pytest.mark.asyncio
    async def test_empty_customer_list(self, analyst: CustomerAnalyst):
        """测试空客户列表"""
        result = await analyst.segment_customers(
            customer_ids=[]
        )

        assert result["status"] == "success"
        data = result["data"]
        assert data["segments"] == {} or all(
            len(v) == 0 for v in data["segments"].values()
        )

    @pytest.mark.asyncio
    async def test_large_customer_list(self, analyst: CustomerAnalyst):
        """测试大量客户分层"""
        customer_ids = [f"cust_{i:03d}" for i in range(50)]

        result = await analyst.segment_customers(
            customer_ids=customer_ids
        )

        assert result["status"] == "success"
        data = result["data"]

        # 验证所有客户都被分层
        all_segmented = []
        for customers in data["segments"].values():
            all_segmented.extend(customers)
        assert len(all_segmented) == 50


class TestPredictInsuranceNeeds:
    """保险需求预测测试"""

    @pytest.fixture
    def analyst(self):
        """创建 CustomerAnalyst 实例"""
        return CustomerAnalyst()

    @pytest.mark.asyncio
    async def test_basic_needs_prediction(self, analyst: CustomerAnalyst):
        """测试基础需求预测"""
        profile = {
            "customer_id": "cust_001",
            "age": 35,
            "occupation": "软件工程师",
            "annual_income": 500000,
            "marital_status": "已婚",
            "children": 1,
            "tags": ["中年", "高收入", "家庭支柱"],
            "risk_profile": "稳健型",
            "insurance_awareness": "高"
        }

        result = await analyst.predict_insurance_needs(
            customer_id="cust_001",
            profile=profile
        )

        # 验证返回结构
        assert result["status"] == "success"
        assert "data" in result
        assert "duration_ms" in result

        data = result["data"]
        assert "needs" in data
        assert isinstance(data["needs"], list)
        assert len(data["needs"]) > 0

        # 验证每个需求的结构
        for need in data["needs"]:
            assert "type" in need
            assert "priority" in need
            assert "reason" in need

            # 验证优先级枚举值
            valid_priorities = ["高", "中", "低"]
            assert need["priority"] in valid_priorities

    @pytest.mark.asyncio
    async def test_family_pillar_needs(self, analyst: CustomerAnalyst):
        """测试家庭支柱型客户需求"""
        profile = {
            "customer_id": "cust_002",
            "age": 40,
            "occupation": "部门经理",
            "annual_income": 800000,
            "marital_status": "已婚",
            "children": 2,
            "tags": ["家庭支柱", "中年", "高收入"],
            "risk_profile": "稳健型",
            "insurance_awareness": "高"
        }

        result = await analyst.predict_insurance_needs(
            customer_id="cust_002",
            profile=profile
        )

        assert result["status"] == "success"
        needs = result["data"]["needs"]

        # 家庭支柱应该优先推荐寿险/重疾险
        need_types = [n["type"] for n in needs]
        assert "寿险" in need_types or "重疾险" in need_types

    @pytest.mark.asyncio
    async def test_young_single_needs(self, analyst: CustomerAnalyst):
        """测试年轻单身客户需求"""
        profile = {
            "customer_id": "cust_003",
            "age": 25,
            "occupation": "初级工程师",
            "annual_income": 150000,
            "marital_status": "单身",
            "children": 0,
            "tags": ["青年", "单身"],
            "risk_profile": "平衡型",
            "insurance_awareness": "中"
        }

        result = await analyst.predict_insurance_needs(
            customer_id="cust_003",
            profile=profile
        )

        assert result["status"] == "success"
        needs = result["data"]["needs"]

        # 年轻单身应该优先推荐意外险/医疗险
        need_types = [n["type"] for n in needs]
        assert "意外险" in need_types or "医疗险" in need_types

    @pytest.mark.asyncio
    async def test_elderly_needs(self, analyst: CustomerAnalyst):
        """测试中老年客户需求"""
        profile = {
            "customer_id": "cust_004",
            "age": 55,
            "occupation": "企业顾问",
            "annual_income": 1000000,
            "marital_status": "已婚",
            "children": 2,
            "tags": ["中老年", "高净值", "退休规划"],
            "risk_profile": "保守型",
            "insurance_awareness": "高"
        }

        result = await analyst.predict_insurance_needs(
            customer_id="cust_004",
            profile=profile
        )

        assert result["status"] == "success"
        needs = result["data"]["needs"]

        # 中老年应该优先推荐医疗险/养老险
        need_types = [n["type"] for n in needs]
        assert "医疗险" in need_types or "养老险" in need_types

    @pytest.mark.asyncio
    async def test_minimal_profile(self, analyst: CustomerAnalyst):
        """测试最少信息 profile"""
        profile = {
            "customer_id": "cust_005",
            "age": 30
        }

        result = await analyst.predict_insurance_needs(
            customer_id="cust_005",
            profile=profile
        )

        assert result["status"] == "success"
        data = result["data"]
        assert "needs" in data


class TestCustomerAnalystErrorHandling:
    """错误处理测试"""

    @pytest.fixture
    def analyst(self):
        """创建 CustomerAnalyst 实例"""
        return CustomerAnalyst()

    @pytest.mark.asyncio
    async def test_empty_customer_id(self, analyst: CustomerAnalyst):
        """测试空客户 ID"""
        result = await analyst.analyze_customer_profile(
            customer_id="",
            basic_info={"name": "测试", "age": 30}
        )
        # 应该返回错误或默认处理
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_invalid_age(self, analyst: CustomerAnalyst):
        """测试无效年龄处理"""
        result = await analyst.analyze_customer_profile(
            customer_id="cust_001",
            basic_info={"name": "测试", "age": -1}
        )
        # 应该返回错误或默认处理
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_missing_basic_info(self, analyst: CustomerAnalyst):
        """测试缺失基本信息"""
        result = await analyst.analyze_customer_profile(
            customer_id="cust_001",
            basic_info={}
        )
        # 应该返回错误或默认处理
        assert result["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_empty_profile_for_needs_prediction(self, analyst: CustomerAnalyst):
        """测试空 profile 进行需求预测"""
        result = await analyst.predict_insurance_needs(
            customer_id="cust_001",
            profile={}
        )
        # 应该返回错误或默认处理
        assert result["status"] in ["success", "error"]


class TestCustomerAnalystIntegration:
    """集成测试"""

    @pytest.fixture
    def analyst(self):
        """创建 CustomerAnalyst 实例"""
        return CustomerAnalyst()

    @pytest.mark.asyncio
    async def test_full_workflow(self, analyst: CustomerAnalyst):
        """测试完整工作流：画像分析 -> 分层 -> 需求预测"""
        # 1. 分析客户画像
        basic_info = {
            "name": "完整测试",
            "age": 35,
            "occupation": "产品经理",
            "annual_income": 600000,
            "marital_status": "已婚",
            "children": 1
        }

        profile_result = await analyst.analyze_customer_profile(
            customer_id="cust_workflow",
            basic_info=basic_info
        )
        assert profile_result["status"] == "success"

        # 2. 客户分层
        segment_result = await analyst.segment_customers(
            customer_ids=["cust_workflow"]
        )
        assert segment_result["status"] == "success"

        # 3. 需求预测
        profile = profile_result["data"]
        needs_result = await analyst.predict_insurance_needs(
            customer_id="cust_workflow",
            profile=profile
        )
        assert needs_result["status"] == "success"

        # 验证整个工作流的数据一致性
        assert profile_result["data"]["customer_id"] == "cust_workflow"
        assert "cust_workflow" in str(segment_result["data"]["segments"])
