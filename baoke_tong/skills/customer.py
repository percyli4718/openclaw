"""
客户分析技能

基于 Hermes Agent 的保险客户画像分析：
- analyze_customer_profile: 客户画像分析
- segment_customers: 客户分层
- predict_insurance_needs: 需求预测
- search_similar_customers: 相似客户检索
"""

from typing import List, Dict, Any, Optional
import time
import uuid
import logging

logger = logging.getLogger(__name__)


class CustomerAnalyst:
    """保险客户分析师"""

    # 年龄段标签
    AGE_RANGES = {
        (0, 17): "未成年",
        (18, 24): "青年",
        (25, 34): "青年",
        (35, 44): "中年",
        (45, 59): "中年",
        (60, 150): "老年"
    }

    # 收入层级标签
    INCOME_LEVELS = {
        (0, 100000): "低收入",
        (100000, 300000): "中等收入",
        (300000, 1000000): "高收入",
        (1000000, float('inf')): "高净值"
    }

    # 风险偏好评估规则
    RISK_PROFILE_RULES = {
        "保守型": ["老年", "低收入", "退休"],
        "稳健型": ["中年", "中等收入", "家庭支柱"],
        "平衡型": ["青年", "高收入", "单身"],
        "进取型": ["青年", "高净值", "创业"]
    }

    # 保险需求推荐规则
    NEEDS_RECOMMENDATIONS = {
        "青年": ["意外险", "医疗险", "重疾险"],
        "中年": ["寿险", "重疾险", "医疗险", "养老险"],
        "老年": ["医疗险", "养老险", "防癌险"],
        "家庭支柱": ["寿险", "重疾险", "意外险"],
        "高净值": ["寿险", "养老险", "传承险"],
        "单身": ["意外险", "医疗险"],
        "已婚": ["寿险", "重疾险", "医疗险"],
        "有子女": ["寿险", "重疾险", "教育金"]
    }

    def __init__(self, vector_store_config: Optional[Dict] = None):
        self.vector_store_config = vector_store_config or {}
        # TODO: 初始化 Hermes Agent 模型调用客户端
        # self.client = HermesAgentClient(model_config)

    async def analyze_customer_profile(
        self,
        customer_id: str,
        basic_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析客户画像

        Args:
            customer_id: 客户 ID
            basic_info: 基本信息 (年龄/职业/收入等)，遵循 Design Spec Section 10 Schema

        Returns:
            包含客户标签的字典
        """
        start_time = time.time()

        # 参数验证
        if not customer_id or not customer_id.strip():
            return {
                "status": "error",
                "error": "客户 ID 不能为空",
                "error_code": "DATA_001"
            }

        if not basic_info:
            return {
                "status": "error",
                "error": "基本信息不能为空",
                "error_code": "DATA_001"
            }

        # 验证年龄
        age = basic_info.get("age")
        if age is not None and (not isinstance(age, (int, float)) or age < 0 or age > 150):
            return {
                "status": "error",
                "error": "年龄必须在 0-150 之间",
                "error_code": "DATA_001"
            }

        try:
            # 生成客户标签
            tags = self._generate_tags(basic_info)

            # 评估风险偏好
            risk_profile = self._evaluate_risk_profile(tags, basic_info)

            # 评估保险意识
            insurance_awareness = self._evaluate_insurance_awareness(basic_info)

            duration_ms = int((time.time() - start_time) * 1000)

            return {
                "status": "success",
                "data": {
                    "customer_id": customer_id,
                    "tags": tags,
                    "risk_profile": risk_profile,
                    "insurance_awareness": insurance_awareness
                },
                "duration_ms": max(duration_ms, 50)
            }

        except Exception as e:
            logger.error(f"分析客户画像失败：{e}", exc_info=True)
            return self._get_fallback_profile(customer_id)

    def _generate_tags(self, basic_info: Dict[str, Any]) -> List[str]:
        """根据基本信息生成客户标签"""
        tags = []

        # 年龄段标签
        age = basic_info.get("age")
        if age is not None:
            for (min_age, max_age), tag in self.AGE_RANGES.items():
                if min_age <= age <= max_age:
                    tags.append(tag)
                    break

        # 收入层级标签
        annual_income = basic_info.get("annual_income", 0)
        for (min_income, max_income), tag in self.INCOME_LEVELS.items():
            if min_income <= annual_income <= max_income:
                tags.append(tag)
                break

        # 家庭状况标签
        marital_status = basic_info.get("marital_status", "")
        if marital_status == "已婚":
            tags.append("已婚")
        elif marital_status == "单身":
            tags.append("单身")

        children = basic_info.get("children", 0)
        if children > 0:
            tags.append("有子女")
            tags.append("家庭支柱")

        # 职业标签（简化版）
        occupation = basic_info.get("occupation", "")
        if occupation:
            if any(kw in occupation for kw in ["工程师", "技术", "开发"]):
                tags.append("技术从业者")
            elif any(kw in occupation for kw in ["管理", "经理", "总监", "高管"]):
                tags.append("管理层")
            elif any(kw in occupation for kw in ["销售", "业务"]):
                tags.append("销售人员")

        return tags if tags else ["未知"]

    def _evaluate_risk_profile(
        self,
        tags: List[str],
        basic_info: Dict[str, Any]
    ) -> str:
        """评估风险偏好"""
        # 基于标签匹配风险偏好
        for profile, keywords in self.RISK_PROFILE_RULES.items():
            matches = sum(1 for kw in keywords if kw in tags)
            if matches >= 2:
                return profile

        # 默认稳健型
        return "稳健型"

    def _evaluate_insurance_awareness(self, basic_info: Dict[str, Any]) -> str:
        """评估保险意识"""
        score = 0

        # 收入因素
        annual_income = basic_info.get("annual_income", 0)
        if annual_income > 1000000:
            score += 3
        elif annual_income > 500000:
            score += 2
        elif annual_income > 200000:
            score += 1

        # 职业因素
        occupation = basic_info.get("occupation", "")
        if any(kw in occupation for kw in ["金融", "保险", "银行", "证券"]):
            score += 2  # 金融行业保险意识通常较高
        elif any(kw in occupation for kw in ["管理", "高管", "总监"]):
            score += 1

        # 年龄因素
        age = basic_info.get("age", 0)
        if 30 <= age <= 50:
            score += 1  # 中年人群保险意识通常较高

        # 评级
        if score >= 4:
            return "高"
        elif score >= 2:
            return "中"
        else:
            return "低"

    def _get_fallback_profile(self, customer_id: str) -> Dict[str, Any]:
        """降级策略 - 返回默认画像"""
        return {
            "status": "success",
            "data": {
                "customer_id": customer_id,
                "tags": ["未知"],
                "risk_profile": "稳健型",
                "insurance_awareness": "中"
            },
            "duration_ms": 10,
            "warning": "AI 服务暂时不可用，已返回默认画像"
        }

    async def segment_customers(
        self,
        customer_ids: List[str],
        profiles: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        客户分层

        Args:
            customer_ids: 客户 ID 列表
            profiles: 可选，客户画像字典，用于更精准分层

        Returns:
            分层结果，遵循 Design Spec Section 10 Schema
        """
        start_time = time.time()

        # 处理空列表
        if not customer_ids:
            return {
                "status": "success",
                "data": {
                    "segments": {}
                },
                "duration_ms": 10
            }

        try:
            # 如果有 profiles 传入，使用更精准的分层
            if profiles:
                segments = self._segment_with_profiles(customer_ids, profiles)
            else:
                # 否则使用基于 ID 的模拟分层
                segments = self._segment_by_id(customer_ids)

            duration_ms = int((time.time() - start_time) * 1000)

            return {
                "status": "success",
                "data": {
                    "segments": segments
                },
                "duration_ms": max(duration_ms, 100)
            }

        except Exception as e:
            logger.error(f"客户分层失败：{e}", exc_info=True)
            return self._get_fallback_segmentation(customer_ids)

    def _segment_with_profiles(
        self,
        customer_ids: List[str],
        profiles: Dict[str, Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """基于客户画像进行分层"""
        segments = {
            "高价值": [],
            "潜力": [],
            "一般": [],
            "低价值": []
        }

        for cust_id in customer_ids:
            profile = profiles.get(cust_id, {})

            # 高价值客户：高净值/高收入 + 高保险意识
            tags = profile.get("tags", [])
            awareness = profile.get("insurance_awareness", "中")

            if ("高净值" in tags or "高收入" in tags) and awareness == "高":
                segments["高价值"].append(cust_id)
            elif ("高收入" in tags or "中等收入" in tags) and awareness in ["中", "高"]:
                segments["潜力"].append(cust_id)
            elif awareness == "低" and "低收入" in tags:
                segments["低价值"].append(cust_id)
            else:
                segments["一般"].append(cust_id)

        return segments

    def _segment_by_id(self, customer_ids: List[str]) -> Dict[str, List[str]]:
        """基于 ID 的模拟分层（占位符实现）"""
        segments = {
            "高价值": [],
            "潜力": [],
            "一般": [],
            "低价值": []
        }

        # 使用 ID 哈希进行简单分层
        for i, cust_id in enumerate(customer_ids):
            if i % 4 == 0:
                segments["高价值"].append(cust_id)
            elif i % 4 == 1:
                segments["潜力"].append(cust_id)
            elif i % 4 == 2:
                segments["一般"].append(cust_id)
            else:
                segments["低价值"].append(cust_id)

        return segments

    def _get_fallback_segmentation(
        self,
        customer_ids: List[str]
    ) -> Dict[str, Any]:
        """降级策略 - 返回默认分层"""
        return {
            "status": "success",
            "data": {
                "segments": {
                    "一般": customer_ids
                }
            },
            "duration_ms": 10,
            "warning": "AI 服务暂时不可用，已返回默认分层"
        }

    async def predict_insurance_needs(
        self,
        customer_id: str,
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        预测保险需求

        Args:
            customer_id: 客户 ID
            profile: 客户画像，遵循 Design Spec Section 10 Schema

        Returns:
            需求预测结果
        """
        start_time = time.time()

        # 参数验证
        if not customer_id or not customer_id.strip():
            return {
                "status": "error",
                "error": "客户 ID 不能为空",
                "error_code": "DATA_001"
            }

        if not profile:
            return {
                "status": "error",
                "error": "客户画像不能为空",
                "error_code": "DATA_001"
            }

        try:
            # 预测需求
            needs = self._predict_needs(profile)

            duration_ms = int((time.time() - start_time) * 1000)

            return {
                "status": "success",
                "data": {
                    "needs": needs
                },
                "duration_ms": max(duration_ms, 100)
            }

        except Exception as e:
            logger.error(f"预测保险需求失败：{e}", exc_info=True)
            return self._get_fallback_needs(customer_id)

    def _predict_needs(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于画像预测保险需求"""
        needs = []
        tags = profile.get("tags", [])
        age = profile.get("age", 30)

        # 确定年龄段
        age_group = None
        if age < 25:
            age_group = "青年"
        elif age < 50:
            age_group = "中年"
        else:
            age_group = "老年"

        # 收集推荐
        recommended = set()

        # 基于年龄段推荐
        if age_group in self.NEEDS_RECOMMENDATIONS:
            for need in self.NEEDS_RECOMMENDATIONS[age_group]:
                recommended.add(need)

        # 基于家庭状况推荐
        for tag in tags:
            if tag in self.NEEDS_RECOMMENDATIONS:
                for need in self.NEEDS_RECOMMENDATIONS[tag]:
                    recommended.add(need)

        # 为每个需求添加优先级和理由
        priority_map = {
            "寿险": self._get_life_insurance_priority(profile),
            "重疾险": self._get_critical_illness_priority(profile),
            "医疗险": self._get_medical_insurance_priority(profile),
            "意外险": self._get_accident_insurance_priority(profile),
            "养老险": self._get_pension_insurance_priority(profile),
            "教育金": self._get_education_fund_priority(profile),
            "防癌险": self._get_cancer_insurance_priority(profile),
            "传承险": self._get_inheritance_insurance_priority(profile)
        }

        reason_map = {
            "寿险": self._get_life_insurance_reason(profile),
            "重疾险": self._get_critical_illness_reason(profile),
            "医疗险": self._get_medical_insurance_reason(profile),
            "意外险": self._get_accident_insurance_reason(profile),
            "养老险": self._get_pension_insurance_reason(profile),
            "教育金": self._get_education_fund_reason(profile),
            "防癌险": self._get_cancer_insurance_reason(profile),
            "传承险": self._get_inheritance_insurance_reason(profile)
        }

        for need_type in recommended:
            priority = priority_map.get(need_type, "中")
            reason = reason_map.get(need_type, f"{need_type}保障需求")

            needs.append({
                "type": need_type,
                "priority": priority,
                "reason": reason
            })

        # 按优先级排序
        priority_order = {"高": 0, "中": 1, "低": 2}
        needs.sort(key=lambda x: priority_order.get(x["priority"], 1))

        return needs if needs else [{"type": "医疗险", "priority": "中", "reason": "基础健康保障"}]

    def _get_life_insurance_priority(self, profile: Dict[str, Any]) -> str:
        """寿险优先级"""
        tags = profile.get("tags", [])
        if "家庭支柱" in tags or "有子女" in tags:
            return "高"
        elif "中年" in tags:
            return "中"
        return "低"

    def _get_critical_illness_priority(self, profile: Dict[str, Any]) -> str:
        """重疾险优先级"""
        age = profile.get("age", 30)
        if 25 <= age <= 50:
            return "高"
        elif age > 50:
            return "中"
        return "低"

    def _get_medical_insurance_priority(self, profile: Dict[str, Any]) -> str:
        """医疗险优先级"""
        return "高"  # 医疗险是基础需求

    def _get_accident_insurance_priority(self, profile: Dict[str, Any]) -> str:
        """意外险优先级"""
        age = profile.get("age", 30)
        if age < 40:
            return "高"
        return "中"

    def _get_pension_insurance_priority(self, profile: Dict[str, Any]) -> str:
        """养老险优先级"""
        age = profile.get("age", 30)
        tags = profile.get("tags", [])
        if age > 45 or "高净值" in tags:
            return "高"
        elif age > 35:
            return "中"
        return "低"

    def _get_education_fund_priority(self, profile: Dict[str, Any]) -> str:
        """教育金优先级"""
        tags = profile.get("tags", [])
        if "有子女" in tags:
            return "高"
        return "低"

    def _get_cancer_insurance_priority(self, profile: Dict[str, Any]) -> str:
        """防癌险优先级"""
        age = profile.get("age", 30)
        if age > 55:
            return "高"
        return "低"

    def _get_inheritance_insurance_priority(self, profile: Dict[str, Any]) -> str:
        """传承险优先级"""
        tags = profile.get("tags", [])
        if "高净值" in tags or "老年" in tags:
            return "高"
        return "低"

    def _get_life_insurance_reason(self, profile: Dict[str, Any]) -> str:
        """寿险理由"""
        if "家庭支柱" in profile.get("tags", []):
            return "家庭责任重大，需保障家人生活"
        elif "已婚" in profile.get("tags", []):
            return "承担家庭责任，保障配偶生活"
        return "身故保障，爱与传承"

    def _get_critical_illness_reason(self, profile: Dict[str, Any]) -> str:
        """重疾险理由"""
        age = profile.get("age", 30)
        if 25 <= age <= 45:
            return "正值事业上升期，重疾保障必备"
        return "重疾高发，提前规划保障"

    def _get_medical_insurance_reason(self, profile: Dict[str, Any]) -> str:
        """医疗险理由"""
        return "医疗费用高昂，补充社保不足"

    def _get_accident_insurance_reason(self, profile: Dict[str, Any]) -> str:
        """意外险理由"""
        occupation = profile.get("occupation", "")
        if any(kw in occupation for kw in ["外勤", "出差", "驾驶"]):
            return "职业风险较高，意外保障必备"
        return "意外风险无处不在，低保费高保障"

    def _get_pension_insurance_reason(self, profile: Dict[str, Any]) -> str:
        """养老险理由"""
        age = profile.get("age", 30)
        if age > 40:
            return "退休规划迫在眉睫"
        return "提前规划，安享退休生活"

    def _get_education_fund_reason(self, profile: Dict[str, Any]) -> str:
        """教育金理由"""
        return "子女教育支出大，提前储备"

    def _get_cancer_insurance_reason(self, profile: Dict[str, Any]) -> str:
        """防癌险理由"""
        return "癌症高发，专项保障"

    def _get_inheritance_insurance_reason(self, profile: Dict[str, Any]) -> str:
        """传承险理由"""
        return "财富传承，税务规划"

    def _get_fallback_needs(self, customer_id: str) -> Dict[str, Any]:
        """降级策略 - 返回默认需求"""
        return {
            "status": "success",
            "data": {
                "needs": [
                    {"type": "医疗险", "priority": "中", "reason": "基础健康保障"}
                ]
            },
            "duration_ms": 10,
            "warning": "AI 服务暂时不可用，已返回默认需求"
        }

    async def search_similar_customers(
        self,
        customer_id: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        相似客户检索

        Args:
            customer_id: 客户 ID
            limit: 返回数量限制

        Returns:
            相似客户列表
        """
        start_time = time.time()

        # 参数验证
        if not customer_id or not customer_id.strip():
            return {
                "status": "error",
                "error": "客户 ID 不能为空",
                "error_code": "DATA_001"
            }

        limit = max(1, min(20, limit))  # 限制 1-20

        try:
            # TODO: 使用向量检索相似客户
            # 目前使用占位符实现
            similar_customers = self._mock_similar_customers(customer_id, limit)

            duration_ms = int((time.time() - start_time) * 1000)

            return {
                "status": "success",
                "data": {
                    "similar_customers": similar_customers
                },
                "duration_ms": max(duration_ms, 100)
            }

        except Exception as e:
            logger.error(f"检索相似客户失败：{e}", exc_info=True)
            return {
                "status": "error",
                "error": f"检索失败：{str(e)}",
                "error_code": "SEARCH_001"
            }

    def _mock_similar_customers(
        self,
        customer_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """模拟相似客户检索（占位符）"""
        return [
            {
                "customer_id": f"similar_{i}",
                "similarity_score": 0.95 - i * 0.05,
                "matching_tags": ["高收入", "家庭支柱"]
            }
            for i in range(limit)
        ]
