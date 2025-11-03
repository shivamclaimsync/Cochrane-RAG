#!/usr/bin/env python3
"""
Utility script to load and use test questions for RAG system evaluation.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def load_test_questions(file_path: str = None) -> Dict[str, Any]:
    """
    Load test questions from JSON file.
    
    Args:
        file_path: Path to test questions JSON file. If None, uses default path.
        
    Returns:
        Dictionary containing test questions organized by category
    """
    if file_path is None:
        # Default path relative to this script
        script_dir = Path(__file__).parent
        file_path = script_dir / "test_questions_rag_system.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


def get_all_questions(data: Dict[str, Any] = None) -> List[str]:
    """
    Get all questions as a flat list.
    
    Args:
        data: Test questions dictionary. If None, loads from default file.
        
    Returns:
        List of all test questions
    """
    if data is None:
        data = load_test_questions()
    
    all_questions = []
    categories = data.get("categories", {})
    
    for category, questions in categories.items():
        all_questions.extend(questions)
    
    return all_questions


def get_questions_by_category(category: str, data: Dict[str, Any] = None) -> List[str]:
    """
    Get questions from a specific category.
    
    Args:
        category: Category name (e.g., "treatment_effectiveness", "comparative_questions")
        data: Test questions dictionary. If None, loads from default file.
        
    Returns:
        List of questions from the specified category
    """
    if data is None:
        data = load_test_questions()
    
    categories = data.get("categories", {})
    return categories.get(category, [])


def print_questions_summary(data: Dict[str, Any] = None):
    """
    Print a summary of all test questions.
    
    Args:
        data: Test questions dictionary. If None, loads from default file.
    """
    if data is None:
        data = load_test_questions()
    
    print("=" * 80)
    print("TEST QUESTIONS SUMMARY")
    print("=" * 80)
    print()
    
    categories = data.get("categories", {})
    
    for category, questions in categories.items():
        print(f"{category.replace('_', ' ').title()}: {len(questions)} questions")
        for i, question in enumerate(questions, 1):
            print(f"  {i}. {question}")
        print()
    
    metadata = data.get("metadata", {})
    print(f"Total Questions: {metadata.get('total_questions', len(get_all_questions(data)))}")
    print(f"Categories: {metadata.get('categories', len(categories))}")
    print()


def example_usage():
    """Example of how to use the test questions."""
    print("Example Usage:\n")
    
    # Load all questions
    data = load_test_questions()
    
    # Get all questions
    all_questions = get_all_questions(data)
    print(f"Total questions available: {len(all_questions)}\n")
    
    # Get questions from a specific category
    treatment_questions = get_questions_by_category("treatment_effectiveness", data)
    print(f"Treatment effectiveness questions: {len(treatment_questions)}\n")
    print("Sample questions:")
    for q in treatment_questions[:3]:
        print(f"  - {q}")
    print()
    
    # Print full summary
    print_questions_summary(data)


if __name__ == "__main__":
    example_usage()

