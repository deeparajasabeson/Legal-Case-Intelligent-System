import google.generativeai as genai
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
import json
import re

class CaseAnalysisAgent:
    """AI agent for case strength assessment and legal strategy development"""

    def __init__(self):
        # Configure Gemini AI
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

        # Case analysis prompt templates
        self.analysis_prompts = {
            'case_strength': """
                You are an expert legal strategist analyzing case strength.

                Case Facts: {case_facts}
                Legal Issues: {legal_issues}
                Relevant Case Law: {case_law}
                Applicable Statutes: {statutes}
                Client Context: {client_context}

                Analyze case strength across these factors:

                1. LEGAL MERIT ANALYSIS (Score 1-10)
                   - Strength of legal claims
                   - Quality of supporting evidence
                   - Precedential support
                   - Statutory framework alignment

                2. FACTUAL STRENGTH ASSESSMENT (Score 1-10)
                   - Strength of factual foundation
                   - Evidence quality and admissibility
                   - Witness credibility potential
                   - Documentation completeness

                3. PROCEDURAL CONSIDERATIONS (Score 1-10)
                   - Jurisdiction advantages
                   - Statute of limitations compliance
                   - Venue selection benefits
                   - Procedural requirements met

                4. RISK ASSESSMENT (Score 1-10)
                   - Opposing party resources
                   - Potential counterarguments
                   - Discovery risks
                   - Cost-benefit analysis

                Provide:
                - Overall case strength score (1-10)
                - Detailed factor analysis
                - Strategic recommendations
                - Risk mitigation strategies
                - Settlement considerations
            """,

            'litigation_strategy': """
                You are a litigation strategy specialist.

                Case Analysis: {case_analysis}
                Legal Precedents: {precedents}
                Opposing Party Profile: {opposing_party}

                Develop comprehensive litigation strategy:

                1. CASE THEORY DEVELOPMENT
                   - Primary legal theory
                   - Alternative theories
                   - Narrative framework
                   - Theme development

                2. DISCOVERY STRATEGY
                   - Key documents to obtain
                   - Witness identification
                   - Expert witness needs
                   - Privileged materials protection

                3. MOTION PRACTICE STRATEGY
                   - Dispositive motions potential
                   - Procedural advantage opportunities
                   - Timing considerations
                   - Burden shifting tactics

                4. SETTLEMENT STRATEGY
                   - Settlement leverage points
                   - Negotiation timeline
                   - Alternative dispute resolution
                   - Reservation of rights

                5. TRIAL PREPARATION
                   - Evidence presentation order
                   - Witness examination strategy
                   - Jury considerations
                   - Appellate preservation

                Focus on practical, actionable strategy with ethical considerations.
            """,

            'outcome_prediction': """
                You are a legal outcome prediction specialist using historical data analysis.

                Case Profile: {case_profile}
                Similar Cases: {similar_cases}
                Jurisdiction Trends: {jurisdiction_data}
                Judge Profile: {judge_profile}

                Provide outcome prediction analysis:

                1. SUCCESS PROBABILITY ASSESSMENT
                   - Win probability percentage
                   - Confidence interval
                   - Key variables affecting outcome
                   - Historical trend analysis

                2. MONETARY OUTCOME PREDICTION
                   - Damage estimation range
                   - Settlement value assessment
                   - Cost projection
                   - ROI analysis

                3. TIMELINE PREDICTION
                   - Case duration estimate
                   - Key milestone timeline
                   - Resolution pathway probabilities
                   - Appellate likelihood

                4. STRATEGIC RECOMMENDATIONS
                   - Recommended approach
                   - Risk mitigation priorities
                   - Resource allocation guidance
                   - Decision points timeline

                Base predictions on data-driven analysis with appropriate disclaimers.
            """
        }

    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect('database/legal_data.db')

    def analyze_case_merits(self, case_facts: str, legal_issues: str, client_context: Dict = None) -> Dict:
        """Analyze case merits and provide strength assessment"""
        try:
            # Get relevant legal authority
            case_law = self._get_relevant_case_law(legal_issues)
            statutes = self._get_relevant_statutes(legal_issues)

            # Prepare analysis context
            analysis_context = {
                'case_facts': case_facts,
                'legal_issues': legal_issues,
                'case_law': json.dumps(case_law, indent=2),
                'statutes': json.dumps(statutes, indent=2),
                'client_context': json.dumps(client_context or {}, indent=2)
            }

            # Generate case strength analysis
            prompt = self.analysis_prompts['case_strength'].format(**analysis_context)
            response = self.model.generate_content(prompt)
            strength_analysis = response.text

            # Extract numerical scores using regex
            scores = self._extract_scores(strength_analysis)

            return {
                'case_facts': case_facts,
                'legal_issues': legal_issues,
                'strength_analysis': strength_analysis,
                'strength_scores': scores,
                'supporting_authority': {
                    'case_law': case_law,
                    'statutes': statutes
                },
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'overall_strength': scores.get('overall', 5.0)
            }

        except Exception as e:
            return {
                'error': f"Case analysis failed: {str(e)}",
                'case_facts': case_facts,
                'legal_issues': legal_issues
            }

    def develop_litigation_strategy(self, case_analysis: Dict, opposing_party: str = None) -> Dict:
        """Develop comprehensive litigation strategy"""
        try:
            # Get relevant precedents for strategy development
            precedents = self._get_strategic_precedents(case_analysis.get('legal_issues', ''))

            # Generate litigation strategy
            strategy_context = {
                'case_analysis': json.dumps(case_analysis, indent=2),
                'precedents': json.dumps(precedents, indent=2),
                'opposing_party': opposing_party or 'Unknown'
            }

            prompt = self.analysis_prompts['litigation_strategy'].format(**strategy_context)
            response = self.model.generate_content(prompt)
            strategy_analysis = response.text

            return {
                'case_id': case_analysis.get('case_id'),
                'litigation_strategy': strategy_analysis,
                'strategic_precedents': precedents,
                'case_theory': self._extract_case_theory(strategy_analysis),
                'discovery_priorities': self._extract_discovery_priorities(strategy_analysis),
                'settlement_considerations': self._extract_settlement_factors(strategy_analysis),
                'strategy_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Strategy development failed: {str(e)}",
                'case_analysis': case_analysis
            }

    def predict_case_outcome(self, case_profile: Dict, jurisdiction: str = "Federal") -> Dict:
        """Predict case outcome based on historical data and analysis"""
        try:
            # Find similar cases for comparison
            similar_cases = self._find_similar_cases(case_profile, jurisdiction)

            # Get jurisdiction-specific data
            jurisdiction_trends = self._get_jurisdiction_trends(jurisdiction)

            # Generate outcome prediction
            prediction_context = {
                'case_profile': json.dumps(case_profile, indent=2),
                'similar_cases': json.dumps(similar_cases, indent=2),
                'jurisdiction_data': json.dumps(jurisdiction_trends, indent=2),
                'judge_profile': 'General jurisdiction profile'  # Placeholder
            }

            prompt = self.analysis_prompts['outcome_prediction'].format(**prediction_context)
            response = self.model.generate_content(prompt)
            prediction_analysis = response.text

            # Extract prediction metrics
            success_probability = self._extract_probability(prediction_analysis)
            timeline_estimate = self._extract_timeline(prediction_analysis)

            return {
                'case_profile': case_profile,
                'outcome_prediction': prediction_analysis,
                'success_probability': success_probability,
                'timeline_estimate': timeline_estimate,
                'similar_cases_count': len(similar_cases),
                'jurisdiction': jurisdiction,
                'prediction_timestamp': datetime.utcnow().isoformat(),
                'confidence_level': self._calculate_confidence(similar_cases, case_profile)
            }

        except Exception as e:
            return {
                'error': f"Outcome prediction failed: {str(e)}",
                'case_profile': case_profile
            }

    def _get_relevant_case_law(self, legal_issues: str, limit: int = 5) -> List[Dict]:
        """Get case law relevant to legal issues"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT case_name, court, citation, holding, legal_issues
            FROM case_law
            WHERE legal_issues LIKE ? OR holding LIKE ?
            ORDER BY decision_date DESC
            LIMIT ?
        """, (f"%{legal_issues}%", f"%{legal_issues}%", limit))

        results = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def _get_relevant_statutes(self, legal_issues: str, limit: int = 3) -> List[Dict]:
        """Get statutes relevant to legal issues"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT statute_title, code_section, statute_text, legal_area
            FROM statutes
            WHERE statute_text LIKE ? OR legal_area LIKE ?
            ORDER BY effective_date DESC
            LIMIT ?
        """, (f"%{legal_issues}%", f"%{legal_issues}%", limit))

        results = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def _get_strategic_precedents(self, legal_issues: str, limit: int = 5) -> List[Dict]:
        """Get precedents for strategic development"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.legal_principle, p.binding_authority, p.precedent_weight,
                   c.case_name, c.citation
            FROM legal_precedents p
            JOIN case_law c ON p.case_id = c.case_id
            WHERE p.legal_principle LIKE ?
            ORDER BY p.precedent_weight DESC
            LIMIT ?
        """, (f"%{legal_issues}%", limit))

        results = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def _find_similar_cases(self, case_profile: Dict, jurisdiction: str, limit: int = 5) -> List[Dict]:
        """Find similar cases for outcome prediction"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Simple similarity based on legal issues
        legal_issues = case_profile.get('legal_issues', '')

        cursor.execute("""
            SELECT case_name, legal_issues, holding, decision_date
            FROM case_law
            WHERE legal_issues LIKE ? AND jurisdiction = ?
            ORDER BY decision_date DESC
            LIMIT ?
        """, (f"%{legal_issues}%", jurisdiction, limit))

        results = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def _get_jurisdiction_trends(self, jurisdiction: str) -> Dict:
        """Get jurisdiction-specific trends and statistics"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) as case_count, AVG(precedent_weight) as avg_weight
            FROM legal_precedents
            WHERE jurisdiction = ?
        """, (jurisdiction,))

        result = cursor.fetchone()
        conn.close()

        return {
            'total_cases': result[0] if result else 0,
            'average_precedent_weight': result[1] if result and result[1] else 5.0,
            'jurisdiction': jurisdiction
        }

    def _extract_scores(self, analysis_text: str) -> Dict:
        """Extract numerical scores from analysis text"""
        scores = {}

        # Extract overall score
        overall_match = re.search(r'overall.*?score.*?(\d+(?:\.\d+)?)', analysis_text, re.IGNORECASE)
        if overall_match:
            scores['overall'] = float(overall_match.group(1))

        # Extract individual factor scores
        for factor in ['legal', 'factual', 'procedural', 'risk']:
            pattern = rf'{factor}.*?score.*?(\d+(?:\.\d+)?)'
            match = re.search(pattern, analysis_text, re.IGNORECASE)
            if match:
                scores[factor] = float(match.group(1))

        return scores

    def _extract_probability(self, prediction_text: str) -> float:
        """Extract success probability from prediction text"""
        prob_match = re.search(r'(\d+(?:\.\d+)?)%', prediction_text)
        return float(prob_match.group(1)) / 100 if prob_match else 0.5

    def _extract_timeline(self, prediction_text: str) -> str:
        """Extract timeline estimate from prediction text"""
        timeline_match = re.search(r'(\d+-\d+ months?|\d+ months?|\d+-\d+ years?)', prediction_text, re.IGNORECASE)
        return timeline_match.group(1) if timeline_match else "6-12 months"

    def _extract_case_theory(self, strategy_text: str) -> str:
        """Extract primary case theory from strategy text"""
        theory_match = re.search(r'primary legal theory:?\s*([^\n]+)', strategy_text, re.IGNORECASE)
        return theory_match.group(1).strip() if theory_match else "To be developed"

    def _extract_discovery_priorities(self, strategy_text: str) -> List[str]:
        """Extract discovery priorities from strategy text"""
        # Simple extraction of bullet points or numbered items
        priorities = []
        lines = strategy_text.split('\n')
        in_discovery_section = False

        for line in lines:
            if 'discovery' in line.lower() and 'strategy' in line.lower():
                in_discovery_section = True
                continue
            elif in_discovery_section and line.strip():
                if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line.strip()):
                    priorities.append(line.strip().lstrip('- *•0123456789. '))
                elif line.strip().isupper() or re.match(r'^\d+\.', line.strip()):
                    break

        return priorities[:5]  # Return top 5 priorities

    def _extract_settlement_factors(self, strategy_text: str) -> List[str]:
        """Extract settlement considerations from strategy text"""
        factors = []
        lines = strategy_text.split('\n')
        in_settlement_section = False

        for line in lines:
            if 'settlement' in line.lower() and ('strategy' in line.lower() or 'consideration' in line.lower()):
                in_settlement_section = True
                continue
            elif in_settlement_section and line.strip():
                if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line.strip()):
                    factors.append(line.strip().lstrip('- *•0123456789. '))
                elif line.strip().isupper():
                    break

        return factors[:5]

    def _calculate_confidence(self, similar_cases: List[Dict], case_profile: Dict) -> float:
        """Calculate confidence level based on available similar cases"""
        if not similar_cases:
            return 0.3

        # Simple confidence calculation based on number of similar cases
        confidence = min(0.9, 0.4 + (len(similar_cases) * 0.1))
        return round(confidence, 2)