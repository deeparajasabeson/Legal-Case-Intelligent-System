import google.generativeai as genai
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import re
from collections import defaultdict

class PrecedentMiningAgent:
    """AI agent for discovering and analyzing legal precedents"""

    def __init__(self):
        # Configure Gemini AI
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

        # Precedent analysis prompts
        self.precedent_prompts = {
            'precedent_discovery': """
                You are a legal precedent research specialist analyzing case precedents.

                Legal Issue: {legal_issue}
                Jurisdiction: {jurisdiction}
                Case Facts: {case_facts}

                Available Precedents: {precedent_data}
                Related Case Law: {case_law_data}

                Provide comprehensive precedent analysis:

                1. BINDING AUTHORITY ANALYSIS
                   - Identify controlling precedents in jurisdiction
                   - Analyze precedential hierarchy and weight
                   - Evaluate binding vs. persuasive authority
                   - Assess jurisdictional applicability

                2. PRECEDENT STRENGTH EVALUATION (Score 1-10 for each)
                   - Legal authority strength
                   - Factual similarity to current case
                   - Recency and currency of precedent
                   - Judicial treatment and citations

                3. ANALOGICAL REASONING ANALYSIS
                   - Key factual similarities and differences
                   - Legal principle application
                   - Distinguishing factors identification
                   - Analogical strength assessment

                4. ADVERSE PRECEDENT IDENTIFICATION
                   - Potentially harmful precedents
                   - Distinguishing strategies
                   - Limitation arguments
                   - Overruling possibilities

                5. STRATEGIC PRECEDENT RECOMMENDATIONS
                   - Most favorable precedents to cite
                   - Precedent citation order and emphasis
                   - Factual analogy development
                   - Legal argument construction

                Focus on practical strategic value with specific citation recommendations.
            """,

            'precedent_comparison': """
                You are analyzing multiple precedents for comparative legal analysis.

                Target Case Profile: {target_case}
                Precedent Cases: {precedent_cases}
                Legal Framework: {legal_framework}

                Conduct comparative precedent analysis:

                1. PRECEDENT RANKING BY RELEVANCE
                   - Rank precedents by applicability (1-10 scale)
                   - Justify ranking based on legal and factual similarity
                   - Identify primary vs. secondary precedents
                   - Assess strategic citation value

                2. FACTUAL PATTERN ANALYSIS
                   - Compare fact patterns across precedents
                   - Identify recurring legal themes
                   - Analyze outcome predictors
                   - Map factual distinctions

                3. LEGAL DOCTRINE EVOLUTION
                   - Trace development of legal principles
                   - Identify doctrinal trends and shifts
                   - Analyze judicial reasoning patterns
                   - Predict future doctrinal development

                4. STRATEGIC CITATION RECOMMENDATIONS
                   - Optimal precedent selection strategy
                   - Citation sequencing and emphasis
                   - Distinguishing adverse precedents
                   - Building persuasive precedent chain

                Provide actionable strategic guidance for precedent utilization.
            """,

            'precedent_validation': """
                You are validating the current status and treatment of legal precedents.

                Primary Precedents: {primary_precedents}
                Citation History: {citation_history}
                Subsequent Treatment: {subsequent_treatment}

                Validate precedent authority:

                1. PRECEDENT VITALITY ASSESSMENT
                   - Current validity status
                   - Overruling or modification analysis
                   - Statutory supersession review
                   - Judicial criticism evaluation

                2. CITATION TREATMENT ANALYSIS
                   - Positive citations and follow-on cases
                   - Negative treatment and distinctions
                   - Limiting or narrowing decisions
                   - Expansion or broadening applications

                3. JURISDICTIONAL AUTHORITY VERIFICATION
                   - Binding authority confirmation
                   - Cross-jurisdictional treatment
                   - Federal vs. state precedent analysis
                   - Circuit split identification

                4. STRATEGIC RELIABILITY ASSESSMENT
                   - Safe-to-cite evaluation
                   - Risk of adverse treatment
                   - Alternative precedent options
                   - Backup authority recommendations

                Focus on precedent reliability and strategic citation safety.
            """
        }

    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect('database/legal_data.db')

    def discover_relevant_precedents(self, legal_issue: str, jurisdiction: str, case_facts: str = "") -> Dict:
        """Discover and analyze relevant legal precedents"""
        try:
            # Search for relevant precedents
            precedent_results = self._search_precedents(legal_issue, jurisdiction)

            # Get related case law
            case_law_results = self._search_related_case_law(legal_issue, jurisdiction)

            # Prepare data for AI analysis
            analysis_context = {
                'legal_issue': legal_issue,
                'jurisdiction': jurisdiction,
                'case_facts': case_facts,
                'precedent_data': json.dumps(precedent_results, indent=2),
                'case_law_data': json.dumps(case_law_results, indent=2)
            }

            # Generate precedent analysis
            prompt = self.precedent_prompts['precedent_discovery'].format(**analysis_context)
            response = self.model.generate_content(prompt)
            precedent_analysis = response.text

            # Process and rank precedents
            ranked_precedents = self._rank_precedents(precedent_results, precedent_analysis)

            # Identify adverse precedents
            adverse_precedents = self._identify_adverse_precedents(legal_issue, jurisdiction, precedent_analysis)

            return {
                'legal_issue': legal_issue,
                'jurisdiction': jurisdiction,
                'case_facts': case_facts,
                'precedent_analysis': precedent_analysis,
                'favorable_precedents': ranked_precedents['favorable'],
                'adverse_precedents': adverse_precedents,
                'binding_authority': ranked_precedents['binding'],
                'persuasive_authority': ranked_precedents['persuasive'],
                'strategic_recommendations': self._extract_strategic_recommendations(precedent_analysis),
                'citation_suggestions': self._generate_citation_suggestions(ranked_precedents),
                'research_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Precedent discovery failed: {str(e)}",
                'legal_issue': legal_issue,
                'jurisdiction': jurisdiction
            }

    def compare_precedents(self, target_case: Dict, precedent_list: List[Dict], legal_framework: str = "") -> Dict:
        """Compare multiple precedents for strategic analysis"""
        try:
            # Prepare comparison context
            comparison_context = {
                'target_case': json.dumps(target_case, indent=2),
                'precedent_cases': json.dumps(precedent_list, indent=2),
                'legal_framework': legal_framework
            }

            # Generate comparative analysis
            prompt = self.precedent_prompts['precedent_comparison'].format(**comparison_context)
            response = self.model.generate_content(prompt)
            comparison_analysis = response.text

            # Extract rankings and scores
            precedent_rankings = self._extract_precedent_rankings(comparison_analysis, precedent_list)

            # Analyze factual patterns
            factual_analysis = self._analyze_factual_patterns(target_case, precedent_list)

            # Generate strategic recommendations
            strategic_recommendations = self._extract_strategic_recommendations(comparison_analysis)

            return {
                'target_case': target_case,
                'precedent_count': len(precedent_list),
                'comparison_analysis': comparison_analysis,
                'precedent_rankings': precedent_rankings,
                'factual_pattern_analysis': factual_analysis,
                'strategic_recommendations': strategic_recommendations,
                'optimal_citation_order': self._determine_optimal_citation_order(precedent_rankings),
                'distinguishing_strategies': self._extract_distinguishing_strategies(comparison_analysis),
                'comparison_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Precedent comparison failed: {str(e)}",
                'target_case': target_case
            }

    def validate_precedent_authority(self, precedent_citations: List[str]) -> Dict:
        """Validate current authority and treatment of precedents"""
        try:
            # Get precedent details
            precedent_details = self._get_precedent_details(precedent_citations)

            # Check citation history and treatment
            citation_history = self._check_citation_history(precedent_citations)

            # Analyze subsequent treatment
            subsequent_treatment = self._analyze_subsequent_treatment(precedent_citations)

            # Prepare validation context
            validation_context = {
                'primary_precedents': json.dumps(precedent_details, indent=2),
                'citation_history': json.dumps(citation_history, indent=2),
                'subsequent_treatment': json.dumps(subsequent_treatment, indent=2)
            }

            # Generate validation analysis
            prompt = self.precedent_prompts['precedent_validation'].format(**validation_context)
            response = self.model.generate_content(prompt)
            validation_analysis = response.text

            # Extract validation results
            validity_status = self._extract_validity_status(validation_analysis)
            citation_safety = self._assess_citation_safety(validation_analysis)

            return {
                'precedent_citations': precedent_citations,
                'validation_analysis': validation_analysis,
                'validity_status': validity_status,
                'citation_safety': citation_safety,
                'recommended_precedents': self._filter_safe_precedents(precedent_details, validity_status),
                'alternative_authorities': self._suggest_alternative_authorities(precedent_details, validity_status),
                'validation_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Precedent validation failed: {str(e)}",
                'precedent_citations': precedent_citations
            }

    def find_analogous_cases(self, case_facts: str, legal_principles: List[str], jurisdiction: str = "Federal") -> Dict:
        """Find cases with analogous factual patterns"""
        try:
            # Search for factually similar cases
            analogous_cases = self._search_analogous_cases(case_facts, jurisdiction)

            # Filter by legal principles
            filtered_cases = self._filter_by_legal_principles(analogous_cases, legal_principles)

            # Calculate similarity scores
            similarity_scores = self._calculate_similarity_scores(case_facts, filtered_cases)

            # Generate analogy analysis
            analogy_prompt = f"""
                Analyze factual analogies for legal precedent application.

                Target Case Facts: {case_facts}
                Legal Principles: {', '.join(legal_principles)}
                Analogous Cases: {json.dumps(filtered_cases, indent=2)}

                Provide analogy analysis:
                1. Strongest factual analogies and their legal significance
                2. Key distinguishing factors and their importance
                3. Analogical reasoning strengths and weaknesses
                4. Strategic use recommendations for each analogous case
            """

            response = self.model.generate_content(analogy_prompt)
            analogy_analysis = response.text

            return {
                'target_facts': case_facts,
                'legal_principles': legal_principles,
                'jurisdiction': jurisdiction,
                'analogous_cases': filtered_cases,
                'similarity_scores': similarity_scores,
                'analogy_analysis': analogy_analysis,
                'strongest_analogies': self._identify_strongest_analogies(similarity_scores, analogy_analysis),
                'distinguishing_factors': self._extract_distinguishing_factors(analogy_analysis),
                'analogy_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Analogous case search failed: {str(e)}",
                'case_facts': case_facts
            }

    def _search_precedents(self, legal_issue: str, jurisdiction: str, limit: int = 10) -> List[Dict]:
        """Search precedent database"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.precedent_id, p.legal_principle, p.binding_authority,
                   p.jurisdiction, p.precedent_weight, p.related_statutes,
                   c.case_name, c.citation, c.holding, c.decision_date
            FROM legal_precedents p
            JOIN case_law c ON p.case_id = c.case_id
            WHERE p.legal_principle LIKE ?
               OR p.related_statutes LIKE ?
               OR c.legal_issues LIKE ?
        """, (f"%{legal_issue}%", f"%{legal_issue}%", f"%{legal_issue}%"))

        if jurisdiction and jurisdiction != "Federal":
            cursor.execute(cursor.lastrowid, cursor.lastrowid + " AND p.jurisdiction = ?", (jurisdiction,))

        cursor.execute(cursor.lastrowid, cursor.lastrowid + " ORDER BY p.precedent_weight DESC LIMIT ?", (limit,))

        results = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def _search_related_case_law(self, legal_issue: str, jurisdiction: str, limit: int = 5) -> List[Dict]:
        """Search for related case law"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT case_name, citation, holding, legal_issues, decision_date, court
            FROM case_law
            WHERE legal_issues LIKE ? OR holding LIKE ?
        """, (f"%{legal_issue}%", f"%{legal_issue}%"))

        if jurisdiction and jurisdiction != "Federal":
            cursor.execute(cursor.lastrowid, cursor.lastrowid + " AND jurisdiction = ?", (jurisdiction,))

        cursor.execute(cursor.lastrowid, cursor.lastrowid + " ORDER BY decision_date DESC LIMIT ?", (limit,))

        results = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def _rank_precedents(self, precedents: List[Dict], analysis: str) -> Dict:
        """Rank precedents by favorability and authority"""
        ranked = {
            'favorable': [],
            'adverse': [],
            'binding': [],
            'persuasive': []
        }

        for precedent in precedents:
            # Simple ranking based on precedent weight and analysis content
            weight = precedent.get('precedent_weight', 5)
            authority = precedent.get('binding_authority', '').lower()

            # Classify by authority type
            if 'supreme court' in authority or 'binding' in authority:
                ranked['binding'].append({**precedent, 'rank_score': weight})
            else:
                ranked['persuasive'].append({**precedent, 'rank_score': weight})

            # Classify by favorability (simplified analysis)
            case_name = precedent.get('case_name', '').lower()
            if any(positive in analysis.lower() for positive in ['favorable', 'support', 'strengthens']):
                if case_name in analysis.lower():
                    ranked['favorable'].append({**precedent, 'rank_score': weight})

        # Sort each category by rank score
        for category in ranked:
            ranked[category].sort(key=lambda x: x.get('rank_score', 0), reverse=True)

        return ranked

    def _identify_adverse_precedents(self, legal_issue: str, jurisdiction: str, analysis: str) -> List[Dict]:
        """Identify potentially adverse precedents"""
        # Search for precedents that might be adverse
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Look for precedents with opposing outcomes or principles
        opposing_terms = ['against', 'denied', 'dismissed', 'rejected', 'failed']
        adverse_precedents = []

        for term in opposing_terms:
            cursor.execute("""
                SELECT p.precedent_id, p.legal_principle, c.case_name, c.citation, c.holding
                FROM legal_precedents p
                JOIN case_law c ON p.case_id = c.case_id
                WHERE (c.holding LIKE ? OR p.legal_principle LIKE ?)
                  AND (p.legal_principle LIKE ? OR c.legal_issues LIKE ?)
                LIMIT 3
            """, (f"%{term}%", f"%{term}%", f"%{legal_issue}%", f"%{legal_issue}%"))

            results = cursor.fetchall()
            for row in results:
                adverse_precedents.append(dict(zip([col[0] for col in cursor.description], row)))

        conn.close()
        return adverse_precedents[:5]  # Limit to top 5

    def _extract_strategic_recommendations(self, analysis: str) -> List[str]:
        """Extract strategic recommendations from analysis"""
        recommendations = []
        lines = analysis.split('\n')
        in_recommendations = False

        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'strategic', 'suggest']):
                in_recommendations = True
                continue
            elif in_recommendations and line.strip():
                if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line.strip()):
                    recommendations.append(line.strip().lstrip('- *•0123456789. '))
                elif line.strip().isupper():
                    break

        return recommendations[:8]

    def _generate_citation_suggestions(self, ranked_precedents: Dict) -> Dict:
        """Generate strategic citation suggestions"""
        suggestions = {
            'primary_citations': [],
            'supporting_citations': [],
            'distinguishing_citations': []
        }

        # Primary citations from binding authority
        binding = ranked_precedents.get('binding', [])
        if binding:
            suggestions['primary_citations'] = [
                {'case_name': p.get('case_name'), 'citation': p.get('citation')}
                for p in binding[:3]
            ]

        # Supporting citations from favorable precedents
        favorable = ranked_precedents.get('favorable', [])
        suggestions['supporting_citations'] = [
            {'case_name': p.get('case_name'), 'citation': p.get('citation')}
            for p in favorable[:5]
        ]

        return suggestions

    def _extract_precedent_rankings(self, analysis: str, precedent_list: List[Dict]) -> List[Dict]:
        """Extract precedent rankings from comparison analysis"""
        rankings = []

        for i, precedent in enumerate(precedent_list):
            case_name = precedent.get('case_name', '')

            # Look for ranking information in analysis
            rank_pattern = rf'{re.escape(case_name)}.*?(\d+(?:\.\d+)?)'
            match = re.search(rank_pattern, analysis, re.IGNORECASE)

            if match:
                score = float(match.group(1))
            else:
                score = 5.0  # Default score

            rankings.append({
                **precedent,
                'relevance_score': score,
                'ranking_position': i + 1
            })

        # Sort by relevance score
        rankings.sort(key=lambda x: x['relevance_score'], reverse=True)
        return rankings

    def _analyze_factual_patterns(self, target_case: Dict, precedents: List[Dict]) -> Dict:
        """Analyze factual patterns across precedents"""
        patterns = {
            'common_facts': [],
            'distinguishing_facts': [],
            'fact_categories': defaultdict(list)
        }

        target_facts = target_case.get('case_facts', '').lower()

        for precedent in precedents:
            precedent_facts = precedent.get('holding', '').lower()

            # Simple fact pattern analysis
            common_words = set(target_facts.split()) & set(precedent_facts.split())
            if len(common_words) > 3:
                patterns['common_facts'].append({
                    'case': precedent.get('case_name'),
                    'common_elements': list(common_words)[:5]
                })

        return patterns

    def _determine_optimal_citation_order(self, ranked_precedents: List[Dict]) -> List[str]:
        """Determine optimal order for citing precedents"""
        return [p.get('case_name', '') for p in ranked_precedents[:5]]

    def _extract_distinguishing_strategies(self, analysis: str) -> List[str]:
        """Extract strategies for distinguishing adverse precedents"""
        strategies = []
        lines = analysis.split('\n')

        for line in lines:
            if 'distinguish' in line.lower() or 'different' in line.lower():
                strategies.append(line.strip())

        return strategies[:5]

    def _get_precedent_details(self, citations: List[str]) -> List[Dict]:
        """Get detailed information for precedent citations"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        details = []

        for citation in citations:
            cursor.execute("""
                SELECT c.case_name, c.citation, c.holding, c.decision_date,
                       p.legal_principle, p.binding_authority, p.precedent_weight
                FROM case_law c
                LEFT JOIN legal_precedents p ON c.case_id = p.case_id
                WHERE c.citation LIKE ?
            """, (f"%{citation}%",))

            result = cursor.fetchone()
            if result:
                details.append(dict(zip([col[0] for col in cursor.description], result)))

        conn.close()
        return details

    def _check_citation_history(self, citations: List[str]) -> Dict:
        """Check how precedents have been cited in subsequent cases"""
        # Simplified citation history check
        return {
            'positive_citations': len(citations) * 5,  # Mock data
            'negative_treatment': 0,
            'recent_citations': len(citations) * 2
        }

    def _analyze_subsequent_treatment(self, citations: List[str]) -> Dict:
        """Analyze how precedents have been treated in later cases"""
        # Simplified subsequent treatment analysis
        return {
            'followed': len(citations) * 3,
            'distinguished': len(citations),
            'criticized': 0,
            'overruled': 0
        }

    def _extract_validity_status(self, analysis: str) -> Dict:
        """Extract validity status from analysis"""
        status = {}

        if 'valid' in analysis.lower() and 'invalid' not in analysis.lower():
            status['overall_validity'] = 'valid'
        elif 'overruled' in analysis.lower():
            status['overall_validity'] = 'overruled'
        else:
            status['overall_validity'] = 'uncertain'

        return status

    def _assess_citation_safety(self, analysis: str) -> str:
        """Assess safety of citing precedents"""
        if 'safe to cite' in analysis.lower() or ('valid' in analysis.lower() and 'risk' not in analysis.lower()):
            return 'safe'
        elif 'caution' in analysis.lower() or 'risk' in analysis.lower():
            return 'caution'
        else:
            return 'review_needed'

    def _filter_safe_precedents(self, precedents: List[Dict], validity_status: Dict) -> List[Dict]:
        """Filter precedents that are safe to cite"""
        if validity_status.get('overall_validity') == 'valid':
            return precedents
        else:
            return []  # Simplified filtering

    def _suggest_alternative_authorities(self, precedents: List[Dict], validity_status: Dict) -> List[Dict]:
        """Suggest alternative authorities if primary precedents are problematic"""
        if validity_status.get('overall_validity') != 'valid':
            # In practice, this would search for alternative precedents
            return [{'suggestion': 'Search for more recent precedents in same jurisdiction'}]
        return []

    def _search_analogous_cases(self, case_facts: str, jurisdiction: str, limit: int = 8) -> List[Dict]:
        """Search for cases with analogous facts"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Extract key terms from case facts for search
        key_terms = self._extract_key_terms(case_facts)

        analogous_cases = []
        for term in key_terms[:3]:  # Use top 3 terms
            cursor.execute("""
                SELECT case_name, citation, holding, legal_issues, decision_date
                FROM case_law
                WHERE holding LIKE ? OR legal_issues LIKE ?
                ORDER BY decision_date DESC
                LIMIT ?
            """, (f"%{term}%", f"%{term}%", limit // len(key_terms[:3])))

            results = cursor.fetchall()
            analogous_cases.extend([dict(zip([col[0] for col in cursor.description], row)) for row in results])

        conn.close()
        return analogous_cases[:limit]

    def _filter_by_legal_principles(self, cases: List[Dict], legal_principles: List[str]) -> List[Dict]:
        """Filter cases by relevant legal principles"""
        filtered = []

        for case in cases:
            case_text = (case.get('holding', '') + ' ' + case.get('legal_issues', '')).lower()
            if any(principle.lower() in case_text for principle in legal_principles):
                filtered.append(case)

        return filtered

    def _calculate_similarity_scores(self, target_facts: str, cases: List[Dict]) -> Dict:
        """Calculate factual similarity scores between target case and precedents"""
        scores = {}
        target_terms = set(self._extract_key_terms(target_facts))

        for case in cases:
            case_name = case.get('case_name', '')
            case_facts = case.get('holding', '') + ' ' + case.get('legal_issues', '')
            case_terms = set(self._extract_key_terms(case_facts))

            # Simple Jaccard similarity
            intersection = len(target_terms & case_terms)
            union = len(target_terms | case_terms)
            similarity = intersection / union if union > 0 else 0

            scores[case_name] = round(similarity * 10, 1)  # Scale to 1-10

        return scores

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for similarity analysis"""
        # Simple term extraction - remove common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'was', 'are', 'were', 'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should'}

        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        key_terms = [word for word in words if word not in common_words and len(word) > 3]

        return key_terms[:10]  # Return top 10 terms

    def _identify_strongest_analogies(self, similarity_scores: Dict, analysis: str) -> List[Dict]:
        """Identify strongest factual analogies"""
        strongest = []

        # Sort by similarity score
        sorted_scores = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

        for case_name, score in sorted_scores[:3]:
            strongest.append({
                'case_name': case_name,
                'similarity_score': score,
                'analogy_strength': 'strong' if score > 7 else 'moderate' if score > 4 else 'weak'
            })

        return strongest

    def _extract_distinguishing_factors(self, analysis: str) -> List[str]:
        """Extract distinguishing factors from analysis"""
        factors = []
        lines = analysis.split('\n')

        for line in lines:
            if 'distinguish' in line.lower() or 'different' in line.lower() or 'unlike' in line.lower():
                factors.append(line.strip())

        return factors[:5]