"""
Query rewriting system for medical RAG with HyDE (Hypothetical Document Embeddings).

Rewrites queries using multiple strategies:
1. Medical synonym expansion (rule-based)
2. LLM reformulation (alternative phrasings)
3. HyDE (generate hypothetical answer, then search with it)
"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class QueryVariant:
    """Single query variant with metadata."""
    text: str
    strategy: str  # "original", "synonyms", "llm_reformulation", "hyde"
    weight: float = 1.0  # For fusion scoring


class MedicalQueryRewriter:
    """
    Multi-strategy query rewriting for medical RAG.
    
    Strategies:
    1. Medical synonym expansion (rule-based, fast)
    2. LLM-based reformulation (better quality)
    3. HyDE (hypothetical document embedding) - generates what an ideal answer would look like
    """
    
    def __init__(
        self,
        enable_synonyms: bool = True,
        enable_llm: bool = True,
        enable_hyde: bool = True,
        model: str = "gpt-4o-mini",  # Cheaper model for rewrites
        temperature: float = 0.7,
    ):
        """
        Initialize query rewriter.
        
        Args:
            enable_synonyms: Enable medical synonym expansion
            enable_llm: Enable LLM-based reformulation
            enable_hyde: Enable HyDE (hypothetical document generation)
            model: OpenAI model for LLM operations
            temperature: Sampling temperature
        """
        self.enable_synonyms = enable_synonyms
        self.enable_llm = enable_llm
        self.enable_hyde = enable_hyde
        self.model = model
        self.temperature = temperature
        
        # Medical terminology mappings
        self.medical_synonyms = self._load_medical_synonyms()
        
        if enable_llm or enable_hyde:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY must be set in .env file")
            self.client = OpenAI(api_key=api_key)
    
    def rewrite_query(
        self, 
        query: str, 
        num_variants: int = 2
    ) -> List[QueryVariant]:
        """
        Generate query variants using multiple strategies.
        
        Args:
            query: Original user query
            num_variants: Number of LLM variants to generate (if enabled)
        
        Returns:
            List of QueryVariant objects with different rewritten versions
        """
        variants = [QueryVariant(text=query, strategy="original", weight=1.0)]
        
        print(f"🔄 Rewriting query: '{query[:80]}...'")
        
        # Strategy 1: Synonym expansion
        if self.enable_synonyms:
            synonym_variant = self._expand_medical_synonyms(query)
            if synonym_variant != query:  # Only add if different
                variants.append(QueryVariant(
                    text=synonym_variant,
                    strategy="synonyms",
                    weight=0.8
                ))
                print(f"  📖 Synonym expansion: '{synonym_variant[:80]}...'")
        
        # Strategy 2: LLM reformulation
        if self.enable_llm:
            llm_variants = self._llm_reformulate(query, num_variants=num_variants)
            variants.extend(llm_variants)
            for var in llm_variants:
                print(f"  🤖 LLM reformulation: '{var.text[:80]}...'")
        
        # Strategy 3: HyDE (hypothetical document)
        if self.enable_hyde:
            hyde_variant = self._generate_hypothetical_answer(query)
            if hyde_variant and hyde_variant != query:
                variants.append(QueryVariant(
                    text=hyde_variant,
                    strategy="hyde",
                    weight=0.9
                ))
                print(f"  🔮 HyDE (hypothetical): '{hyde_variant[:80]}...'")
        
        print(f"  ✅ Generated {len(variants)} query variants")
        return variants
    
    def _expand_medical_synonyms(self, query: str) -> str:
        """
        Rule-based synonym expansion for medical terms.
        
        Args:
            query: Original query
            
        Returns:
            Query with expanded medical synonyms
        """
        expanded = query.lower()
        added_terms = []
        
        for term, synonyms in self.medical_synonyms.items():
            if term.lower() in expanded:
                # Add synonyms after the original term
                added_terms.extend(synonyms)
        
        # Append synonyms at the end
        if added_terms:
            return f"{query} {' '.join(added_terms)}"
        
        return query
    
    def _llm_reformulate(self, query: str, num_variants: int = 2) -> List[QueryVariant]:
        """
        Use LLM to reformulate query with medical terminology.
        
        Args:
            query: Original query
            num_variants: Number of variants to generate
            
        Returns:
            List of reformulated query variants
        """
        system_prompt = """You are a medical librarian helping to reformulate queries for searching Cochrane systematic reviews.

Generate alternative phrasings that:
1. Use medical terminology and standard acronyms (e.g., NSCLC for non-small cell lung cancer)
2. Focus on PICO elements (Population, Intervention, Comparison, Outcome)
3. Include relevant clinical terminology
4. Keep queries concise and focused

Return ONLY the reformulated queries, one per line, without numbering or bullets."""

        user_prompt = f"""Original query: {query}

Generate {num_variants} alternative phrasings for better medical literature search:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            variants = []
            
            for i, line in enumerate(content.split('\n')):
                line = line.strip().lstrip('123456789.-) ')
                if line:
                    variants.append(QueryVariant(
                        text=line,
                        strategy="llm_reformulation",
                        weight=0.9
                    ))
            
            return variants[:num_variants]
            
        except Exception as e:
            print(f"⚠️ LLM reformulation failed: {e}")
            return []
    
    def _generate_hypothetical_answer(self, query: str) -> str:
        """
        HyDE: Generate hypothetical answer to search with.
        
        This generates what an ideal answer from a Cochrane review would look like,
        then uses that text for semantic search. This often retrieves more relevant
        documents than searching with the question.
        
        Args:
            query: Original query
            
        Returns:
            Hypothetical answer text
        """
        prompt = f"""Generate a short paragraph (3-4 sentences) that would appear in a Cochrane systematic review answering this question:

"{query}"

Write as if you are writing the conclusion section of a Cochrane review. Use medical terminology, mention typical elements like interventions, outcomes, and evidence quality. Be specific and factual."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=200
            )
            
            hypothetical = response.choices[0].message.content.strip()
            return hypothetical
            
        except Exception as e:
            print(f"⚠️ HyDE generation failed: {e}")
            return query
    
    def _load_medical_synonyms(self) -> Dict[str, List[str]]:
        """
        Load medical synonym dictionary.
        
        Maps common terms to medical terminology, acronyms, and related terms.
        Focused on Cochrane review topics.
        
        Returns:
            Dictionary mapping terms to lists of synonyms
        """
        return {
            # Cancer terms
            "lung cancer": ["NSCLC", "SCLC", "pulmonary carcinoma", "bronchogenic carcinoma"],
            "breast cancer": ["mammary carcinoma", "breast neoplasm", "mammary neoplasm"],
            "colorectal cancer": ["CRC", "colon cancer", "rectal cancer", "bowel cancer"],
            "prostate cancer": ["prostatic neoplasm", "prostatic carcinoma"],
            "melanoma": ["malignant melanoma", "skin cancer"],
            "pancreatic cancer": ["pancreatic carcinoma", "pancreatic neoplasm"],
            
            # Treatment terms
            "chemotherapy": ["cytotoxic therapy", "antineoplastic agents", "chemo"],
            "immunotherapy": ["immune checkpoint inhibitor", "PD-1", "PD-L1", "CTLA-4"],
            "radiation therapy": ["radiotherapy", "RT", "radiation treatment"],
            "surgery": ["surgical intervention", "operative procedure", "resection"],
            "targeted therapy": ["molecular targeted therapy", "biological therapy"],
            
            # Common conditions
            "asthma": ["bronchial asthma", "reactive airway disease"],
            "diabetes": ["diabetes mellitus", "DM", "hyperglycemia"],
            "hypertension": ["high blood pressure", "HTN", "elevated blood pressure"],
            "obesity": ["overweight", "excessive body weight", "BMI"],
            "depression": ["major depressive disorder", "MDD", "depressive disorder"],
            "anxiety": ["anxiety disorder", "GAD", "generalized anxiety"],
            "ADHD": ["attention deficit hyperactivity disorder", "attention deficit disorder", "ADD"],
            "autism": ["autism spectrum disorder", "ASD", "autistic disorder"],
            
            # Population terms
            "children": ["pediatric", "paediatric", "child", "infant", "adolescent"],
            "elderly": ["geriatric", "older adults", "aged", "senior"],
            "adults": ["adult population", "grown"],
            "pregnant": ["pregnancy", "gestational", "prenatal", "antenatal"],
            
            # Complementary medicine
            "acupuncture": ["needle therapy", "traditional Chinese medicine", "TCM"],
            "herbal medicine": ["botanical medicine", "phytotherapy", "herbal therapy"],
            "meditation": ["mindfulness", "contemplative practice"],
            "yoga": ["hatha yoga", "yogic practice"],
            "massage": ["manual therapy", "soft tissue manipulation"],
            
            # Outcomes and measures
            "effective": ["efficacy", "efficacious", "beneficial", "successful"],
            "treatment": ["therapy", "intervention", "management"],
            "prevention": ["prophylaxis", "preventive", "preventative"],
            "pain": ["analgesia", "pain relief", "pain management", "nociception"],
            "infection": ["infectious disease", "bacterial infection", "viral infection"],
            "chronic": ["long-term", "persistent", "ongoing"],
            "acute": ["short-term", "sudden onset", "immediate"],
        }


class QueryFusionRetriever:
    """
    Retriever that uses query rewriting and result fusion.
    
    Process:
    1. Rewrite query into multiple variants
    2. Search with each variant
    3. Fuse results using Reciprocal Rank Fusion (RRF)
    """
    
    def __init__(
        self,
        base_retriever,
        rewriter: Optional[MedicalQueryRewriter] = None,
        k_per_variant: int = 10,
        final_k: int = 10,
        rrf_k: int = 60,
    ):
        """
        Initialize fusion retriever.
        
        Args:
            base_retriever: Base retriever instance (CochraneRetriever)
            rewriter: Query rewriter instance
            k_per_variant: Number of results per query variant
            final_k: Final number of results after fusion
            rrf_k: RRF constant (default 60 as per literature)
        """
        self.base_retriever = base_retriever
        self.rewriter = rewriter or MedicalQueryRewriter()
        self.k_per_variant = k_per_variant
        self.final_k = final_k
        self.rrf_k = rrf_k
    
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        **search_kwargs
    ) -> List:
        """
        Retrieve using query rewriting and result fusion.
        
        Args:
            query: User query
            top_k: Number of final results
            **search_kwargs: Additional arguments for base retriever
            
        Returns:
            List of fused retrieval results
        """
        # Step 1: Generate query variants
        variants = self.rewriter.rewrite_query(query, num_variants=2)
        
        # Step 2: Search with each variant
        all_results = {}  # chunk_id -> RetrievalResult
        variant_ranks = {}  # chunk_id -> list of (rank, weight) tuples
        
        for variant in variants:
            try:
                # Search with this variant
                results = self.base_retriever.search(
                    variant.text,
                    limit=self.k_per_variant,
                    **search_kwargs
                )
                
                # Store results and ranks
                for rank, result in enumerate(results):
                    chunk_id = result.chunk_id
                    
                    if chunk_id not in all_results:
                        all_results[chunk_id] = result
                        variant_ranks[chunk_id] = []
                    
                    # Store rank with strategy weight
                    variant_ranks[chunk_id].append((rank, variant.weight))
                    
            except Exception as e:
                print(f"⚠️ Error searching with variant '{variant.text[:50]}...': {e}")
                continue
        
        if not all_results:
            print("⚠️ No results retrieved from any query variant")
            return []
        
        # Step 3: Reciprocal Rank Fusion (RRF)
        fusion_scores = {}
        
        for chunk_id, ranks in variant_ranks.items():
            # RRF formula: sum of weight / (k + rank) for each appearance
            rrf_score = sum(weight / (self.rrf_k + rank) for rank, weight in ranks)
            fusion_scores[chunk_id] = rrf_score
        
        # Step 4: Sort by fusion score and return top results
        sorted_chunks = sorted(
            fusion_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        fused_results = [all_results[chunk_id] for chunk_id, _ in sorted_chunks]
        
        print(f"✅ Fused {len(all_results)} unique results into top {len(fused_results)}")
        return fused_results
    
    def close(self):
        """Close underlying retriever connections."""
        if self.base_retriever:
            self.base_retriever.close()

