__version__ = "0.1.0"
__author__ = "Research Intelligence Tool"

from .paper_hunter import PaperHunter
from .research_types import ResearchAuthor, ResearchPaper, SearchRequest
from .company_finder import IndustryDetector

__all__ = ["PaperHunter", "ResearchAuthor", "ResearchPaper", "SearchRequest", "IndustryDetector"]