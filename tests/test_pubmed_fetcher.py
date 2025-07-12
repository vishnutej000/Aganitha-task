"""
Tests for the PubMed paper fetcher module.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from pubmed_fetcher.models import Paper, Author
from pubmed_fetcher.utils import CompanyDetector, filter_authors_by_company_affiliation
from pubmed_fetcher.fetcher import PubMedFetcher


class TestCompanyDetector:
    """Test the CompanyDetector utility class."""
    
    def test_known_company_detection(self):
        """Test detection of known pharmaceutical companies."""
        assert CompanyDetector.is_pharma_biotech_affiliation("Pfizer Inc.")
        assert CompanyDetector.is_pharma_biotech_affiliation("Novartis Pharmaceuticals")
        assert CompanyDetector.is_pharma_biotech_affiliation("Johnson & Johnson")
    
    def test_keyword_detection(self):
        """Test detection based on pharmaceutical keywords."""
        assert CompanyDetector.is_pharma_biotech_affiliation("BioTech Solutions Ltd.")
        assert CompanyDetector.is_pharma_biotech_affiliation("Pharmaceutical Research Corp.")
        assert CompanyDetector.is_pharma_biotech_affiliation("Life Sciences Company")
    
    def test_academic_institutions_not_detected(self):
        """Test that academic institutions are not detected as companies."""
        assert not CompanyDetector.is_pharma_biotech_affiliation("Harvard University")
        assert not CompanyDetector.is_pharma_biotech_affiliation("MIT Department of Biology")
        assert not CompanyDetector.is_pharma_biotech_affiliation("Stanford Research Institute")
    
    def test_extract_company_names(self):
        """Test extraction of company names from affiliations."""
        companies = CompanyDetector.extract_company_names("Pfizer Inc., New York, NY")
        assert "Pfizer" in companies
        
        companies = CompanyDetector.extract_company_names("BioTech Solutions Ltd.")
        assert len(companies) > 0


class TestModels:
    """Test the data models."""
    
    def test_author_full_name(self):
        """Test author full name property."""
        author = Author(first_name="John", last_name="Doe", initials="JD")
        assert author.full_name == "Doe JD"
        
        author_no_initials = Author(first_name="Jane", last_name="Smith")
        assert author_no_initials.full_name == "Jane Smith"
    
    def test_paper_corresponding_author_email(self):
        """Test extraction of corresponding author email."""
        authors = [
            Author(first_name="John", last_name="Doe", email="john@example.com", is_corresponding=True),
            Author(first_name="Jane", last_name="Smith", email="jane@example.com", is_corresponding=False)
        ]
        
        paper = Paper(
            pubmed_id="12345",
            title="Test Paper",
            publication_date=datetime.now(),
            authors=authors
        )
        
        assert paper.corresponding_author_email == "john@example.com"
    
    def test_non_academic_authors(self):
        """Test filtering of non-academic authors."""
        authors = [
            Author(first_name="John", last_name="Doe", affiliation="Pfizer Inc."),
            Author(first_name="Jane", last_name="Smith", affiliation="Harvard University"),
            Author(first_name="Bob", last_name="Johnson", affiliation="BioTech Corp.")
        ]
        
        paper = Paper(
            pubmed_id="12345",
            title="Test Paper",
            publication_date=datetime.now(),
            authors=authors
        )
        
        non_academic = paper.non_academic_authors
        assert len(non_academic) == 2
        assert all(author.last_name in ["Doe", "Johnson"] for author in non_academic)


class TestPubMedFetcher:
    """Test the PubMed fetcher."""
    
    @patch('pubmed_fetcher.fetcher.requests.Session.get')
    def test_search_papers(self, mock_get):
        """Test paper search functionality."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'esearchresult': {
                'idlist': ['12345', '67890']
            }
        }
        mock_get.return_value = mock_response
        
        fetcher = PubMedFetcher()
        ids = fetcher.search_papers("cancer treatment")
        
        assert len(ids) == 2
        assert "12345" in ids
        assert "67890" in ids
    
    def test_filter_authors_by_company_affiliation(self):
        """Test filtering authors by company affiliation."""
        authors = [
            Author(first_name="John", last_name="Doe", affiliation="Pfizer Inc."),
            Author(first_name="Jane", last_name="Smith", affiliation="Harvard University"),
            Author(first_name="Bob", last_name="Johnson", affiliation="Novartis")
        ]
        
        filtered = filter_authors_by_company_affiliation(authors)
        assert len(filtered) == 2
        assert all(author.last_name in ["Doe", "Johnson"] for author in filtered)


if __name__ == '__main__':
    pytest.main([__file__])
