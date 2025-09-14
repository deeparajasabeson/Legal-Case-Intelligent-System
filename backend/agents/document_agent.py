import google.generativeai as genai
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import re

class DocumentReviewAgent:
    """AI agent for legal document review and contract analysis"""

    def __init__(self):
        # Configure Gemini AI
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

        # Document analysis templates
        self.analysis_prompts = {
            'contract_review': """
                You are an expert contract review attorney analyzing a legal document.

                Document Type: {document_type}
                Document Text: {document_text}
                Standard Contract Templates: {templates}
                Review Purpose: {review_purpose}

                Provide comprehensive contract analysis:

                1. DOCUMENT OVERVIEW
                   - Contract type and purpose
                   - Parties identification
                   - Key terms summary
                   - Effective dates and duration

                2. LEGAL COMPLIANCE ANALYSIS (Score 1-10)
                   - Regulatory compliance assessment
                   - Legal requirement adherence
                   - Statutory compliance verification
                   - Industry standard alignment

                3. RISK ASSESSMENT (Score 1-10)
                   - High-risk provisions identification
                   - Liability exposure analysis
                   - Indemnification risks
                   - Termination and breach consequences

                4. ENFORCEABILITY ANALYSIS (Score 1-10)
                   - Legal enforceability probability
                   - Potential enforceability challenges
                   - Jurisdiction and governing law issues
                   - Dispute resolution mechanisms

                5. OBLIGATION ANALYSIS
                   - Client obligations and responsibilities
                   - Counterparty obligations
                   - Performance standards and metrics
                   - Compliance requirements

                6. RECOMMENDATIONS
                   - Suggested modifications
                   - Risk mitigation strategies
                   - Negotiation priorities
                   - Alternative clause suggestions

                Focus on practical, actionable insights with specific clause references.
            """,

            'clause_analysis': """
                You are a contract clause specialist analyzing specific provisions.

                Clause Text: {clause_text}
                Clause Type: {clause_type}
                Contract Context: {contract_context}
                Standard Clauses: {standard_clauses}

                Provide detailed clause analysis:

                1. CLAUSE INTERPRETATION
                   - Plain language meaning
                   - Legal implications
                   - Ambiguity identification
                   - Intent determination

                2. RISK EVALUATION
                   - Client risk exposure
                   - Counterparty advantages
                   - Enforcement challenges
                   - Unintended consequences

                3. MARKET COMPARISON
                   - Industry standard comparison
                   - Negotiation positioning
                   - Alternative formulations
                   - Best practice recommendations

                4. IMPROVEMENT SUGGESTIONS
                   - Specific language modifications
                   - Additional protective provisions
                   - Clarification opportunities
                   - Risk mitigation enhancements

                Provide specific, actionable recommendations with exact language suggestions.
            """,

            'compliance_review': """
                You are a regulatory compliance specialist reviewing legal documents.

                Document: {document_text}
                Industry/Sector: {industry}
                Applicable Regulations: {regulations}
                Compliance Requirements: {compliance_reqs}

                Conduct comprehensive compliance review:

                1. REGULATORY COMPLIANCE ASSESSMENT
                   - Applicable law identification
                   - Compliance requirement mapping
                   - Regulatory gap analysis
                   - Industry standard adherence

                2. COMPLIANCE RISK EVALUATION (Score 1-10)
                   - Regulatory violation risks
                   - Enforcement action likelihood
                   - Penalty exposure assessment
                   - Reputational risk factors

                3. REQUIRED MODIFICATIONS
                   - Mandatory compliance updates
                   - Recommended safety provisions
                   - Regulatory filing requirements
                   - Documentation improvements

                4. ONGOING COMPLIANCE REQUIREMENTS
                   - Monitoring obligations
                   - Reporting requirements
                   - Review and update schedules
                   - Training and implementation needs

                Focus on specific compliance gaps and actionable remediation steps.
            """
        }

        # Document type configurations
        self.document_types = {
            'employment': {
                'key_clauses': ['compensation', 'termination', 'confidentiality', 'non-compete', 'benefits'],
                'risk_areas': ['discrimination', 'wage compliance', 'termination procedures'],
                'compliance_areas': ['FLSA', 'ADA', 'Title VII']
            },
            'service': {
                'key_clauses': ['scope of work', 'payment terms', 'intellectual property', 'liability', 'termination'],
                'risk_areas': ['service level compliance', 'IP ownership', 'liability caps'],
                'compliance_areas': ['consumer protection', 'data privacy', 'professional licensing']
            },
            'nda': {
                'key_clauses': ['confidential information definition', 'use restrictions', 'return of materials', 'duration'],
                'risk_areas': ['overly broad definitions', 'enforcement challenges', 'reciprocity issues'],
                'compliance_areas': ['trade secret law', 'employment restrictions']
            },
            'purchase': {
                'key_clauses': ['purchase price', 'delivery terms', 'warranties', 'risk of loss', 'remedies'],
                'risk_areas': ['title issues', 'warranty limitations', 'payment risks'],
                'compliance_areas': ['UCC', 'consumer protection', 'international trade']
            }
        }

    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect('database/legal_data.db')

    def review_document(self, document_text: str, document_type: str, attorney_id: str = None, review_purpose: str = "general") -> Dict:
        """Conduct comprehensive document review"""
        try:
            # Get relevant contract templates for comparison
            templates = self._get_contract_templates(document_type)

            # Prepare analysis context
            analysis_context = {
                'document_type': document_type,
                'document_text': document_text,
                'templates': json.dumps(templates, indent=2),
                'review_purpose': review_purpose
            }

            # Generate comprehensive review
            prompt = self.analysis_prompts['contract_review'].format(**analysis_context)
            response = self.model.generate_content(prompt)
            review_analysis = response.text

            # Extract key clauses
            key_clauses = self._extract_key_clauses(document_text, document_type)

            # Assess risks
            risk_assessment = self._assess_document_risks(document_text, document_type)

            # Calculate scores
            scores = self._extract_scores(review_analysis)

            return {
                'document_type': document_type,
                'review_analysis': review_analysis,
                'key_clauses': key_clauses,
                'risk_assessment': risk_assessment,
                'compliance_score': scores.get('compliance', 7.0),
                'risk_score': scores.get('risk', 5.0),
                'enforceability_score': scores.get('enforceability', 7.0),
                'overall_score': self._calculate_overall_score(scores),
                'recommendations': self._extract_recommendations(review_analysis),
                'red_flags': self._identify_red_flags(document_text, review_analysis),
                'attorney_id': attorney_id,
                'review_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Document review failed: {str(e)}",
                'document_type': document_type
            }

    def analyze_specific_clause(self, clause_text: str, clause_type: str, contract_context: str = "") -> Dict:
        """Analyze specific contract clause in detail"""
        try:
            # Get standard clauses for comparison
            standard_clauses = self._get_standard_clauses(clause_type)

            # Prepare clause analysis context
            clause_context = {
                'clause_text': clause_text,
                'clause_type': clause_type,
                'contract_context': contract_context,
                'standard_clauses': json.dumps(standard_clauses, indent=2)
            }

            # Generate clause analysis
            prompt = self.analysis_prompts['clause_analysis'].format(**clause_context)
            response = self.model.generate_content(prompt)
            clause_analysis = response.text

            # Evaluate clause strength
            strength_score = self._evaluate_clause_strength(clause_text, clause_type)

            return {
                'clause_text': clause_text,
                'clause_type': clause_type,
                'clause_analysis': clause_analysis,
                'strength_score': strength_score,
                'risk_level': self._assess_clause_risk(clause_text, clause_analysis),
                'improvements': self._extract_improvements(clause_analysis),
                'alternative_language': self._suggest_alternatives(clause_analysis),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Clause analysis failed: {str(e)}",
                'clause_type': clause_type
            }

    def compliance_review(self, document_text: str, industry: str, regulations: List[str] = None) -> Dict:
        """Conduct regulatory compliance review"""
        try:
            # Get applicable regulations
            if not regulations:
                regulations = self._get_applicable_regulations(industry)

            # Build compliance requirements
            compliance_reqs = self._build_compliance_requirements(industry, regulations)

            # Prepare compliance analysis context
            compliance_context = {
                'document_text': document_text,
                'industry': industry,
                'regulations': json.dumps(regulations, indent=2),
                'compliance_reqs': json.dumps(compliance_reqs, indent=2)
            }

            # Generate compliance review
            prompt = self.analysis_prompts['compliance_review'].format(**compliance_context)
            response = self.model.generate_content(prompt)
            compliance_analysis = response.text

            # Extract compliance score
            compliance_score = self._extract_compliance_score(compliance_analysis)

            # Identify compliance gaps
            compliance_gaps = self._identify_compliance_gaps(compliance_analysis)

            return {
                'industry': industry,
                'applicable_regulations': regulations,
                'compliance_analysis': compliance_analysis,
                'compliance_score': compliance_score,
                'compliance_gaps': compliance_gaps,
                'required_modifications': self._extract_required_modifications(compliance_analysis),
                'compliance_risks': self._assess_compliance_risks(compliance_analysis),
                'remediation_timeline': self._suggest_remediation_timeline(compliance_gaps),
                'review_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Compliance review failed: {str(e)}",
                'industry': industry
            }

    def _get_contract_templates(self, document_type: str, limit: int = 3) -> List[Dict]:
        """Get contract templates for comparison"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT contract_type, contract_name, standard_clauses, risk_factors
            FROM contracts
            WHERE contract_type LIKE ?
            LIMIT ?
        """, (f"%{document_type}%", limit))

        results = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def _extract_key_clauses(self, document_text: str, document_type: str) -> List[Dict]:
        """Extract and identify key clauses from document"""
        key_clauses = []

        if document_type.lower() in self.document_types:
            expected_clauses = self.document_types[document_type.lower()]['key_clauses']

            for clause_type in expected_clauses:
                # Simple pattern matching for clause identification
                patterns = [
                    rf'{clause_type}[:\s]+(.*?)(?:\n\n|\n[A-Z]|\Z)',
                    rf'(?:^|\n)\s*\d+\.?\s*{clause_type}[:\s]+(.*?)(?:\n\n|\n\d+\.|\Z)',
                ]

                for pattern in patterns:
                    matches = re.finditer(pattern, document_text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    for match in matches:
                        key_clauses.append({
                            'clause_type': clause_type,
                            'clause_text': match.group(1).strip()[:500],  # Limit length
                            'position': match.start()
                        })
                        break  # Take first match for each clause type

        return key_clauses

    def _assess_document_risks(self, document_text: str, document_type: str) -> Dict:
        """Assess risks in the document"""
        risk_factors = {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': []
        }

        if document_type.lower() in self.document_types:
            risk_areas = self.document_types[document_type.lower()]['risk_areas']

            for risk_area in risk_areas:
                if risk_area.lower() in document_text.lower():
                    # Simple risk classification - in practice, this would be more sophisticated
                    if 'unlimited' in document_text.lower() or 'sole discretion' in document_text.lower():
                        risk_factors['high_risk'].append(risk_area)
                    elif 'reasonable' in document_text.lower() or 'material' in document_text.lower():
                        risk_factors['medium_risk'].append(risk_area)
                    else:
                        risk_factors['low_risk'].append(risk_area)

        return risk_factors

    def _extract_scores(self, analysis_text: str) -> Dict:
        """Extract numerical scores from analysis"""
        scores = {}

        # Extract different types of scores
        score_types = ['compliance', 'risk', 'enforceability', 'legal', 'overall']

        for score_type in score_types:
            pattern = rf'{score_type}.*?score.*?(\d+(?:\.\d+)?)'
            match = re.search(pattern, analysis_text, re.IGNORECASE)
            if match:
                scores[score_type] = float(match.group(1))

        return scores

    def _calculate_overall_score(self, scores: Dict) -> float:
        """Calculate overall document score"""
        if not scores:
            return 6.0

        # Weighted average of available scores
        weights = {
            'compliance': 0.3,
            'risk': 0.3,
            'enforceability': 0.2,
            'legal': 0.2
        }

        total_score = 0
        total_weight = 0

        for score_type, weight in weights.items():
            if score_type in scores:
                total_score += scores[score_type] * weight
                total_weight += weight

        return round(total_score / total_weight if total_weight > 0 else 6.0, 1)

    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract recommendations from analysis"""
        recommendations = []
        lines = analysis_text.split('\n')
        in_recommendations = False

        for line in lines:
            if 'recommendation' in line.lower():
                in_recommendations = True
                continue
            elif in_recommendations and line.strip():
                if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line.strip()):
                    recommendations.append(line.strip().lstrip('- *•0123456789. '))
                elif line.strip().isupper():
                    break

        return recommendations[:10]  # Limit to top 10

    def _identify_red_flags(self, document_text: str, analysis_text: str) -> List[str]:
        """Identify potential red flags in the document"""
        red_flags = []

        # Common red flag patterns
        red_flag_patterns = [
            'unlimited liability',
            'sole discretion',
            'perpetual',
            'irrevocable',
            'personal guarantee',
            'liquidated damages'
        ]

        for pattern in red_flag_patterns:
            if pattern in document_text.lower():
                red_flags.append(f"Contains {pattern} clause")

        # Extract red flags mentioned in analysis
        if 'red flag' in analysis_text.lower() or 'concern' in analysis_text.lower():
            # Simple extraction - could be enhanced
            concern_sentences = [
                sentence.strip() for sentence in analysis_text.split('.')
                if 'concern' in sentence.lower() or 'red flag' in sentence.lower()
            ]
            red_flags.extend(concern_sentences[:5])

        return red_flags

    def _get_standard_clauses(self, clause_type: str, limit: int = 3) -> List[Dict]:
        """Get standard clauses for comparison"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT contract_type, standard_clauses
            FROM contracts
            WHERE standard_clauses LIKE ?
            LIMIT ?
        """, (f"%{clause_type}%", limit))

        results = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def _evaluate_clause_strength(self, clause_text: str, clause_type: str) -> float:
        """Evaluate strength of specific clause"""
        # Simple scoring based on presence of key terms
        strength_indicators = {
            'reasonable': 0.2,
            'material': 0.2,
            'written notice': 0.3,
            'cure period': 0.3,
            'mutual': 0.2
        }

        weakness_indicators = {
            'sole discretion': -0.4,
            'unlimited': -0.5,
            'waive': -0.3,
            'as is': -0.2
        }

        base_score = 6.0
        clause_lower = clause_text.lower()

        for indicator, value in strength_indicators.items():
            if indicator in clause_lower:
                base_score += value

        for indicator, value in weakness_indicators.items():
            if indicator in clause_lower:
                base_score += value

        return max(1.0, min(10.0, base_score))

    def _assess_clause_risk(self, clause_text: str, analysis_text: str) -> str:
        """Assess risk level of clause"""
        if 'high risk' in analysis_text.lower() or 'significant concern' in analysis_text.lower():
            return 'high'
        elif 'medium risk' in analysis_text.lower() or 'moderate concern' in analysis_text.lower():
            return 'medium'
        else:
            return 'low'

    def _extract_improvements(self, analysis_text: str) -> List[str]:
        """Extract improvement suggestions"""
        improvements = []
        lines = analysis_text.split('\n')
        in_improvements = False

        for line in lines:
            if 'improvement' in line.lower() or 'suggestion' in line.lower():
                in_improvements = True
                continue
            elif in_improvements and line.strip():
                if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line.strip()):
                    improvements.append(line.strip().lstrip('- *•0123456789. '))
                elif line.strip().isupper():
                    break

        return improvements[:5]

    def _suggest_alternatives(self, analysis_text: str) -> List[str]:
        """Extract alternative language suggestions"""
        alternatives = []

        # Look for quoted text that might be alternative language
        quote_pattern = r'"([^"]{20,200})"'
        matches = re.findall(quote_pattern, analysis_text)
        alternatives.extend(matches[:3])

        return alternatives

    def _get_applicable_regulations(self, industry: str) -> List[str]:
        """Get applicable regulations for industry"""
        regulation_map = {
            'employment': ['FLSA', 'ADA', 'Title VII', 'FMLA'],
            'healthcare': ['HIPAA', 'HITECH', 'FDA', 'ACA'],
            'financial': ['SOX', 'GDPR', 'PCI DSS', 'CCPA'],
            'technology': ['GDPR', 'CCPA', 'COPPA', 'CAN-SPAM'],
            'general': ['UCC', 'FTC Act', 'Consumer Protection']
        }

        return regulation_map.get(industry.lower(), regulation_map['general'])

    def _build_compliance_requirements(self, industry: str, regulations: List[str]) -> Dict:
        """Build compliance requirements for industry and regulations"""
        # Simplified compliance requirements mapping
        return {
            'data_protection': 'GDPR' in regulations or 'CCPA' in regulations,
            'employment_law': 'FLSA' in regulations or industry.lower() == 'employment',
            'consumer_protection': 'FTC Act' in regulations,
            'financial_compliance': 'SOX' in regulations or industry.lower() == 'financial'
        }

    def _extract_compliance_score(self, analysis_text: str) -> float:
        """Extract compliance score from analysis"""
        score_match = re.search(r'compliance.*?score.*?(\d+(?:\.\d+)?)', analysis_text, re.IGNORECASE)
        return float(score_match.group(1)) if score_match else 7.0

    def _identify_compliance_gaps(self, analysis_text: str) -> List[str]:
        """Identify compliance gaps from analysis"""
        gaps = []
        lines = analysis_text.split('\n')

        for line in lines:
            if any(word in line.lower() for word in ['gap', 'missing', 'required', 'must add']):
                gaps.append(line.strip())

        return gaps[:5]

    def _extract_required_modifications(self, analysis_text: str) -> List[str]:
        """Extract required modifications"""
        modifications = []
        lines = analysis_text.split('\n')
        in_modifications = False

        for line in lines:
            if 'modification' in line.lower() or 'required' in line.lower():
                in_modifications = True
                continue
            elif in_modifications and line.strip():
                if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line.strip()):
                    modifications.append(line.strip().lstrip('- *•0123456789. '))
                elif line.strip().isupper():
                    break

        return modifications[:5]

    def _assess_compliance_risks(self, analysis_text: str) -> Dict:
        """Assess compliance risks"""
        risks = {'high': [], 'medium': [], 'low': []}

        # Simple risk assessment based on keywords
        if 'violation' in analysis_text.lower():
            risks['high'].append('Regulatory violation risk')
        if 'penalty' in analysis_text.lower():
            risks['medium'].append('Penalty exposure')
        if 'update' in analysis_text.lower():
            risks['low'].append('Documentation updates needed')

        return risks

    def _suggest_remediation_timeline(self, compliance_gaps: List[str]) -> str:
        """Suggest timeline for compliance remediation"""
        if not compliance_gaps:
            return "No immediate action required"
        elif len(compliance_gaps) > 5:
            return "30-60 days for comprehensive compliance review"
        else:
            return "15-30 days for gap remediation"