"""
Gradio UI for Cochrane Medical RAG System Visualization
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

import gradio as gr
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.generation.medical_rag_system import CochraneMedicalRAG


class GradioRAGInterface:
    """Gradio interface for the Cochrane Medical RAG System."""

    def __init__(self):
        """Initialize the RAG system."""
        self.rag = None
        self._initialize_rag()

    def _initialize_rag(self):
        """Initialize RAG system (lazy loading)."""
        if self.rag is None:
            self.rag = CochraneMedicalRAG(verbose=False)

    def ask_question(
        self,
        question: str,
        use_reranker: bool,
        top_k: int,
        output_format: str,
    ) -> Tuple[str, go.Figure, go.Figure, go.Figure]:
        """Ask a question and return formatted response with visualizations."""
        if not question.strip():
            empty_fig = go.Figure()
            return "Please enter a question.", empty_fig, empty_fig, empty_fig

        try:
            # Reinitialize if settings changed
            if (
                self.rag is None
                or (self.rag.chain.reranker is None) != use_reranker
                or self.rag.retriever.top_k != top_k
            ):
                if self.rag:
                    self.rag.close()
                self.rag = CochraneMedicalRAG(
                    use_reranker=use_reranker,
                    top_k=top_k,
                    verbose=False,
                )

            # Get answer - always get dict format for visualization data
            result_dict = self.rag.ask(question, format="dict")
            
            # Prepare visualization data
            viz_data = self._prepare_visualization_data(result_dict, "dict")

            # Format answer text based on user preference
            if output_format == "string":
                answer_text = self.rag._format_as_string(result_dict)
            else:
                answer_text = self._format_dict_result(result_dict)

            # Create charts
            quality_fig = self.create_quality_chart(viz_data) if viz_data else go.Figure()
            section_fig = self.create_section_chart(viz_data) if viz_data else go.Figure()
            relevance_fig = self.create_relevance_chart(viz_data) if viz_data else go.Figure()

            return answer_text, quality_fig, section_fig, relevance_fig

        except Exception as e:
            empty_fig = go.Figure()
            return f"Error: {str(e)}", empty_fig, empty_fig, empty_fig

    def search_only(
        self,
        query: str,
        quality_filter: str,
        section_filter: str,
        statistical_only: bool,
        top_k: int,
    ) -> Tuple[str, go.Figure, go.Figure]:
        """Search only mode without LLM generation."""
        if not query.strip():
            empty_fig = go.Figure()
            return "Please enter a search query.", empty_fig, empty_fig

        try:
            self._initialize_rag()

            # Build filters
            filters = {}
            if quality_filter and quality_filter != "Any":
                filters["quality_grade"] = quality_filter
            if section_filter and section_filter != "Any":
                filters["section"] = section_filter
            if statistical_only:
                filters["statistical_only"] = True

            # Perform search
            results = self.rag.search(query, filters=filters, top_k=top_k)

            # Format results
            formatted_results = self._format_search_results(results)

            # Prepare visualization
            viz_data = self._prepare_search_visualization(results)

            # Create charts
            quality_fig = self.create_quality_chart(viz_data) if viz_data else go.Figure()
            section_fig = self.create_section_chart(viz_data) if viz_data else go.Figure()

            return formatted_results, quality_fig, section_fig

        except Exception as e:
            empty_fig = go.Figure()
            return f"Error: {str(e)}", empty_fig, empty_fig

    def get_system_stats(self) -> Tuple[str, go.Figure]:
        """Get and display system statistics."""
        try:
            self._initialize_rag()
            stats = self.rag.get_stats()

            # Format stats text
            stats_text = f"""
# System Statistics

## Database Overview
- **Total Chunks**: {stats['total_chunks']:,}
- **Total Documents**: {stats['total_documents']:,}
- **Model**: {stats['model']}
- **Reranker**: {'Enabled' if stats['reranker_enabled'] else 'Disabled'}

## Chunks by Level
"""
            if stats.get("chunks_by_level"):
                for level, count in stats["chunks_by_level"].items():
                    stats_text += f"- **{level}**: {count:,}\n"

            # Prepare visualization and create chart
            viz_data = self._prepare_stats_visualization(stats)
            stats_fig = self.create_stats_chart(viz_data) if viz_data else go.Figure()

            return stats_text, stats_fig

        except Exception as e:
            empty_fig = go.Figure()
            return f"Error: {str(e)}", empty_fig

    def _prepare_visualization_data(self, result: Dict, output_format: str) -> Dict:
        """Prepare data for visualization from RAG result."""
        if output_format == "string":
            # For string format, we don't have structured data
            return None

        # Extract data for visualizations
        sources = result.get("sources", [])

        # Quality grade distribution
        quality_grades = {}
        for source in sources:
            grade = source.get("quality_grade", "") or "Unknown"
            quality_grades[grade] = quality_grades.get(grade, 0) + 1

        # Section distribution
        sections = {}
        for source in sources:
            section = source.get("section", "") or "Unknown"
            sections[section] = sections.get(section, 0) + 1

        # Statistical content
        has_statistical = sum(
            1 for source in sources if source.get("is_statistical", False)
        )

        # Relevance scores (if available)
        relevance_scores = [
            source.get("relevance_score", 0) for source in sources if "relevance_score" in source
        ]

        return {
            "quality_grades": quality_grades,
            "sections": sections,
            "has_statistical": has_statistical,
            "total_sources": len(sources),
            "relevance_scores": relevance_scores,
            "sources": sources,
        }

    def _prepare_search_visualization(self, results: List[Dict]) -> Dict:
        """Prepare visualization data for search results."""
        if not results:
            return None

        # Quality distribution
        quality_grades = {}
        for result in results:
            grade = result.get("quality_grade", "Unknown") or "Unknown"
            quality_grades[grade] = quality_grades.get(grade, 0) + 1

        # Section distribution
        sections = {}
        for result in results:
            section = result.get("section", "Unknown") or "Unknown"
            sections[section] = sections.get(section, 0) + 1

        # Statistical content
        has_statistical = sum(1 for result in results if result.get("is_statistical", False))

        # Relevance scores
        relevance_scores = [
            result.get("relevance_score", 0)
            for result in results
            if "relevance_score" in result
        ]

        return {
            "quality_grades": quality_grades,
            "sections": sections,
            "has_statistical": has_statistical,
            "total_results": len(results),
            "relevance_scores": relevance_scores,
            "results": results,
        }

    def _prepare_stats_visualization(self, stats: Dict) -> Dict:
        """Prepare visualization data for system statistics."""
        chunks_by_level = stats.get("chunks_by_level", {})

        return {
            "chunks_by_level": chunks_by_level,
            "total_chunks": stats.get("total_chunks", 0),
            "total_documents": stats.get("total_documents", 0),
        }

    def _format_dict_result(self, result: Dict) -> str:
        """Format dictionary result as readable text."""
        lines = []
        lines.append("=" * 80)
        lines.append("EVIDENCE-BASED ANSWER")
        lines.append("=" * 80)
        lines.append(f"\n{result.get('answer', 'No answer generated')}\n")
        lines.append("-" * 80)
        lines.append("METADATA")
        lines.append("-" * 80)
        lines.append(f"Quality Summary: {result.get('quality_summary', 'N/A')}")
        lines.append(f"Statistical Summary: {result.get('statistical_summary', 'N/A')}")
        lines.append(f"Sources Used: {result.get('num_sources', 0)}")
        lines.append("\n" + "-" * 80)
        lines.append("SOURCES")
        lines.append("-" * 80)

        for source in result.get("sources", [])[:10]:  # Show top 10
            idx = source.get("index", "?")
            title = source.get("title", "Unknown")
            url = source.get("url", "")
            section = source.get("section", "")
            quality = source.get("quality_grade", "")
            lines.append(f"\n[{idx}] {title}")
            if section:
                lines.append(f"    Section: {section}")
            if quality:
                lines.append(f"    Quality: Grade {quality}")
            if url:
                lines.append(f"    URL: {url}")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)

    def _format_search_results(self, results: List[Dict]) -> str:
        """Format search results as readable text."""
        if not results:
            return "No results found."

        lines = []
        lines.append(f"# Search Results ({len(results)} found)\n")

        for idx, result in enumerate(results, 1):
            lines.append(f"## [{idx}] {result.get('title', 'No title')}")
            if result.get("topic"):
                lines.append(f"**Topic**: {result['topic']}")
            if result.get("quality_grade"):
                lines.append(f"**Quality**: Grade {result['quality_grade']}")
            if result.get("section"):
                lines.append(f"**Section**: {result['section']}")
            if result.get("is_statistical"):
                lines.append("**Contains Statistical Data**: Yes")
            if result.get("relevance_score"):
                lines.append(f"**Relevance Score**: {result['relevance_score']:.3f}")
            if result.get("url"):
                lines.append(f"**URL**: {result['url']}")
            lines.append(f"\n**Content**:\n{result.get('content', '')[:500]}...")
            lines.append("\n" + "-" * 80 + "\n")

        return "\n".join(lines)

    def create_quality_chart(self, viz_data: Dict) -> go.Figure:
        """Create quality grade distribution chart."""
        if not viz_data or "quality_grades" not in viz_data:
            return go.Figure()

        quality_grades = viz_data["quality_grades"]
        if not quality_grades:
            return go.Figure()

        grades = list(quality_grades.keys())
        counts = list(quality_grades.values())

        fig = px.bar(
            x=grades,
            y=counts,
            title="Quality Grade Distribution",
            labels={"x": "Quality Grade", "y": "Number of Sources"},
            color=grades,
            color_discrete_map={
                "A": "#2ecc71",
                "B": "#3498db",
                "C": "#f39c12",
                "D": "#e74c3c",
                "Unknown": "#95a5a6",
            },
        )
        fig.update_layout(showlegend=False, height=300)
        return fig

    def create_section_chart(self, viz_data: Dict) -> go.Figure:
        """Create section distribution chart."""
        if not viz_data or "sections" not in viz_data:
            return go.Figure()

        sections = viz_data["sections"]
        if not sections:
            return go.Figure()

        # Limit to top 10 sections
        sorted_sections = sorted(sections.items(), key=lambda x: x[1], reverse=True)[:10]
        section_names = [s[0] for s in sorted_sections]
        counts = [s[1] for s in sorted_sections]

        fig = px.pie(
            values=counts,
            names=section_names,
            title="Section Distribution",
            height=300,
        )
        return fig

    def create_relevance_chart(self, viz_data: Dict) -> go.Figure:
        """Create relevance score chart."""
        if not viz_data or "relevance_scores" not in viz_data:
            return go.Figure()

        relevance_scores = viz_data["relevance_scores"]
        if not relevance_scores:
            return go.Figure()

        fig = px.bar(
            x=list(range(1, len(relevance_scores) + 1)),
            y=relevance_scores,
            title="Relevance Scores",
            labels={"x": "Source Rank", "y": "Relevance Score"},
            height=300,
        )
        fig.update_traces(marker_color="#3498db")
        return fig

    def create_stats_chart(self, viz_data: Dict) -> go.Figure:
        """Create system statistics chart."""
        if not viz_data or "chunks_by_level" not in viz_data:
            return go.Figure()

        chunks_by_level = viz_data["chunks_by_level"]
        if not chunks_by_level:
            return go.Figure()

        levels = list(chunks_by_level.keys())
        counts = list(chunks_by_level.values())

        fig = px.bar(
            x=levels,
            y=counts,
            title="Chunks by Hierarchical Level",
            labels={"x": "Level", "y": "Number of Chunks"},
            color=levels,
            height=300,
        )
        fig.update_layout(showlegend=False)
        return fig

    def cleanup(self):
        """Cleanup resources."""
        if self.rag:
            self.rag.close()


def create_interface():
    """Create the Gradio interface."""
    interface = GradioRAGInterface()

    with gr.Blocks(title="Cochrane Medical RAG System", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🏥 Cochrane Medical RAG System
            
            Evidence-based medical question answering using Cochrane systematic reviews.
            
            This interface allows you to:
            - Ask medical questions and get evidence-based answers
            - Search the knowledge base
            - Visualize system statistics and results
            """
        )

        with gr.Tabs():
            # Tab 1: Ask Questions
            with gr.Tab("Ask Questions"):
                with gr.Row():
                    with gr.Column(scale=2):
                        question_input = gr.Textbox(
                            label="Medical Question",
                            placeholder="Enter your medical question here...",
                            lines=3,
                        )
                        with gr.Row():
                            use_reranker = gr.Checkbox(
                                label="Use Re-ranker", value=True
                            )
                            top_k_slider = gr.Slider(
                                minimum=5,
                                maximum=20,
                                value=10,
                                step=1,
                                label="Number of Sources (Top K)",
                            )
                            output_format = gr.Radio(
                                choices=["string", "dict"],
                                value="string",
                                label="Output Format",
                            )
                        ask_btn = gr.Button("Ask Question", variant="primary")

                    with gr.Column(scale=1):
                        gr.Markdown("### Settings")
                        gr.Markdown(
                            """
                            **Re-ranker**: Improves relevance by re-scoring results
                            
                            **Top K**: Number of documents to retrieve
                            
                            **Output Format**: 
                            - String: Human-readable format
                            - Dict: Structured format with metadata
                            """
                        )

                answer_output = gr.Textbox(
                    label="Answer",
                    lines=15,
                    max_lines=25,
                )

                with gr.Row():
                    quality_chart = gr.Plot(label="Quality Distribution")
                    section_chart = gr.Plot(label="Section Distribution")
                    relevance_chart = gr.Plot(label="Relevance Scores")

                ask_btn.click(
                    fn=interface.ask_question,
                    inputs=[question_input, use_reranker, top_k_slider, output_format],
                    outputs=[answer_output, quality_chart, section_chart, relevance_chart],
                )

            # Tab 2: Search Only
            with gr.Tab("Search"):
                with gr.Row():
                    with gr.Column(scale=2):
                        search_query = gr.Textbox(
                            label="Search Query",
                            placeholder="Enter search terms...",
                            lines=2,
                        )
                        with gr.Row():
                            quality_filter = gr.Dropdown(
                                choices=["Any", "A", "B", "C", "D"],
                                value="Any",
                                label="Quality Filter",
                            )
                            section_filter = gr.Dropdown(
                                choices=[
                                    "Any",
                                    "abstract",
                                    "background",
                                    "results",
                                    "authors_conclusions",
                                    "plain_language_summary",
                                ],
                                value="Any",
                                label="Section Filter",
                            )
                            statistical_only = gr.Checkbox(
                                label="Statistical Content Only", value=False
                            )
                            search_top_k = gr.Slider(
                                minimum=3,
                                maximum=20,
                                value=10,
                                step=1,
                                label="Number of Results",
                            )
                        search_btn = gr.Button("Search", variant="primary")

                search_output = gr.Textbox(
                    label="Search Results",
                    lines=15,
                    max_lines=25,
                )

                with gr.Row():
                    search_quality_chart = gr.Plot(label="Quality Distribution")
                    search_section_chart = gr.Plot(label="Section Distribution")

                search_btn.click(
                    fn=interface.search_only,
                    inputs=[
                        search_query,
                        quality_filter,
                        section_filter,
                        statistical_only,
                        search_top_k,
                    ],
                    outputs=[search_output, search_quality_chart, search_section_chart],
                )

            # Tab 3: Statistics
            with gr.Tab("System Statistics"):
                stats_btn = gr.Button("Load Statistics", variant="primary")
                stats_output = gr.Markdown()

                stats_chart = gr.Plot(label="Chunks by Level")

                stats_btn.click(
                    fn=interface.get_system_stats,
                    outputs=[stats_output, stats_chart],
                )

    return demo


def main():
    """Launch the Gradio interface."""
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    main()

