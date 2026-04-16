"""
内容生成技能

基于 Hermes Agent 的保险行业内容生成：
- generate_wechat_copywriting: 朋友圈文案生成
- generate_short_video_script: 短视频脚本生成
- generate_poster_copywriting: 海报文案生成
"""

from typing import List, Dict, Any, Optional
import time
import uuid
import logging

logger = logging.getLogger(__name__)


class ContentGenerator:
    """保险行业内容生成器"""

    # 文案风格提示词模板
    TONE_TEMPLATES = {
        "专业": "用专业、权威的语气，强调产品保障和可靠性",
        "亲和": "用温暖、亲切的语气，像朋友一样推荐",
        "幽默": "用轻松、幽默的语气，让保险不再沉重",
        "紧迫": "用紧迫感的语气，强调限时优惠和风险警示"
    }

    # 产品类型关键词
    PRODUCT_KEYWORDS = {
        "重疾险": ["重大疾病", "健康保障", "确诊即赔", "医疗负担"],
        "医疗险": ["医疗费用", "报销", "看病不愁", "住院保障"],
        "寿险": ["家庭责任", "爱与传承", "终身保障", "安心传承"],
        "意外险": ["意外风险", "突发状况", "出行保障", "全方位守护"]
    }

    def __init__(self, model_config: Optional[Dict] = None):
        self.model_config = model_config or {}
        # TODO: 初始化 Hermes Agent 模型调用客户端
        # self.client = HermesAgentClient(model_config)

    async def generate_wechat_copywriting(
        self,
        product_name: str,
        product_type: str,
        target_audience: Optional[str] = None,
        tone: str = "专业",
        count: int = 3
    ) -> Dict[str, Any]:
        """
        生成朋友圈文案

        Args:
            product_name: 保险产品名称
            product_type: 产品类型 (重疾险/医疗险/寿险/意外险)
            target_audience: 目标客户群体
            tone: 文案风格 (专业/亲和/幽默/紧迫)
            count: 生成条数 (1-5)

        Returns:
            包含文案列表的字典，遵循 Design Spec Section 10.1 Schema
        """
        start_time = time.time()

        # 参数验证
        if not product_name or not product_name.strip():
            return {
                "status": "error",
                "error": "产品名称不能为空",
                "error_code": "DATA_001"
            }

        valid_product_types = ["重疾险", "医疗险", "寿险", "意外险"]
        if product_type not in valid_product_types:
            return {
                "status": "error",
                "error": f"无效的产品类型，必须是：{', '.join(valid_product_types)}",
                "error_code": "DATA_001"
            }

        # 限制 count 范围
        count = max(1, min(5, count))

        try:
            # TODO: 调用 Hermes Agent 技能执行
            # 目前使用占位符实现，后续接入真实 AI 模型
            copies = self._generate_mock_copies(
                product_name=product_name,
                product_type=product_type,
                target_audience=target_audience,
                tone=tone,
                count=count
            )

            duration_ms = int((time.time() - start_time) * 1000)

            return {
                "status": "success",
                "data": {
                    "copies": copies
                },
                "duration_ms": max(duration_ms, 100)  # 模拟 AI 调用耗时
            }

        except Exception as e:
            logger.error(f"生成文案失败：{e}", exc_info=True)
            # 降级策略 - 返回预置模板
            return self._get_fallback_copies(count, product_type)

    def _generate_mock_copies(
        self,
        product_name: str,
        product_type: str,
        target_audience: Optional[str],
        tone: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """生成模拟文案（占位符实现）"""
        copies = []
        tone_desc = self.TONE_TEMPLATES.get(tone, "专业")
        keywords = self.PRODUCT_KEYWORDS.get(product_type, ["保障"])

        for i in range(count):
            copy_id = f"copy_{uuid.uuid4().hex[:8]}"

            # 根据风格和产品类型生成不同的文案模板
            content = self._generate_copy_content(
                product_name=product_name,
                product_type=product_type,
                keywords=keywords,
                target_audience=target_audience,
                tone=tone,
                variant=i
            )

            hashtags = self._generate_hashtags(product_type, tone)

            copies.append({
                "id": copy_id,
                "content": content,
                "hashtags": hashtags,
                "score": 0.75 + (0.25 * (i + 1) / count)  # 模拟评分
            })

        return copies

    def _generate_copy_content(
        self,
        product_name: str,
        product_type: str,
        keywords: List[str],
        target_audience: Optional[str],
        tone: str,
        variant: int
    ) -> str:
        """根据风格和产品类型生成文案内容"""
        # 从关键词中选择一个融入文案
        keyword = keywords[variant % len(keywords)] if keywords else "保障"

        templates = {
            "专业": [
                f"【{product_name}】专业保障，为您的未来保驾护航。{keyword}，值得信赖。",
                f"选择{product_name}，就是选择一份安心的保障。{keyword}，专业团队，贴心服务。",
                f"{product_name} - 用专业守护您和家人的幸福。{keyword}，保障全面，理赔便捷。",
                f"保险不是消费，是责任。{product_name}，给您最专业的{keyword}方案。",
                f"{product_name}，专注{keyword}领域，服务超过 10 万家庭。专业，所以放心。"
            ],
            "亲和": [
                f"亲爱的朋友们，今天给大家安利{product_name}～{keyword}的贴心保障💕",
                f"有了一份好保险，心里暖暖的～{product_name}，懂你所需，关注{keyword}❤️",
                f"生活不易，但有{product_name}陪伴，{keyword}让每一天都更安心😊",
                f"想对你们说：爱自己，从一份{product_name}开始～关注{keyword}很重要",
                f"感谢信任～{product_name}一直在这里，{keyword}做你最温暖的依靠🌟"
            ],
            "幽默": [
                f"听说买了{product_name}的人，后来都... 更安心地吃喝玩乐了～{keyword}你懂的😄",
                f"人生苦短，保险要选好玩的～{product_name}，{keyword}让保障不再枯燥！",
                f"别人在担心风险，我在{product_name}的保护下安心躺平～因为有{keyword}😎",
                f"买保险也能很开心？{product_name}说：当然可以！{keyword}安排上！",
                f"生活已经很难了，保险就选个靠谱的吧～{product_name}，{keyword}必须安排！"
            ],
            "紧迫": [
                f"⚠️最后 3 天！{product_name}限时优惠，{keyword}不容错过！",
                f"风险不等人！{product_name}{keyword}今天投保，明天生效，立即行动！",
                f"🔥火爆抢购中！{product_name}仅剩最后 50 个名额！{keyword}抓紧！",
                f"别让犹豫成为遗憾！{product_name}，现在就是最好的选择！{keyword}",
                f"紧急提醒：{product_name}优惠活动即将结束！{keyword}抓紧最后机会！"
            ]
        }

        tone_templates = templates.get(tone, templates["专业"])
        content = tone_templates[variant % len(tone_templates)]

        if target_audience:
            content = f"【{target_audience}专享】{content}"

        return content

    def _generate_hashtags(self, product_type: str, tone: str) -> List[str]:
        """生成话题标签"""
        base_tags = ["保险", "保障"]
        type_tags = {
            "重疾险": ["健康", "重疾保障", "医疗费用"],
            "医疗险": ["医疗", "报销", "住院保障"],
            "寿险": ["家庭责任", "传承", "终身保障"],
            "意外险": ["意外", "安全", "出行保障"]
        }
        tone_tags = {
            "专业": ["专业推荐", "值得信赖"],
            "亲和": ["暖心推荐", "好物分享"],
            "幽默": ["轻松一刻", "保险也可以很有趣"],
            "紧迫": ["限时优惠", "不容错过"]
        }

        return (
            base_tags +
            type_tags.get(product_type, []) +
            tone_tags.get(tone, [])
        )[:5]  # 最多 5 个标签

    def _get_fallback_copies(self, count: int, product_type: str) -> Dict[str, Any]:
        """降级策略 - 返回预置模板"""
        fallback_templates = [
            {
                "id": "fallback_001",
                "content": f"【保险服务】专业保障，值得信赖。了解更多详情，请咨询您的保险顾问。",
                "hashtags": ["保险", "保障", "专业服务"],
                "score": 0.6
            }
        ]

        copies = fallback_templates * count

        return {
            "status": "success",
            "data": {"copies": copies[:count]},
            "duration_ms": 50,
            "warning": "AI 服务暂时不可用，已返回预置模板"
        }

    async def generate_short_video_script(
        self,
        topic: str,
        duration: int = 30,
        style: str = "科普"
    ) -> Dict[str, Any]:
        """
        生成短视频脚本

        Args:
            topic: 视频主题
            duration: 视频时长 (秒)，支持 15/30/60
            style: 风格 (科普/剧情/访谈)

        Returns:
            包含脚本的字典，遵循 Design Spec Section 10.1 Schema
        """
        start_time = time.time()

        # 参数验证
        if not topic or not topic.strip():
            return {
                "status": "error",
                "error": "视频主题不能为空",
                "error_code": "DATA_001"
            }

        valid_durations = [15, 30, 60]
        if duration not in valid_durations:
            # 自动转换为最接近的有效时长
            duration = min(valid_durations, key=lambda x: abs(x - duration))

        valid_styles = ["科普", "剧情", "访谈"]
        if style not in valid_styles:
            style = "科普"

        try:
            script = self._generate_mock_script(
                topic=topic,
                duration=duration,
                style=style
            )

            duration_ms = int((time.time() - start_time) * 1000)

            return {
                "status": "success",
                "data": {
                    "script": script
                },
                "duration_ms": max(duration_ms, 500)  # 模拟 AI 调用耗时
            }

        except Exception as e:
            logger.error(f"生成脚本失败：{e}", exc_info=True)
            return self._get_fallback_script(topic)

    def _generate_mock_script(
        self,
        topic: str,
        duration: int,
        style: str
    ) -> Dict[str, Any]:
        """生成模拟脚本（占位符实现）"""
        script_id = f"script_{uuid.uuid4().hex[:8]}"

        # 根据时长和风格生成场景分解
        scenes = self._generate_scenes(topic, duration, style)

        return {
            "id": script_id,
            "title": f"{topic}",
            "duration_seconds": duration,
            "style": style,
            "scenes": scenes,
            "estimated_words": duration * 3  # 约每秒 3 个字
        }

    def _generate_scenes(
        self,
        topic: str,
        duration: int,
        style: str
    ) -> List[Dict[str, Any]]:
        """根据时长和风格生成场景分解"""
        if duration == 15:
            return [
                {"time": "0-3s", "content": f"开场：{topic}，你了解多少？", "type": "hook"},
                {"time": "3-12s", "content": f"核心知识点讲解：{topic}的关键信息", "type": "content"},
                {"time": "12-15s", "content": "总结 + 行动号召：关注我了解更多", "type": "cta"}
            ]
        elif duration == 30:
            if style == "科普":
                return [
                    {"time": "0-5s", "content": f"开场引入：你知道吗？{topic}很重要", "type": "hook"},
                    {"time": "5-10s", "content": "问题呈现：常见的误区和痛点", "type": "problem"},
                    {"time": "10-25s", "content": f"核心内容：{topic}的详细讲解", "type": "content"},
                    {"time": "25-30s", "content": "总结 + CTA：点赞收藏，关注我", "type": "cta"}
                ]
            elif style == "剧情":
                return [
                    {"time": "0-5s", "content": "场景设定：日常生活场景引入", "type": "setup"},
                    {"time": "5-15s", "content": "冲突呈现：遇到问题/困难", "type": "conflict"},
                    {"time": "15-25s", "content": f"解决方案：{topic}相关知识", "type": "resolution"},
                    {"time": "25-30s", "content": "结尾反转/金句总结", "type": "twist"}
                ]
            else:  # 访谈
                return [
                    {"time": "0-5s", "content": "主持人开场 + 嘉宾介绍", "type": "intro"},
                    {"time": "5-15s", "content": f"提问：关于{topic}的疑问", "type": "question"},
                    {"time": "15-25s", "content": "嘉宾解答：专业知识分享", "type": "answer"},
                    {"time": "25-30s", "content": "总结 + 关注引导", "type": "outro"}
                ]
        else:  # 60 秒
            return [
                {"time": "0-5s", "content": f"黄金 5 秒：{topic} hook", "type": "hook"},
                {"time": "5-15s", "content": "背景介绍：为什么这个话题重要", "type": "context"},
                {"time": "15-35s", "content": f"知识点 1: {topic}核心要点", "type": "content"},
                {"time": "35-50s", "content": f"知识点 2: 实际应用案例", "type": "content"},
                {"time": "50-55s", "content": "总结回顾", "type": "summary"},
                {"time": "55-60s", "content": "行动号召：点赞/评论/关注", "type": "cta"}
            ]

    def _get_fallback_script(self, topic: str) -> Dict[str, Any]:
        """降级策略 - 返回预置模板"""
        return {
            "status": "success",
            "data": {
                "script": {
                    "id": "fallback_script_001",
                    "title": topic,
                    "duration_seconds": 30,
                    "style": "科普",
                    "scenes": [
                        {"time": "0-5s", "content": "开场引入"},
                        {"time": "5-25s", "content": "核心内容讲解"},
                        {"time": "25-30s", "content": "总结 + CTA"}
                    ],
                    "estimated_words": 90
                }
            },
            "duration_ms": 50,
            "warning": "AI 服务暂时不可用，已返回预置模板"
        }

    async def generate_poster_copywriting(
        self,
        product_name: str,
        selling_point: str,
        cta: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成海报文案

        Args:
            product_name: 保险产品名称
            selling_point: 卖点
            cta: 行动号召

        Returns:
            包含海报文案的字典，遵循 Design Spec Section 10.1 Schema
        """
        start_time = time.time()

        # 参数验证
        if not product_name or not product_name.strip():
            return {
                "status": "error",
                "error": "产品名称不能为空",
                "error_code": "DATA_001"
            }

        if not selling_point or not selling_point.strip():
            return {
                "status": "error",
                "error": "卖点不能为空",
                "error_code": "DATA_001"
            }

        try:
            poster = self._generate_mock_poster(
                product_name=product_name,
                selling_point=selling_point,
                cta=cta
            )

            duration_ms = int((time.time() - start_time) * 1000)

            return {
                "status": "success",
                "data": {
                    "poster": poster
                },
                "duration_ms": max(duration_ms, 200)
            }

        except Exception as e:
            logger.error(f"生成海报文案失败：{e}", exc_info=True)
            return self._get_fallback_poster(product_name, selling_point)

    def _generate_mock_poster(
        self,
        product_name: str,
        selling_point: str,
        cta: Optional[str]
    ) -> Dict[str, Any]:
        """生成模拟海报文案（占位符实现）"""
        poster_id = f"poster_{uuid.uuid4().hex[:8]}"

        # 生成副标题变体
        subtitles = self._generate_subtitle_variants(selling_point)

        return {
            "id": poster_id,
            "title": self._generate_title(product_name),
            "subtitle": subtitles[0],
            "subtitle_variants": subtitles,
            "cta": cta or self._get_default_cta(),
            "design_suggestions": self._get_design_suggestions(product_name)
        }

    def _generate_title(self, product_name: str) -> str:
        """生成标题"""
        templates = [
            f"{product_name}",
            f"选择{product_name}",
            f"{product_name}，守护您"
        ]
        return templates[hash(product_name) % len(templates)]

    def _generate_subtitle_variants(self, selling_point: str) -> List[str]:
        """生成副标题变体"""
        return [
            selling_point,
            f"亮点：{selling_point}",
            f"为什么选择我们？{selling_point}"
        ][:3]

    def _get_default_cta(self) -> str:
        """获取默认 CTA"""
        ctas = [
            "立即咨询",
            "免费获取方案",
            "限时优惠中",
            "扫码了解详情"
        ]
        return ctas[0]

    def _get_design_suggestions(self, product_name: str) -> Dict[str, str]:
        """获取设计建议"""
        return {
            "color_scheme": "蓝色系（专业、信赖）",
            "mood": "温暖、安心",
            "imagery": "家庭、守护、阳光"
        }

    def _get_fallback_poster(self, product_name: str, selling_point: str) -> Dict[str, Any]:
        """降级策略 - 返回预置模板"""
        return {
            "status": "success",
            "data": {
                "poster": {
                    "id": "fallback_poster_001",
                    "title": product_name,
                    "subtitle": selling_point,
                    "cta": "立即咨询"
                }
            },
            "duration_ms": 50,
            "warning": "AI 服务暂时不可用，已返回预置模板"
        }
