"""
Medical prompt templates for evidence-based question answering.
"""

from typing import List

from langchain_core.documents import Document


class MedicalPromptBuilder:
    """Build prompts for medical RAG generation."""

    SYSTEM_INSTRUCTIONS = """You are a medical information assistant providing evidence-based answers from Cochrane systematic reviews.

Guidelines:
- Base responses ONLY on the provided evidence
- Cite sources by [1], [2], etc. at the end of relevant sentences
- Do NOT include URLs in your response - they will be added automatically
- Indicate quality of evidence when relevant
- Mention statistical significance when data is available
- Acknowledge limitations and uncertainties
- Do not make claims beyond the provided evidence

Format your response naturally with inline citations like:
Based on current evidence, vitamin C shows little effectiveness[1]. However, some studies suggest modest benefits[2].

The system will automatically append the URL list below your response."""

    @classmethod
    def build_qa_prompt(
        cls,
        question: str,
        context: str,
        quality_summary: str,
        statistical_summary: str,
    ) -> str:
        """
        Build complete medical QA prompt.

        Args:
            question: User's medical question
            context: Formatted retrieved documents
            quality_summary: Quality grade distribution
            statistical_summary: Statistical data indicator

        Returns:
            Complete prompt string
        """
        prompt = f"""{cls.SYSTEM_INSTRUCTIONS}

{context}

Quality of Sources: {quality_summary}
Statistical Evidence: {statistical_summary}

Question: {question}

Provide an evidence-based answer following the guidelines above."""

        return prompt

    @classmethod
    def format_context(cls, documents: List[Document]) -> str:
        """
        Format retrieved documents into context.

        Args:
            documents: List of LangChain Document objects

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            title = metadata.get("title", "Unknown")
            section = metadata.get("section_name", "")
            quality = metadata.get("quality_grade", "")

            context_parts.append(f"[{i}] {title}")
            if quality:
                context_parts.append(f"Quality: Grade {quality}")
            if section:
                context_parts.append(f"Section: {section}")
            context_parts.append(f"\n{doc.page_content}\n---\n")

        return "\n".join(context_parts)

    @classmethod
    def generate_quality_summary(cls, documents: List[Document]) -> str:
        """
        Generate quality grade distribution summary.

        Args:
            documents: List of retrieved documents

        Returns:
            Quality summary string
        """
        if not documents:
            return "No sources available"

        quality_counts = {"A": 0, "B": 0, "C": 0, "Unknown": 0}
        for doc in documents:
            quality = doc.metadata.get("quality_grade", "").upper()
            if quality in quality_counts:
                quality_counts[quality] += 1
            else:
                quality_counts["Unknown"] += 1

        parts = []
        for grade in ["A", "B", "C"]:
            if quality_counts[grade] > 0:
                parts.append(f"Grade {grade}: {quality_counts[grade]}")

        if quality_counts["Unknown"] > 0:
            parts.append(f"Unknown: {quality_counts['Unknown']}")

        return "; ".join(parts) if parts else "No quality grades available"

    @classmethod
    def generate_statistical_summary(cls, documents: List[Document]) -> str:
        """
        Generate statistical data availability summary.

        Args:
            documents: List of retrieved documents

        Returns:
            Statistical summary string
        """
        if not documents:
            return "No sources available"

        statistical_count = sum(
            1 for doc in documents if doc.metadata.get("is_statistical", False)
        )

        total = len(documents)
        if statistical_count == 0:
            return "No statistical data available"
        elif statistical_count == total:
            return f"All {total} sources contain statistical data"
        else:
            return f"{statistical_count} of {total} sources contain statistical data"

