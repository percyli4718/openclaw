"""
Pydantic Schema 定义

遵循 Design Spec Section 10.1 输入/输出 Schema
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime


# ==================== 通用响应 Schema ====================


class APIResponse(BaseModel):
    """API 响应基础 Schema"""
    status: str = Field(..., description="响应状态：success/error")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")
    error_code: Optional[str] = Field(None, description="错误码")
    duration_ms: Optional[int] = Field(None, description="执行耗时 (毫秒)")


# ==================== 内容生成相关 Schema ====================


class ContentGenerateRequest(BaseModel):
    """内容生成请求"""
    product_name: str = Field(..., description="保险产品名称")
    product_type: Literal["重疾险", "医疗险", "寿险", "意外险"] = Field(
        ...,
        description="产品类型",
    )
    target_audience: Optional[str] = Field(None, description="目标客户群体")
    tone: Literal["专业", "亲和", "幽默", "紧迫"] = Field(
        default="专业",
        description="文案风格",
    )
    count: int = Field(default=3, ge=1, le=5, description="生成条数")


class ContentGenerateResponse(BaseModel):
    """内容生成响应"""
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    duration_ms: Optional[int] = None


class VideoScriptRequest(BaseModel):
    """短视频脚本请求"""
    topic: str = Field(..., description="视频主题")
    duration: Literal[15, 30, 60] = Field(default=30, description="视频时长 (秒)")
    style: Literal["科普", "剧情", "访谈"] = Field(default="科普", description="风格")


class PosterRequest(BaseModel):
    """海报文案请求"""
    product_name: str = Field(..., description="保险产品名称")
    selling_point: str = Field(..., description="卖点")
    cta: Optional[str] = Field(None, description="行动号召")


# ==================== 客户分析相关 Schema ====================


class CustomerProfileRequest(BaseModel):
    """客户画像请求"""
    customer_id: str = Field(..., description="客户 ID")
    basic_info: Dict[str, Any] = Field(..., description="基本信息")


class CustomerProfileResponse(BaseModel):
    """客户画像响应"""
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    duration_ms: Optional[int] = None


class CustomerSegmentRequest(BaseModel):
    """客户分层请求"""
    customer_ids: List[str] = Field(..., description="客户 ID 列表")
    profiles: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="客户画像")


class CustomerNeedsRequest(BaseModel):
    """需求预测请求"""
    customer_id: str = Field(..., description="客户 ID")
    profile: Dict[str, Any] = Field(..., description="客户画像")


class SimilarCustomerRequest(BaseModel):
    """相似客户请求"""
    customer_id: str = Field(..., description="客户 ID")
    limit: int = Field(default=5, ge=1, le=20, description="返回数量")


# ==================== 跟进管理相关 Schema ====================


class FollowupPlanRequest(BaseModel):
    """跟进计划请求"""
    customer_id: str = Field(..., description="客户 ID")
    plan_duration: int = Field(default=30, ge=1, le=3650, description="计划天数")
    frequency: Literal["daily", "weekly", "monthly"] = Field(
        default="weekly",
        description="跟进频率",
    )


class FollowupPlanResponse(BaseModel):
    """跟进计划响应"""
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    duration_ms: Optional[int] = None


class AutomatedMessageRequest(BaseModel):
    """定时消息请求"""
    customer_id: str = Field(..., description="客户 ID")
    message_content: str = Field(..., description="消息内容")
    send_time: datetime = Field(..., description="发送时间")


class FollowupRecordRequest(BaseModel):
    """跟进记录请求"""
    customer_id: str = Field(..., description="客户 ID")
    followup_type: str = Field(..., description="跟进类型")
    content: str = Field(..., description="跟进内容")
    feedback: Optional[str] = Field(None, description="客户反馈")


# ==================== 认证相关 Schema ====================


class TokenRequest(BaseModel):
    """Token 请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # 默认 1 小时过期


class TenantContext(BaseModel):
    """租户上下文"""
    tenant_id: str
    tenant_name: Optional[str] = None
