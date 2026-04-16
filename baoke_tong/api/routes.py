"""
API 路由实现

遵循 Design Spec Section 10 定义的接口规范
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Optional
import logging

from .schemas import (
    ContentGenerateRequest,
    VideoScriptRequest,
    PosterRequest,
    CustomerProfileRequest,
    CustomerSegmentRequest,
    CustomerNeedsRequest,
    SimilarCustomerRequest,
    FollowupPlanRequest,
    AutomatedMessageRequest,
    FollowupRecordRequest,
)
from ..skills.content_gen import ContentGenerator
from ..skills.customer import CustomerAnalyst
from ..skills.followup import FollowupManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# 初始化技能实例
_content_generator = ContentGenerator()
_customer_analyst = CustomerAnalyst()
_followup_manager = FollowupManager()


# ==================== 健康检查 ====================


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "service": "保客通 (BaokeTong)"
    }


# ==================== 内容生成 API ====================


@router.post("/content/generate", response_model=dict)
async def content_generate_api(request: ContentGenerateRequest):
    """
    内容生成 API - 朋友圈文案生成

    遵循 Design Spec Section 10.1 Schema
    """
    try:
        result = await _content_generator.generate_wechat_copywriting(
            product_name=request.product_name,
            product_type=request.product_type,
            target_audience=request.target_audience,
            tone=request.tone,
            count=request.count
        )
        return result
    except Exception as e:
        logger.error(f"内容生成失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内容生成失败：{str(e)}")


@router.post("/content/video-script", response_model=dict)
async def video_script_api(request: VideoScriptRequest):
    """
    短视频脚本生成 API
    """
    try:
        result = await _content_generator.generate_short_video_script(
            topic=request.topic,
            duration=request.duration,
            style=request.style
        )
        return result
    except Exception as e:
        logger.error(f"短视频脚本生成失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"脚本生成失败：{str(e)}")


@router.post("/content/poster", response_model=dict)
async def poster_api(request: PosterRequest):
    """
    海报文案生成 API
    """
    try:
        result = await _content_generator.generate_poster_copywriting(
            product_name=request.product_name,
            selling_point=request.selling_point,
            cta=request.cta
        )
        return result
    except Exception as e:
        logger.error(f"海报文案生成失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"海报文案生成失败：{str(e)}")


# ==================== 客户分析 API ====================


@router.post("/customer/analyze", response_model=dict)
async def customer_analyze_api(request: CustomerProfileRequest):
    """
    客户画像分析 API

    遵循 Design Spec Section 10.1 Schema
    """
    try:
        result = await _customer_analyst.analyze_customer_profile(
            customer_id=request.customer_id,
            basic_info=request.basic_info
        )
        return result
    except Exception as e:
        logger.error(f"客户画像分析失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"客户分析失败：{str(e)}")


@router.post("/customer/segment", response_model=dict)
async def customer_segment_api(request: CustomerSegmentRequest):
    """
    客户分层 API
    """
    try:
        result = await _customer_analyst.segment_customers(
            customer_ids=request.customer_ids,
            profiles=request.profiles
        )
        return result
    except Exception as e:
        logger.error(f"客户分层失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"客户分层失败：{str(e)}")


@router.post("/customer/needs", response_model=dict)
async def customer_needs_api(request: CustomerNeedsRequest):
    """
    需求预测 API
    """
    try:
        result = await _customer_analyst.predict_insurance_needs(
            customer_id=request.customer_id,
            profile=request.profile
        )
        return result
    except Exception as e:
        logger.error(f"需求预测失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"需求预测失败：{str(e)}")


@router.post("/customer/search-similar", response_model=dict)
async def search_similar_customers_api(request: SimilarCustomerRequest):
    """
    相似客户检索 API
    """
    try:
        result = await _customer_analyst.search_similar_customers(
            customer_id=request.customer_id,
            limit=request.limit
        )
        return result
    except Exception as e:
        logger.error(f"相似客户检索失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"检索失败：{str(e)}")


# ==================== 跟进管理 API ====================


@router.post("/followup/create", response_model=dict)
async def followup_create_api(request: FollowupPlanRequest):
    """
    跟进计划创建 API

    遵循 Design Spec Section 10.1 Schema
    """
    try:
        result = await _followup_manager.create_followup_plan(
            customer_id=request.customer_id,
            plan_duration=request.plan_duration,
            frequency=request.frequency
        )
        return result
    except Exception as e:
        logger.error(f"跟进计划创建失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"跟进计划创建失败：{str(e)}")


@router.post("/followup/schedule", response_model=dict)
async def followup_schedule_api(request: AutomatedMessageRequest):
    """
    定时消息推送 API
    """
    try:
        result = await _followup_manager.schedule_automated_message(
            customer_id=request.customer_id,
            message_content=request.message_content,
            send_time=request.send_time
        )
        return result
    except Exception as e:
        logger.error(f"定时消息调度失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"消息调度失败：{str(e)}")


@router.post("/followup/log", response_model=dict)
async def followup_log_api(request: FollowupRecordRequest):
    """
    跟进记录 API
    """
    try:
        result = await _followup_manager.log_followup_record(
            customer_id=request.customer_id,
            followup_type=request.followup_type,
            content=request.content,
            feedback=request.feedback
        )
        return result
    except Exception as e:
        logger.error(f"跟进记录失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"跟进记录失败：{str(e)}")
