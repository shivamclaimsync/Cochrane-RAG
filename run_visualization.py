"""
Run visualization analysis and save all results.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.visualization import EmbeddingAnalyzer, AnalysisReportGenerator


def main():
    print("=" * 80)
    print("WEAVIATE EMBEDDING VISUALIZATION ANALYSIS")
    print("=" * 80)
    print()
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("embedding_analysis_results") / f"run_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Results will be saved to: {output_dir}")
    print()
    
    try:
        # Initialize analyzer
        print("🔧 Initializing analyzer...")
        analyzer = EmbeddingAnalyzer(sample_size=500, random_seed=42)
        
        # Test queries for hit analysis
        test_queries = [
            "What are the effects of treatment?",
            "What is the statistical significance?",
            "What are the side effects?",
            "What is the methodology?",
            "What are the conclusions?",
            "What are the adverse effects?",
            "What is the efficacy?",
            "What are the outcomes?"
        ]
        
        # Run full analysis
        print("\n🚀 Running full analysis...")
        print("   This may take a few minutes...")
        print()
        
        full_results = analyzer.run_full_analysis(
            limit=500,
            test_queries=test_queries,
            n_clusters=10
        )
        
        print("\n✅ Analysis complete!")
        print()
        
        # Print summary
        print("=" * 80)
        print("ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Embeddings analyzed: {len(full_results['embeddings'])}")
        print(f"Clusters: {full_results['clustering_results']['n_clusters']}")
        print(f"Silhouette score: {full_results['clustering_results']['silhouette_score']:.3f}")
        print(f"Average cluster purity: {full_results['clustering_results']['average_purity']:.3f}")
        
        if full_results['query_results']:
            stats = full_results['query_results']['statistics']
            print(f"Query hits: {stats['total_unique_hits']} unique chunks")
            print(f"Avg hits per query: {stats['avg_hits_per_query']:.1f}")
        
        print(f"Figures generated: {len(full_results['figures'])}")
        print()
        
        # Save all figures as HTML
        print("💾 Saving visualizations...")
        figures_dir = output_dir / "figures"
        figures_dir.mkdir(exist_ok=True)
        
        for fig_name, fig in full_results['figures'].items():
            html_path = figures_dir / f"{fig_name}.html"
            fig.write_html(str(html_path))
            print(f"   ✓ Saved: {fig_name}.html")
        
        print()
        
        # Generate and save reports
        print("📄 Generating reports...")
        report_gen = AnalysisReportGenerator()
        
        # Text report
        report_path = output_dir / "analysis_report.txt"
        report_gen.generate_text_report(
            full_results['clustering_results'],
            full_results.get('query_results'),
            report_path
        )
        print(f"   ✓ Saved: analysis_report.txt")
        
        # JSON export
        json_path = output_dir / "analysis_results.json"
        report_gen.export_json(
            full_results['clustering_results'],
            full_results.get('query_results'),
            json_path
        )
        print(f"   ✓ Saved: analysis_results.json")
        
        # Summary statistics
        summary = report_gen.get_summary_stats(
            full_results['clustering_results'],
            full_results.get('query_results')
        )
        
        import json
        summary_path = output_dir / "summary_stats.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"   ✓ Saved: summary_stats.json")
        
        print()
        
        # Save metadata about the run
        run_info = {
            'timestamp': timestamp,
            'embeddings_analyzed': len(full_results['embeddings']),
            'n_clusters': full_results['clustering_results']['n_clusters'],
            'silhouette_score': float(full_results['clustering_results']['silhouette_score']),
            'average_purity': float(full_results['clustering_results']['average_purity']),
            'n_queries': len(test_queries),
            'figures_generated': list(full_results['figures'].keys())
        }
        
        if full_results['query_results']:
            stats = full_results['query_results']['statistics']
            run_info['query_stats'] = {
                'total_unique_hits': stats['total_unique_hits'],
                'avg_hits_per_query': stats['avg_hits_per_query']
            }
        
        info_path = output_dir / "run_info.json"
        with open(info_path, 'w') as f:
            json.dump(run_info, f, indent=2)
        print(f"   ✓ Saved: run_info.json")
        
        print()
        print("=" * 80)
        print("✅ ALL RESULTS SAVED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print(f"📂 Output directory: {output_dir}")
        print()
        print("Files created:")
        print(f"  📊 Figures: {figures_dir}/ (HTML files)")
        print(f"  📄 Reports: analysis_report.txt, analysis_results.json")
        print(f"  📈 Summary: summary_stats.json, run_info.json")
        print()
        print("To view visualizations:")
        print(f"  Open any HTML file in {figures_dir}/ in your web browser")
        print()
        
        # Clean up
        analyzer.close()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

