"""
API 路由实现

遵循 Design Spec Section 10 定义的接口规范
"""

from fastapi import APIRouter, HTTPException, Request
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
    ContentReviewRequest,
    AuditLogQueryRequest,
    SensitiveWordManageRequest,
)
from ..skills.content_gen import ContentGenerator
from ..skills.customer import CustomerAnalyst
from ..skills.followup import FollowupManager
from ..skills.compliance import ComplianceReviewer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# 初始化技能实例（LLM Provider 延迟初始化）
_content_generator = ContentGenerator()
_customer_analyst = CustomerAnalyst()
_followup_manager = FollowupManager()
_compliance_reviewer = ComplianceReviewer()


# ==================== 健康检查 ====================


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "service": "保客通 (BaokeTong)",
    }


# ==================== 内容生成 API ====================


@router.post("/content/generate")
async def content_generate_api(request: ContentGenerateRequest, req: Request):
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
            count=request.count,
            user_id=getattr(req.state, "user_id", None),
            ip_address=req.client.host if req.client else None,
        )
        return result
    except Exception as e:
        logger.error(f"内容生成失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"内容生成失败：{str(e)}")


@router.post("/content/video-script")
async def video_script_api(request: VideoScriptRequest):
    """
    短视频脚本生成 API
    """
    try:
        result = await _content_generator.generate_short_video_script(
            topic=request.topic,
            duration=request.duration,
            style=request.style,
        )
        return result
    except Exception as e:
        logger.error(f"短视频脚本生成失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"脚本生成失败：{str(e)}")


@router.post("/content/poster")
async def poster_api(request: PosterRequest):
    """
    海报文案生成 API
    """
    try:
        result = await _content_generator.generate_poster_copywriting(
            product_name=request.product_name,
            selling_point=request.selling_point,
            cta=request.cta,
        )
        return result
    except Exception as e:
        logger.error(f"海报文案生成失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"海报文案生成失败：{str(e)}")


# ==================== 客户分析 API ====================


@router.post("/customer/analyze")
async def customer_analyze_api(request: CustomerProfileRequest, req: Request):
    """
    客户画像分析 API

    遵循 Design Spec Section 10.1 Schema
    """
    try:
        result = await _customer_analyst.analyze_customer_profile(
            customer_id=request.customer_id,
            basic_info=request.basic_info,
        )
        return result
    except Exception as e:
        logger.error(f"客户画像分析失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"客户分析失败：{str(e)}")


@router.post("/customer/segment")
async def customer_segment_api(request: CustomerSegmentRequest):
    """
    客户分层 API
    """
    try:
        # profiles 在 schema 中是 Dict[str, Dict]，转为 List[Dict] 传给 skill
        profiles = None
        if request.profiles:
            profiles = list(request.profiles.values())
        result = await _customer_analyst.segment_customers(
            customer_ids=request.customer_ids,
            profiles=profiles,
        )
        return result
    except Exception as e:
        logger.error(f"客户分层失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"客户分层失败：{str(e)}")


@router.post("/customer/needs")
async def customer_needs_api(request: CustomerNeedsRequest):
    """
    需求预测 API
    """
    try:
        result = await _customer_analyst.predict_insurance_needs(
            customer_id=request.customer_id,
            profile=request.profile,
        )
        return result
    except Exception as e:
        logger.error(f"需求预测失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"需求预测失败：{str(e)}")


@router.post("/customer/search-similar")
async def search_similar_customers_api(request: SimilarCustomerRequest):
    """
    相似客户检索 API

    注意：当前为 stub 实现，需要 Qdrant 向量检索支持。
    """
    try:
        result = await _customer_analyst.search_similar_customers(
            customer_id=request.customer_id,
            limit=request.limit,
        )
        return result
    except AttributeError:
        # search_similar_customers 尚未实现
        return {
            "status": "success",
            "data": {
                "customer_id": request.customer_id,
                "similar_customers": [],
                "note": "向量检索功能尚未实现",
            },
            "duration_ms": 0,
        }
    except Exception as e:
        logger.error(f"相似客户检索失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"检索失败：{str(e)}")


# ==================== 跟进管理 API ====================


@router.post("/followup/create")
async def followup_create_api(request: FollowupPlanRequest, req: Request):
    """
    跟进计划创建 API

    遵循 Design Spec Section 10.1 Schema
    """
    try:
        result = await _followup_manager.create_followup_plan(
            customer_id=request.customer_id,
            plan_duration=request.plan_duration,
            frequency=request.frequency,
        )
        return result
    except Exception as e:
        logger.error(f"跟进计划创建失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"跟进计划创建失败：{str(e)}")


@router.post("/followup/schedule")
async def followup_schedule_api(request: AutomatedMessageRequest):
    """
    定时消息推送 API
    """
    try:
        result = await _followup_manager.schedule_automated_message(
            customer_id=request.customer_id,
            message_content=request.message_content,
            send_time=request.send_time,
        )
        return result
    except Exception as e:
        logger.error(f"定时消息调度失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"消息调度失败：{str(e)}")


@router.post("/followup/log")
async def followup_log_api(request: FollowupRecordRequest):
    """
    跟进记录 API
    """
    try:
        result = await _followup_manager.log_followup_record(
            customer_id=request.customer_id,
            followup_type=request.followup_type,
            content=request.content,
            feedback=request.feedback,
        )
        return result
    except Exception as e:
        logger.error(f"跟进记录失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"跟进记录失败：{str(e)}")


# ==================== 合规审核 API ====================


@router.post("/compliance/review")
async def compliance_review_api(request: ContentReviewRequest, req: Request):
    """
    内容合规审核 API

    对内容进行敏感词过滤 + AI 语义审核，返回审核结果。
    """
    try:
        user_id = getattr(req.state, "user_id", None) or "anonymous"
        result = await _compliance_reviewer.review_content(
            content=request.content,
            user_id=user_id,
            content_type=request.content_type,
            product_name=request.product_name,
            ip_address=req.client.host if req.client else None,
        )
        return {
            "status": "success",
            "data": result["data"],
            "duration_ms": result.get("duration_ms"),
        }
    except Exception as e:
        logger.error(f"合规审核失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"审核失败：{str(e)}")


@router.post("/compliance/audit-logs")
async def compliance_audit_logs_api(request: AuditLogQueryRequest):
    """
    审计日志查询 API

    支持按用户、操作类型、审核状态、时间范围过滤。
    """
    try:
        logs = _compliance_reviewer.get_audit_logs(
            user_id=request.user_id,
            action=request.action,
            review_status=request.review_status,
            start_time=request.start_time,
            end_time=request.end_time,
            limit=request.limit,
        )
        return {
            "status": "success",
            "data": {"logs": logs, "total": len(logs)},
            "duration_ms": 0,
        }
    except Exception as e:
        logger.error(f"审计日志查询失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"审计日志查询失败：{str(e)}")


@router.post("/compliance/sensitive-words/add")
async def compliance_add_sensitive_word_api(request: SensitiveWordManageRequest):
    """
    添加敏感词 API
    """
    try:
        _compliance_reviewer.add_sensitive_word(request.word)
        return {
            "status": "success",
            "data": {"word": request.word, "action": "added"},
            "duration_ms": 0,
        }
    except Exception as e:
        logger.error(f"添加敏感词失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"添加敏感词失败：{str(e)}")


@router.post("/compliance/sensitive-words/remove")
async def compliance_remove_sensitive_word_api(request: SensitiveWordManageRequest):
    """
    移除敏感词 API
    """
    try:
        _compliance_reviewer.remove_sensitive_word(request.word)
        return {
            "status": "success",
            "data": {"word": request.word, "action": "removed"},
            "duration_ms": 0,
        }
    except Exception as e:
        logger.error(f"移除敏感词失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"移除敏感词失败：{str(e)}")


@router.get("/compliance/sensitive-words")
async def compliance_list_sensitive_words_api():
    """
    获取敏感词列表 API
    """
    try:
        words = _compliance_reviewer.sensitive_words
        return {
            "status": "success",
            "data": {"words": words, "total": len(words)},
            "duration_ms": 0,
        }
    except Exception as e:
        logger.error(f"获取敏感词列表失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取敏感词列表失败：{str(e)}")
