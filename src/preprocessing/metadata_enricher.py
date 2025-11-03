"""
Metadata enrichment component for Cochrane RAG system.

This module handles enrichment of metadata with medical classifications,
temporal information, and quality assessments, following single responsibility principle.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional
from src.core.data_models import (
    CleanedContent, ExtractedSections, PicoElements,
    EnrichedMetadata, MedicalEntities, StudyDesign
)


class MetadataEnricher:
    """Enriches metadata with medical classifications and additional information."""
    
    # Medical specialty mapping based on topic names
    MEDICAL_SPECIALTY_MAPPING = {
        'allergy & intolerance': 'Allergy and Immunology',
        'cancer': 'Oncology',
        'heart & circulation': 'Cardiology',
        'mental health': 'Psychiatry',
        'child health': 'Pediatrics',
        'neonatal care': 'Neonatology',
        'neurology': 'Neurology',
        'infectious disease': 'Infectious Diseases',
        'lungs & airways': 'Pulmonology',
        'skin disorders': 'Dermatology',
        'urology': 'Urology',
        'dentistry & oral health': 'Dentistry',
        'rheumatology': 'Rheumatology',
        'gastroenterology & hepatology': 'Gastroenterology',
        'ear, nose & throat': 'Otolaryngology',
        'wounds': 'Wound Care',
        'complementary & alternative medicine': 'Complementary Medicine',
        'developmental, psychosocial & learning problems': 'Developmental Medicine',
        'genetic disorders': 'Medical Genetics',
        'reproductive & sexual health': 'Reproductive Medicine'
    }
    
    # Condition category mapping
    CONDITION_CATEGORY_MAPPING = {
        'allergy & intolerance': 'Immune System',
        'cancer': 'Oncological',
        'heart & circulation': 'Cardiovascular',
        'mental health': 'Psychiatric',
        'child health': 'Pediatric',
        'neonatal care': 'Neonatal',
        'neurology': 'Neurological',
        'infectious disease': 'Infectious',
        'lungs & airways': 'Respiratory',
        'skin disorders': 'Dermatological',
        'urology': 'Urological',
        'dentistry & oral health': 'Oral Health',
        'rheumatology': 'Rheumatological',
        'gastroenterology & hepatology': 'Gastrointestinal',
        'ear, nose & throat': 'ENT',
        'wounds': 'Wound Care',
        'complementary & alternative medicine': 'Alternative Medicine',
        'developmental, psychosocial & learning problems': 'Developmental',
        'genetic disorders': 'Genetic',
        'reproductive & sexual health': 'Reproductive'
    }
    
    # Intervention type patterns
    INTERVENTION_TYPE_PATTERNS = {
        'pharmacological': [
            r'drug', r'medication', r'therapy', r'treatment', r'pharmaceutical',
            r'antihistamine', r'corticosteroid', r'antibiotic', r'antiviral'
        ],
        'surgical': [
            r'surgery', r'surgical', r'operation', r'procedure', r'intervention',
            r'excision', r'resection', r'repair', r'reconstruction'
        ],
        'behavioral': [
            r'behavioral', r'psychological', r'cognitive', r'therapy', r'intervention',
            r'counseling', r'education', r'training', r'support'
        ],
        'environmental': [
            r'environmental', r'dehumidifier', r'ventilation', r'air quality',
            r'home environment', r'workplace', r'climate'
        ],
        'diagnostic': [
            r'diagnostic', r'screening', r'test', r'assessment', r'evaluation',
            r'measurement', r'monitoring'
        ]
    }
    
    def enrich_metadata(
        self,
        cleaned_content: CleanedContent,
        sections: ExtractedSections,
        pico_elements: PicoElements,
        source_file: str
    ) -> EnrichedMetadata:
        """
        Enrich metadata with medical classifications and additional information.
        
        Args:
            cleaned_content: Cleaned content with basic metadata
            sections: Extracted sections
            pico_elements: Extracted PICO elements
            source_file: Source file name
            
        Returns:
            EnrichedMetadata with enhanced information
        """
        medical_entities = self._extract_medical_entities(sections)
        medical_specialty = self._map_medical_specialty(cleaned_content.topic_name)
        condition_category = self._map_condition_category(cleaned_content.topic_name)
        intervention_type = self._identify_intervention_type(pico_elements, sections)
        evidence_level = self._determine_evidence_level_from_content(sections)
        publication_date = self._extract_publication_date(cleaned_content.full_content)
        
        return EnrichedMetadata(
            source_file=source_file,
            title=cleaned_content.title,
            doi=cleaned_content.doi,
            authors=cleaned_content.authors,
            url=cleaned_content.url,
            topic_name=cleaned_content.topic_name,
            quality_grade=cleaned_content.quality_grade,
            extraction_date=datetime.now().isoformat(),
            publication_date=publication_date,
            content_length=len(cleaned_content.full_content),
            pico_elements=pico_elements,
            medical_entities=medical_entities,
            sections_extracted=list(sections.sections.keys()),
            section_count=sections.section_count,
            subsection_count=sections.subsection_count,
            full_content=cleaned_content.full_content
        )
    
    def _extract_medical_entities(self, sections: ExtractedSections) -> MedicalEntities:
        """Extract medical entities from sections."""
        conditions = self._extract_conditions(sections)
        drugs = self._extract_drugs(sections)
        procedures = self._extract_procedures(sections)
        outcomes = self._extract_outcomes(sections)
        
        return MedicalEntities(
            conditions=conditions,
            drugs=drugs,
            procedures=procedures,
            outcomes=outcomes
        )
    
    def _extract_conditions(self, sections: ExtractedSections) -> List[str]:
        """Extract medical conditions from sections."""
        conditions = []
        
        # Common condition patterns
        condition_patterns = [
            r'asthma', r'diabetes', r'hypertension', r'depression', r'anxiety',
            r'cancer', r'stroke', r'heart disease', r'pneumonia', r'infection',
            r'allergy', r'arthritis', r'epilepsy', r'migraine', r'obesity',
            r'chronic pain', r'fibromyalgia', r'COPD', r'heart failure'
        ]
        
        for section in sections.sections.values():
            content = section.content.lower()
            for pattern in condition_patterns:
                if re.search(pattern, content):
                    conditions.append(pattern.title())
        
        return list(set(conditions))
    
    def _extract_drugs(self, sections: ExtractedSections) -> List[str]:
        """Extract drug names from sections."""
        drugs = []
        
        # Common drug patterns
        drug_patterns = [
            r'aspirin', r'ibuprofen', r'acetaminophen', r'paracetamol',
            r'prednisone', r'dexamethasone', r'hydrocortisone',
            r'antibiotic', r'antiviral', r'antifungal',
            r'antihistamine', r'antidepressant', r'antipsychotic',
            r'beta-blocker', r'ACE inhibitor', r'statin'
        ]
        
        for section in sections.sections.values():
            content = section.content.lower()
            for pattern in drug_patterns:
                if re.search(pattern, content):
                    drugs.append(pattern.title())
        
        return list(set(drugs))
    
    def _extract_procedures(self, sections: ExtractedSections) -> List[str]:
        """Extract medical procedures from sections."""
        procedures = []
        
        # Common procedure patterns
        procedure_patterns = [
            r'surgery', r'operation', r'procedure', r'intervention',
            r'biopsy', r'endoscopy', r'colonoscopy', r'laparoscopy',
            r'radiotherapy', r'chemotherapy', r'immunotherapy',
            r'physical therapy', r'occupational therapy', r'speech therapy'
        ]
        
        for section in sections.sections.values():
            content = section.content.lower()
            for pattern in procedure_patterns:
                if re.search(pattern, content):
                    procedures.append(pattern.title())
        
        return list(set(procedures))
    
    def _extract_outcomes(self, sections: ExtractedSections) -> List[str]:
        """Extract outcome measures from sections."""
        outcomes = []
        
        # Common outcome patterns
        outcome_patterns = [
            r'quality of life', r'mortality', r'morbidity', r'survival',
            r'pain relief', r'symptom improvement', r'functional status',
            r'adverse effects', r'side effects', r'complications',
            r'hospitalization', r'readmission', r'length of stay'
        ]
        
        for section in sections.sections.values():
            content = section.content.lower()
            for pattern in outcome_patterns:
                if re.search(pattern, content):
                    outcomes.append(pattern.title())
        
        return list(set(outcomes))
    
    def _map_medical_specialty(self, topic_name: str) -> str:
        """Map topic name to medical specialty."""
        topic_lower = topic_name.lower()
        return self.MEDICAL_SPECIALTY_MAPPING.get(topic_lower, 'General Medicine')
    
    def _map_condition_category(self, topic_name: str) -> str:
        """Map topic name to condition category."""
        topic_lower = topic_name.lower()
        return self.CONDITION_CATEGORY_MAPPING.get(topic_lower, 'General')
    
    def _extract_publication_date(self, content: str) -> str:
        """Extract publication date from content."""
        # Common patterns for publication dates in Cochrane reviews
        date_patterns = [
            r'Version published:\s*(\d{1,2}\s+\w+\s+\d{4})',
            r'Published:\s*(\d{1,2}\s+\w+\s+\d{4})',
            r'Publication date:\s*(\d{1,2}\s+\w+\s+\d{4})',
            r'Date published:\s*(\d{1,2}\s+\w+\s+\d{4})',
            r'(\d{1,2}\s+\w+\s+\d{4})\s*Version history',
            r'Version published:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            r'Published online:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            r'First published:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s*Published',
            r'(\d{4}-\d{2}-\d{2})',  # ISO format
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY format
            r'(\d{1,2}-\d{1,2}-\d{4})'  # MM-DD-YYYY format
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Try to parse and standardize the date
                    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                        return date_str
                    elif re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
                        parts = date_str.split('/')
                        return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                    elif re.match(r'\d{1,2}-\d{1,2}-\d{4}', date_str):
                        parts = date_str.split('-')
                        return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                    else:
                        # Try to parse common date formats
                        from dateutil import parser
                        parsed_date = parser.parse(date_str)
                        return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
        
        # If no date found, return current date as fallback
        return datetime.now().strftime('%Y-%m-%d')
    
    def _identify_intervention_type(self, pico_elements: PicoElements, sections: ExtractedSections) -> str:
        """Identify the primary intervention type."""
        intervention_text = ' '.join(pico_elements.intervention).lower()
        
        for intervention_type, patterns in self.INTERVENTION_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, intervention_text):
                    return intervention_type
        
        return 'Other'
    
    def _determine_evidence_level_from_content(self, sections: ExtractedSections) -> str:
        """Determine evidence level based on content analysis."""
        # Look for study design indicators in the content
        content_text = ' '.join([section.content for section in sections.sections.values()]).lower()
        
        if any(term in content_text for term in ['systematic review', 'cochrane review', 'meta-analysis']):
            return 'High'
        elif any(term in content_text for term in ['randomized controlled trial', 'rct', 'randomised controlled trial']):
            return 'Moderate'
        elif any(term in content_text for term in ['observational study', 'cohort study', 'case-control study']):
            return 'Low'
        else:
            return 'Unknown'
