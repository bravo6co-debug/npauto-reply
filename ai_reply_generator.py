"""
AI 기반 답글 생성 엔진
감정 분석 결과를 기반으로 맥락에 맞는 고품질 답글 생성
"""

from typing import Dict
from openai import OpenAI
import random


class AIReplyGenerator:
    """답글 생성 엔진"""

    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)

    def generate_reply(
        self,
        review_content: str,
        analysis_result: Dict = None,
        brand_context: str = "카페"
    ) -> Dict:
        """답글 생성"""

        # analysis_result가 없으면 간단한 분석 수행
        if analysis_result is None:
            analysis_result = self._simple_sentiment_analysis(review_content)

        # 감정별 시스템 프롬프트
        system_prompt = self._get_system_prompt(analysis_result["sentiment"])

        # 고도화 프롬프트 구성
        user_prompt = self._build_user_prompt(
            review_content,
            analysis_result,
            brand_context
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=250,
                presence_penalty=0.4,
                frequency_penalty=0.3
            )

            generated_reply = response.choices[0].message.content.strip()

            # 답글 검증
            validated_reply = self._validate_and_adjust_reply(
                generated_reply,
                analysis_result
            )

            return {
                "success": True,
                "reply": validated_reply,
                "model_used": "gpt-4o-mini",
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }

        except Exception as e:
            print(f"답글 생성 실패: {e}")
            # 템플릿 폴백
            fallback_reply = self._generate_template_reply(
                analysis_result["sentiment"],
                analysis_result.get("topics", []),
                analysis_result.get("keywords", [])
            )
            return {
                "success": True,
                "reply": fallback_reply,
                "model_used": "template",
                "tokens_used": 0
            }

    def _simple_sentiment_analysis(self, review_content: str) -> Dict:
        """간단한 감정 분석 (OpenAI API 없이 사용할 경우)"""

        # 긍정 키워드
        positive_keywords = ["좋", "맛있", "친절", "깨끗", "최고", "추천", "만족", "감사", "훌륭", "완벽"]
        # 부정 키워드
        negative_keywords = ["별로", "실망", "불친절", "맛없", "더럽", "최악", "불만", "화", "짜증", "후회"]

        positive_count = sum(1 for keyword in positive_keywords if keyword in review_content)
        negative_count = sum(1 for keyword in negative_keywords if keyword in review_content)

        if positive_count > negative_count:
            sentiment = "positive"
            strength = min(0.5 + (positive_count * 0.1), 1.0)
        elif negative_count > positive_count:
            sentiment = "negative"
            strength = min(0.5 + (negative_count * 0.1), 1.0)
        else:
            sentiment = "neutral"
            strength = 0.5

        return {
            "sentiment": sentiment,
            "sentiment_strength": strength,
            "topics": [],
            "keywords": [],
            "intent": "일반",
            "reply_focus": [],
            "reply_avoid": []
        }

    def _get_system_prompt(self, sentiment: str) -> str:
        """감정별 시스템 프롬프트"""
        prompts = {
            "positive": """당신은 한국 프랜차이즈 매장의 전문적이고 진심어린 고객 서비스 담당자입니다.

고객의 긍정적인 리뷰에 감사하며, 진정성 있고 따뜻한 답글을 작성합니다.
형식적이지 않고 고객이 언급한 구체적인 내용을 인용하여 답변합니다.

답글 작성 원칙:
- 고객이 언급한 구체적인 내용(맛, 서비스, 분위기 등)을 인용
- 80-120자 내외로 간결하게
- 따뜻하고 진정성 있는 톤
- 자연스러운 이모지 1-2개 사용
- 형식적인 문구 지양""",

            "negative": """당신은 한국 프랜차이즈 매장의 전문적이고 진심어린 고객 서비스 담당자입니다.

고객의 불만에 진심으로 공감하고 사과하며, 구체적인 개선 방안을 제시합니다.
변명하거나 책임을 회피하지 않고, 문제를 정확히 이해했음을 보여줍니다.

답글 작성 원칙:
- 진심 어린 사과로 시작
- 고객이 지적한 구체적인 문제점 언급
- 명확한 개선 약속 또는 보상 제안
- 80-120자 내외로 간결하게
- 진지하고 책임감 있는 톤
- 변명이나 책임 회피 금지""",

            "neutral": """당신은 한국 프랜차이즈 매장의 전문적이고 진심어린 고객 서비스 담당자입니다.

고객의 방문과 피드백에 감사하며, 더 나은 경험을 제공하겠다는 의지를 전달합니다.

답글 작성 원칙:
- 방문 감사 표현
- 고객의 피드백을 진지하게 받아들임을 표현
- 개선 의지 전달
- 80-120자 내외로 간결하게
- 정중하고 따뜻한 톤
- 자연스러운 이모지 1개 사용"""
        }

        return prompts.get(sentiment, prompts["neutral"])

    def _build_user_prompt(
        self,
        review_content: str,
        analysis_result: Dict,
        brand_context: str
    ) -> str:
        """고도화 프롬프트 구성"""

        sentiment = analysis_result["sentiment"]
        topics = ", ".join(analysis_result.get("topics", []))
        keywords = ", ".join(analysis_result.get("keywords", []))
        intent = analysis_result.get("intent", "일반")
        reply_focus = analysis_result.get("reply_focus", [])
        reply_avoid = analysis_result.get("reply_avoid", [])

        prompt = f"""[고객 리뷰 분석 결과]
감정: {sentiment} (강도: {int(analysis_result.get('sentiment_strength', 0.5) * 100)}%)
고객 의도: {intent}
주요 주제: {topics}
핵심 키워드: {keywords}

[리뷰 내용]
"{review_content}"

[매장 정보]
- 매장명/유형: {brand_context}

[답글 작성 가이드라인]
강조할 포인트:
{chr(10).join(f"- {point}" for point in reply_focus) if reply_focus else "- 고객의 피드백에 진심으로 감사"}

피해야 할 요소:
{chr(10).join(f"- {avoid}" for avoid in reply_avoid) if reply_avoid else "- 형식적인 답변"}

[구체적 요구사항]
1. 고객이 언급한 구체적인 키워드를 반드시 1-2개 포함
2. 80-120자 길이 (공백 포함)
3. 자연스러운 한국어 구어체
4. 이모지는 최소한으로 (1-2개)
5. 문장은 2-3개로 구성

답글만 작성하세요 (부가 설명 없이):"""

        return prompt

    def _validate_and_adjust_reply(
        self,
        reply: str,
        analysis_result: Dict
    ) -> str:
        """답글 검증 및 후처리"""

        # 따옴표 제거
        reply = reply.strip('"\'')

        # 길이 체크
        if len(reply) < 40:
            # 너무 짧으면 템플릿으로 대체
            return self._generate_template_reply(
                analysis_result["sentiment"],
                analysis_result.get("topics", []),
                analysis_result.get("keywords", [])
            )

        # 길이가 너무 길면 잘라내기
        if len(reply) > 150:
            sentences = reply.split('.')
            reply = '. '.join(sentences[:2]) + '.'
            if len(reply) > 150:
                reply = reply[:147] + '...'

        return reply

    def _generate_template_reply(
        self,
        sentiment: str,
        topics: list,
        keywords: list
    ) -> str:
        """템플릿 기반 폴백 답글"""

        templates = {
            "positive": [
                f"좋게 봐주셔서 감사합니다 😊 {keywords[0] if keywords else '방문'}해 주셔서 정말 기쁩니다. 앞으로도 더 좋은 모습으로 찾아뵙겠습니다!",
                f"{keywords[0] if keywords else '서비스'} 만족스러우셨다니 기쁩니다! 항상 최선을 다하는 저희 매장이 되겠습니다. 다음에 또 뵙겠습니다 😊"
            ],
            "negative": [
                f"불편을 드려 정말 죄송합니다. {topics[0] if topics else '서비스'} 관련하여 즉시 개선하겠습니다. 더 나은 모습으로 다시 찾아뵙고 싶습니다.",
                f"소중한 의견 감사합니다. 말씀하신 {keywords[0] if keywords else '부분'}은 빠르게 개선하도록 하겠습니다. 다시 한번 사과드립니다."
            ],
            "neutral": [
                "방문해 주셔서 감사합니다 😊 소중한 의견 잘 참고하여 더 나은 서비스로 보답하겠습니다!",
                "피드백 감사드립니다. 고객님의 의견을 바탕으로 지속적으로 개선해 나가겠습니다!"
            ]
        }

        template_list = templates.get(sentiment, templates["neutral"])
        return random.choice(template_list)


# 간단한 사용 예제
if __name__ == "__main__":
    # OpenAI API 키 설정 필요
    import os

    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

    if api_key == "your-api-key-here":
        print("경고: OPENAI_API_KEY 환경 변수를 설정하거나 코드에서 직접 입력하세요.")
        print("템플릿 기반 답글만 생성됩니다.\n")

    generator = AIReplyGenerator(api_key)

    # 테스트 리뷰
    test_reviews = [
        "음식이 정말 맛있었어요! 직원분들도 친절하시고 분위기도 좋았습니다.",
        "음식이 너무 짜고 서비스가 별로였어요. 실망스러웠습니다.",
        "그냥 평범했어요. 나쁘지는 않았습니다."
    ]

    for i, review in enumerate(test_reviews, 1):
        print(f"[테스트 {i}]")
        print(f"리뷰: {review}")

        result = generator.generate_reply(
            review_content=review,
            brand_context="카페"
        )

        print(f"답글: {result['reply']}")
        print(f"모델: {result['model_used']}")
        print(f"토큰: {result['tokens_used']}")
        print("-" * 80)
