"""
LLM Client Module

Provides unified interface for LLM interactions supporting multiple providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional, Type, Union

import structlog
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from core.config import settings

logger = structlog.get_logger()


# =============================================================================
# LLM Client Interface
# =============================================================================

class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    
    Provides high-level methods for common LLM operations with
    automatic retry, token tracking, and error handling.
    """
    
    def __init__(
        self,
        provider: Optional[Literal["openai", "anthropic"]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        self.provider = provider or settings.llm_provider
        self.model = model or settings.get_llm_model()
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self._llm = self._create_llm()
        logger.info(
            "LLM client initialized",
            provider=self.provider,
            model=self.model,
        )
    
    def _create_llm(self) -> BaseChatModel:
        """Create the appropriate LLM instance based on provider."""
        if self.provider == "openai":
            return ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                api_key=settings.openai_api_key,
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                api_key=settings.anthropic_api_key,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    @property
    def llm(self) -> BaseChatModel:
        """Get the underlying LangChain LLM instance."""
        return self._llm
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional variables for prompt template
        
        Returns:
            The generated text response
        """
        messages: List[BaseMessage] = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        try:
            response = await self._llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error("LLM generation failed", error=str(e))
            raise
    
    async def generate_structured(
        self,
        prompt: str,
        output_schema: Type[BaseModel],
        system_prompt: Optional[str] = None,
    ) -> BaseModel:
        """
        Generate a structured response conforming to a Pydantic schema.
        
        Args:
            prompt: The user prompt
            output_schema: Pydantic model class for the expected output
            system_prompt: Optional system prompt
        
        Returns:
            Instance of the output_schema class
        """
        # Create schema description for the prompt
        schema_json = output_schema.model_json_schema()
        
        enhanced_system = f"""
{system_prompt or "You are a helpful assistant."}

You MUST respond with valid JSON that conforms to this schema:
{schema_json}

Only respond with the JSON object, no additional text.
"""
        
        messages: List[BaseMessage] = [
            SystemMessage(content=enhanced_system),
            HumanMessage(content=prompt),
        ]
        
        try:
            response = await self._llm.ainvoke(messages)
            parser = JsonOutputParser(pydantic_object=output_schema)
            return parser.parse(response.content)
        except Exception as e:
            logger.error(
                "Structured generation failed",
                schema=output_schema.__name__,
                error=str(e),
            )
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Have a multi-turn chat conversation.
        
        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            system_prompt: Optional system prompt
        
        Returns:
            The assistant's response
        """
        chat_messages: List[BaseMessage] = []
        
        if system_prompt:
            chat_messages.append(SystemMessage(content=system_prompt))
        
        for msg in messages:
            if msg["role"] == "user":
                chat_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_messages.append(AIMessage(content=msg["content"]))
        
        try:
            response = await self._llm.ainvoke(chat_messages)
            return response.content
        except Exception as e:
            logger.error("Chat generation failed", error=str(e))
            raise
    
    def create_chain(
        self,
        prompt_template: ChatPromptTemplate,
        output_parser: Optional[Any] = None,
    ):
        """
        Create a LangChain runnable chain.
        
        Args:
            prompt_template: The prompt template to use
            output_parser: Optional output parser (defaults to StrOutputParser)
        
        Returns:
            A LangChain runnable chain
        """
        parser = output_parser or StrOutputParser()
        return prompt_template | self._llm | parser
    
    async def summarize(
        self,
        text: str,
        max_length: int = 500,
        style: str = "concise",
    ) -> str:
        """
        Summarize a piece of text.
        
        Args:
            text: The text to summarize
            max_length: Maximum length of the summary in words
            style: Summary style (concise, detailed, bullet_points)
        
        Returns:
            The summary
        """
        style_instructions = {
            "concise": "Provide a brief, focused summary highlighting only the key points.",
            "detailed": "Provide a comprehensive summary covering all important details.",
            "bullet_points": "Provide the summary as bullet points, one point per key idea.",
        }
        
        prompt = f"""
Summarize the following text in at most {max_length} words.
{style_instructions.get(style, style_instructions["concise"])}

TEXT:
{text}

SUMMARY:
"""
        return await self.generate(prompt)
    
    async def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None,
    ) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        
        Args:
            text: The text to analyze
            entity_types: Types of entities to extract (default: all)
        
        Returns:
            Dictionary mapping entity types to lists of entities
        """
        default_types = [
            "people", "organizations", "locations", "bills",
            "committees", "dates", "monetary_values"
        ]
        types_to_extract = entity_types or default_types
        
        class EntityExtraction(BaseModel):
            entities: Dict[str, List[str]]
        
        prompt = f"""
Extract the following types of entities from the text:
{', '.join(types_to_extract)}

TEXT:
{text}

Return a JSON object with entity types as keys and lists of extracted entities as values.
"""
        
        result = await self.generate_structured(
            prompt,
            EntityExtraction,
            system_prompt="You are an expert at named entity recognition.",
        )
        return result.entities
    
    async def analyze_sentiment(
        self,
        text: str,
    ) -> Dict[str, Any]:
        """
        Analyze the sentiment of text.
        
        Args:
            text: The text to analyze
        
        Returns:
            Dictionary with sentiment analysis results
        """
        class SentimentAnalysis(BaseModel):
            sentiment: Literal["positive", "negative", "neutral", "mixed"]
            score: float  # -1 to 1
            confidence: float  # 0 to 1
            key_phrases: List[str]
            summary: str
        
        prompt = f"""
Analyze the sentiment of the following text. Consider both explicit and implicit sentiment.

TEXT:
{text}

Provide:
1. Overall sentiment (positive, negative, neutral, mixed)
2. Sentiment score from -1 (very negative) to 1 (very positive)
3. Confidence score from 0 to 1
4. Key phrases that indicate the sentiment
5. Brief summary of the sentiment analysis
"""
        
        result = await self.generate_structured(
            prompt,
            SentimentAnalysis,
            system_prompt="You are an expert sentiment analyst.",
        )
        return result.model_dump()
    
    async def classify(
        self,
        text: str,
        categories: List[str],
        multi_label: bool = False,
    ) -> Dict[str, Any]:
        """
        Classify text into predefined categories.
        
        Args:
            text: The text to classify
            categories: List of possible categories
            multi_label: Whether multiple categories can apply
        
        Returns:
            Classification results with categories and confidence
        """
        class Classification(BaseModel):
            categories: List[str]
            confidences: Dict[str, float]
            reasoning: str
        
        label_type = "one or more categories" if multi_label else "the most appropriate category"
        
        prompt = f"""
Classify the following text into {label_type} from this list:
{', '.join(categories)}

TEXT:
{text}

Provide the categories that apply and confidence scores for each.
"""
        
        result = await self.generate_structured(
            prompt,
            Classification,
            system_prompt="You are a text classification expert.",
        )
        return result.model_dump()


# =============================================================================
# Factory Function
# =============================================================================

_client_instance: Optional[LLMClient] = None


def get_llm_client(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> LLMClient:
    """
    Get or create an LLM client instance.
    
    For most use cases, use the default singleton instance.
    Create new instances with custom settings only when needed.
    """
    global _client_instance
    
    # Return default instance if no custom settings
    if provider is None and model is None and not kwargs:
        if _client_instance is None:
            _client_instance = LLMClient()
        return _client_instance
    
    # Create new instance with custom settings
    return LLMClient(provider=provider, model=model, **kwargs)


# =============================================================================
# Specialized LLM Clients
# =============================================================================

class PolicyWriterLLM(LLMClient):
    """LLM client specialized for policy writing."""
    
    def __init__(self):
        super().__init__(temperature=0.3)  # Lower temp for factual content
    
    async def write_fact_sheet(
        self,
        topic: str,
        key_points: List[str],
        target_audience: str = "legislators",
    ) -> str:
        """Generate a fact sheet on a policy topic."""
        system_prompt = """
You are an expert policy writer. Create clear, authoritative fact sheets 
that are well-organized and persuasive while remaining factually accurate.
Use professional language appropriate for legislative audiences.
"""
        
        prompt = f"""
Create a comprehensive fact sheet on: {topic}

Key points to cover:
{chr(10).join(f'- {point}' for point in key_points)}

Target audience: {target_audience}

Format the fact sheet with:
- A clear, compelling title
- Executive summary (2-3 sentences)
- Key facts section with bullet points
- Benefits section
- Supporting evidence
- Call to action

Keep it to one page worth of content (400-500 words).
"""
        return await self.generate(prompt, system_prompt=system_prompt)
    
    async def write_one_pager(
        self,
        bill_title: str,
        bill_summary: str,
        talking_points: List[str],
    ) -> str:
        """Generate a legislative one-pager."""
        system_prompt = """
You are an expert at creating concise legislative one-pagers 
that lawmakers can quickly scan to understand a bill's purpose and benefits.
"""
        
        prompt = f"""
Create a one-pager for: {bill_title}

Bill Summary:
{bill_summary}

Key Talking Points:
{chr(10).join(f'- {point}' for point in talking_points)}

The one-pager should include:
- Bill title and number placeholder
- Problem statement (2-3 sentences)
- Solution/What the bill does (3-4 bullets)
- Why it matters (compelling benefits)
- Support statement (who supports this)
- Contact information placeholder

Maximum 400 words.
"""
        return await self.generate(prompt, system_prompt=system_prompt)


class CommunicationsLLM(LLMClient):
    """LLM client specialized for communications content."""
    
    def __init__(self):
        super().__init__(temperature=0.7)  # Moderate creativity
    
    async def write_press_release(
        self,
        headline: str,
        key_facts: List[str],
        quotes: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Generate a press release."""
        system_prompt = """
You are an expert PR professional. Write press releases following 
standard journalistic format: inverted pyramid structure, compelling 
lead, proper dateline, and boilerplate.
"""
        
        quotes_text = ""
        if quotes:
            quotes_text = "\nInclude these quotes:\n"
            for q in quotes:
                quotes_text += f'- "{q["text"]}" - {q["speaker"]}, {q.get("title", "")}\n'
        
        prompt = f"""
Write a professional press release with headline: {headline}

Key facts to include:
{chr(10).join(f'- {fact}' for fact in key_facts)}
{quotes_text}

Follow standard press release format:
- FOR IMMEDIATE RELEASE header
- Dateline (leave city placeholder)
- Compelling lead paragraph
- Supporting paragraphs
- Quotes from stakeholders
- Boilerplate about the organization (placeholder)
- Contact information (placeholder)
"""
        return await self.generate(prompt, system_prompt=system_prompt)
    
    async def write_op_ed(
        self,
        topic: str,
        thesis: str,
        supporting_points: List[str],
        author_perspective: str,
        word_limit: int = 750,
    ) -> str:
        """Generate an opinion editorial."""
        system_prompt = """
You are an expert opinion writer. Create compelling, well-reasoned 
op-eds that persuade through logic, evidence, and emotional resonance.
"""
        
        prompt = f"""
Write an op-ed on: {topic}

Main thesis: {thesis}

Supporting points:
{chr(10).join(f'- {point}' for point in supporting_points)}

Author perspective: {author_perspective}

The op-ed should:
- Open with a hook (compelling anecdote, startling fact, or provocative question)
- Clearly state the thesis by paragraph 2
- Build a logical argument with evidence
- Address potential counterarguments
- End with a strong call to action

Word limit: {word_limit} words
"""
        return await self.generate(prompt, system_prompt=system_prompt)


class SocialMediaLLM(LLMClient):
    """LLM client specialized for social media content."""
    
    def __init__(self):
        super().__init__(temperature=0.8)  # Higher creativity
    
    async def generate_tweets(
        self,
        topic: str,
        key_message: str,
        num_variants: int = 5,
        include_hashtags: bool = True,
    ) -> List[str]:
        """Generate tweet variants."""
        system_prompt = """
You are a social media expert. Create engaging tweets that are 
shareable, on-message, and appropriate for advocacy campaigns.
Keep tweets under 280 characters.
"""
        
        class TweetVariants(BaseModel):
            tweets: List[str]
        
        prompt = f"""
Generate {num_variants} tweet variants about: {topic}

Key message to convey: {key_message}

Requirements:
- Each tweet under 280 characters
- Vary the tone (informative, urgent, inspiring, etc.)
- {"Include relevant hashtags" if include_hashtags else "No hashtags"}
- Make them shareable and engaging
"""
        
        result = await self.generate_structured(
            prompt,
            TweetVariants,
            system_prompt=system_prompt,
        )
        return result.tweets
    
    async def generate_thread(
        self,
        topic: str,
        key_points: List[str],
        max_tweets: int = 10,
    ) -> List[str]:
        """Generate a Twitter thread."""
        system_prompt = """
You are a social media expert. Create engaging Twitter threads 
that educate while maintaining interest throughout.
"""
        
        class TwitterThread(BaseModel):
            thread: List[str]
        
        prompt = f"""
Create a Twitter thread about: {topic}

Key points to cover:
{chr(10).join(f'- {point}' for point in key_points)}

Requirements:
- Maximum {max_tweets} tweets
- Each tweet under 280 characters
- First tweet should hook the reader
- Number tweets (1/, 2/, etc.)
- End with a call to action
- Make it educational but engaging
"""
        
        result = await self.generate_structured(
            prompt,
            TwitterThread,
            system_prompt=system_prompt,
        )
        return result.thread
