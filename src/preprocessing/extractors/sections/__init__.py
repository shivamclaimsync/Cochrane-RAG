"""
Section extractors module.
Contains individual extractors for each Cochrane section type.
"""

from .abstract_extractor import AbstractExtractor
from .picos_extractor import PicosExtractor
from .plain_language_summary_extractor import PlainLanguageSummaryExtractor
from .summary_of_findings_extractor import SummaryOfFindingsExtractor
from .authors_conclusions_extractor import AuthorsConclusionsExtractor
from .background_extractor import BackgroundExtractor
from .objectives_extractor import ObjectivesExtractor
from .methods_extractor import MethodsExtractor
from .results_extractor import ResultsExtractor
from .discussion_extractor import DiscussionExtractor

__all__ = [
    'AbstractExtractor',
    'PicosExtractor', 
    'PlainLanguageSummaryExtractor',
    'SummaryOfFindingsExtractor',
    'AuthorsConclusionsExtractor',
    'BackgroundExtractor',
    'ObjectivesExtractor',
    'MethodsExtractor',
    'ResultsExtractor',
    'DiscussionExtractor'
]
