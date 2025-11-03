"""
Query decomposition for medical RAG system using LLM-based analysis.

Breaks down complex medical queries into focused sub-queries targeting specific aspects
such as effectiveness, safety, comparison, methodology, or statistical evidence.
"""

import os
import json
from typing import List, Optional
from dataclasses import dataclass
from openai import OpenAI

from src.retrieving.reranker import MedicalReranker


@dataclass
class SubQuery:
    """Individual sub-query with metadata."""

    text: str
    intent: str  # "effectiveness", "safety", "comparison", "methodology", "statistical", "general"
    priority: int  # 1=high, 2=medium, 3=low
    statistical_only: bool = False
    section_hint: Optional[str] = None  # "results", "methods", "authors_conclusions", etc.


class MedicalQueryDecomposer:
    """
    Decompose complex medical queries into focused sub-queries using LLM.

    Uses OpenAI GPT models to intelligently break down queries into 2-4 focused sub-queries,
    with fallback keyword-based detection for simpler analysis.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.3,
        enable_llm: bool = True,
    ):
        """
        Initialize query decomposer.

        Args:
            model_name: OpenAI model identifier (default: gpt-4-turbo-preview)
            temperature: Sampling temperature for decomposition
            enable_llm: Whether to use LLM-based decomposition
        """
        self.enable_llm = enable_llm

        if enable_llm:
            self.model_name = model_name or os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
            self.temperature = temperature

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment for query decomposition")

            self.client = OpenAI(api_key=api_key)

        # Use existing reranker for intent detection fallback
        self.intent_detector = MedicalReranker()

    def should_decompose(self, query: str) -> bool:
        """
        Detect if query is complex enough to benefit from decomposition.

        Args:
            query: User query

        Returns:
            True if query should be decomposed
        """
        # Check for multiple intents using keyword-based detection
        intents = self._detect_multiple_intents(query)

        # Decompose if multiple distinct intents detected
        if len(intents) >= 2:
            return True

        # Decompose if query contains "and" connecting different aspects
        query_lower = query.lower()
        if " and " in query_lower:
            # Check if "and" is connecting different medical aspects
            if any(keyword in query_lower for keyword in ["effective", "safe", "compare"]):
                return True

        # Decompose for comparison queries
        if "compare" in query_lower or "versus" in query_lower or " vs " in query_lower:
            return True

        # Decompose if query asks about multiple outcomes
        if any(phrase in query_lower for phrase in ["both", "as well as", "along with"]):
            return True

        # Simple queries don't need decomposition
        return False

    def decompose(self, query: str) -> List[SubQuery]:
        """
        Decompose query into focused sub-queries.

        Args:
            query: User query

        Returns:
            List of SubQuery objects
        """
        # Check if decomposition is needed
        if not self.should_decompose(query):
            # Simple query, return as single sub-query
            intent = self.intent_detector._detect_query_intent(query)
            statistical_only = self.intent_detector._is_statistical_query(query)
            section_hint = self._get_section_hint(intent)

            return [
                SubQuery(
                    text=query,
                    intent=intent,
                    priority=1,
                    statistical_only=statistical_only,
                    section_hint=section_hint,
                )
            ]

        # Complex query - use LLM decomposition if enabled
        if self.enable_llm:
            try:
                sub_queries = self._llm_decompose(query)
                if sub_queries:
                    return sub_queries
                print("⚠️ LLM decomposition failed, falling back to keyword-based")
            except Exception as e:
                print(f"⚠️ LLM decomposition error: {e}, falling back to keyword-based")

        # Fallback: keyword-based decomposition
        return self._keyword_based_decompose(query)

    def _llm_decompose(self, query: str) -> List[SubQuery]:
        """
        Use LLM to decompose query into focused sub-queries.

        Args:
            query: User query

        Returns:
            List of SubQuery objects
        """
        system_prompt = """You are a medical query analyzer. Break down complex medical queries into 2-4 focused sub-queries.
Each sub-query should target a specific aspect: effectiveness, safety, comparison, methodology, or statistical evidence.
Keep each sub-query concise and focused on one aspect.

Output ONLY valid JSON array in this exact format (no markdown, no extra text):
[
  {"text": "First sub-query text", "intent": "effectiveness"},
  {"text": "Second sub-query text", "intent": "safety"}
]

Valid intents: effectiveness, safety, comparison, methodology, statistical, general"""

        user_prompt = f"Query: {query}\n\nGenerate 2-4 focused sub-queries as JSON array:"

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            # Parse JSON response
            content = response.choices[0].message.content.strip()
            data = json.loads(content)

            # Handle different possible response formats
            if "subqueries" in data:
                subqueries_data = data["subqueries"]
            elif isinstance(data, list):
                subqueries_data = data
            else:
                # Try to find any list in the response
                subqueries_data = next((v for v in data.values() if isinstance(v, list)), [])

            # Convert to SubQuery objects
            sub_queries = []
            for sq_data in subqueries_data:
                intent = sq_data.get("intent", "general")
                sub_queries.append(
                    SubQuery(
                        text=sq_data["text"],
                        intent=intent,
                        priority=1,
                        statistical_only=self.intent_detector._is_statistical_query(
                            sq_data["text"]
                        ),
                        section_hint=self._get_section_hint(intent),
                    )
                )

            return sub_queries if sub_queries else None

        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse LLM response as JSON: {e}")
            return None
        except Exception as e:
            print(f"⚠️ LLM decomposition error: {e}")
            return None

    def _keyword_based_decompose(self, query: str) -> List[SubQuery]:
        """
        Fallback decomposition using keyword-based detection.

        Args:
            query: User query

        Returns:
            List of SubQuery objects
        """
        intents = self._detect_multiple_intents(query)
        sub_queries = []

        query_lower = query.lower()

        # Generate sub-queries for each detected intent
        if "effectiveness" in intents:
            # Rewrite query focusing on effectiveness
            effectiveness_text = self._focus_query(query, "effectiveness")
            sub_queries.append(
                SubQuery(
                    text=effectiveness_text,
                    intent="effectiveness",
                    priority=1,
                    section_hint="results",
                )
            )

        if "safety" in intents:
            # Rewrite query focusing on safety
            safety_text = self._focus_query(query, "safety")
            sub_queries.append(
                SubQuery(
                    text=safety_text,
                    intent="safety",
                    priority=1,
                    section_hint="results",
                )
            )

        if "comparison" in intents:
            # Keep comparison query as-is or enhance it
            comparison_text = query  # Can be enhanced later
            sub_queries.append(
                SubQuery(
                    text=comparison_text,
                    intent="comparison",
                    priority=1,
                    section_hint="results",
                )
            )

        if "methodology" in intents:
            sub_queries.append(
                SubQuery(
                    text=self._focus_query(query, "methodology"),
                    intent="methodology",
                    priority=1,
                    section_hint="methods",
                )
            )

        if "statistical" in intents:
            sub_queries.append(
                SubQuery(
                    text=self._focus_query(query, "statistical"),
                    intent="statistical",
                    priority=1,
                    statistical_only=True,
                    section_hint="results",
                )
            )

        # If no specific intents found, return original query
        if not sub_queries:
            intent = self.intent_detector._detect_query_intent(query)
            sub_queries.append(
                SubQuery(
                    text=query,
                    intent=intent,
                    priority=1,
                    section_hint=self._get_section_hint(intent),
                )
            )

        return sub_queries

    def _detect_multiple_intents(self, query: str) -> List[str]:
        """
        Detect all query intents present using keyword matching.

        Args:
            query: User query

        Returns:
            List of detected intent types
        """
        intents = []
        query_lower = query.lower()

        # Effectiveness keywords
        if any(
            keyword in query_lower
            for keyword in ["effective", "efficacy", "benefit", "improve", "work", "help"]
        ):
            intents.append("effectiveness")

        # Safety keywords
        if any(
            keyword in query_lower
            for keyword in ["safe", "safety", "adverse", "side effect", "harm", "risk", "toxic"]
        ):
            intents.append("safety")

        # Comparison keywords
        if any(
            keyword in query_lower
            for keyword in ["compare", "versus", "vs ", "better than", "superior to"]
        ):
            intents.append("comparison")

        # Methodology keywords
        if any(
            keyword in query_lower
            for keyword in ["method", "methodology", "design", "study design", "how study"]
        ):
            intents.append("methodology")

        # Statistical keywords
        if any(
            keyword in query_lower
            for keyword in [
                "statistical",
                "statistically",
                "p-value",
                "confidence interval",
                "evidence",
                "odds ratio",
                "risk ratio",
            ]
        ):
            intents.append("statistical")

        return intents if intents else ["general"]

    def _focus_query(self, query: str, target_intent: str) -> str:
        """
        Rewrite query to focus on specific intent.

        Args:
            query: Original query
            target_intent: Target intent to focus on

        Returns:
            Rewritten query
        """
        # Simple keyword-based rewriting
        query_lower = query.lower()

        if target_intent == "effectiveness":
            if "effective" in query_lower or "efficacy" in query_lower:
                return self._extract_around_keyword(query, ["effective", "efficacy"])
            return f"Effectiveness of {query}"

        elif target_intent == "safety":
            if "safe" in query_lower or "adverse" in query_lower:
                return self._extract_around_keyword(query, ["safe", "adverse", "side effect"])
            return f"Safety and adverse effects of {query}"

        elif target_intent == "methodology":
            if "method" in query_lower:
                return self._extract_around_keyword(query, ["method", "methodology", "design"])
            return f"Methodology for {query}"

        elif target_intent == "statistical":
            if any(kw in query_lower for kw in ["statistical", "evidence"]):
                return self._extract_around_keyword(query, ["statistical", "evidence"])
            return f"Statistical evidence for {query}"

        return query

    def _extract_around_keyword(self, query: str, keywords: List[str]) -> str:
        """
        Extract relevant phrase around a keyword.

        Args:
            query: Full query
            keywords: Keywords to search for

        Returns:
            Extracted phrase
        """
        words = query.split()
        for i, word in enumerate(words):
            if any(kw.lower() in word.lower() for kw in keywords):
                # Take 15 words around keyword
                start = max(0, i - 7)
                end = min(len(words), i + 8)
                return " ".join(words[start:end])
        return query

    def _get_section_hint(self, intent: str) -> Optional[str]:
        """
        Get suggested section for an intent.

        Args:
            intent: Query intent

        Returns:
            Section name hint
        """
        intent_to_section = {
            "effectiveness": "results",
            "safety": "results",
            "comparison": "results",
            "methodology": "methods",
            "statistical": "results",
            "conclusion": "authors_conclusions",
            "background": "background",
            "general": None,
        }
        return intent_to_section.get(intent)

