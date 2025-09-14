import google.generativeai as genai
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
import json

class LegalResearchAgent:
    """AI agent for conducting comprehensive legal research"""

    def __init__(self):
        # Configure Gemini AI
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

        # Legal research prompt templates
        self.research_prompts = {
            'case_law': """
                You are a legal research specialist focusing on case law analysis.

                Query: {query}
                Jurisdiction: {jurisdiction}

                Based on the provided case law database results: {case_data}

                Provide comprehensive analysis including:
                1. Key legal principles and holdings
                2. Relevant precedential authority
                3. Analysis of applicability to current legal issue
                4. Strategic implications and recommendations
                5. Proper legal citations in Bluebook format

                Include appropriate legal disclaimers and maintain attorney-client privilege.
                Focus on practical legal application and strategic value.
            """,

            'statutory': """
                You are a statutory research and interpretation specialist.

                Query: {query}
                Jurisdiction: {jurisdiction}

                Based on the statutory database results: {statute_data}

                Provide analysis covering:
                1. Relevant statutory provisions and interpretations
                2. Regulatory framework and compliance requirements
                3. Potential legal arguments and statutory construction
                4. Enforcement mechanisms and penalties
                5. Recent amendments or proposed changes

                Include proper statutory citations and regulatory references.
                Focus on compliance strategies and risk mitigation.
            """,

            'comprehensive': """
                You are a comprehensive legal research specialist.

                Attorney Query: "{query}" in {jurisdiction}

                Case Law Results: {case_data}
                Statutory Authority: {statute_data}
                Legal Precedents: {precedent_data}

                Provide thorough legal analysis including:
                1. Executive Summary of Legal Position
                2. Controlling Case Law with Citations
                3. Applicable Statutory Framework
                4. Precedential Analysis and Authority
                5. Legal Arguments and Counterarguments
                6. Strategic Recommendations
                7. Risk Assessment and Mitigation
                8. Next Steps and Research Priorities

                Use proper legal citation format (Bluebook).
                Include ethical disclaimers and attorney-client privilege protection.
                Focus on actionable legal insights and strategic value.
            """
        }

    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect('database/legal_data.db')

    def search_case_law(self, query: str, jurisdiction: str = None) -> List[Dict]:
        """Search case law database for relevant cases"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Build search query
        sql = """
            SELECT case_id, case_name, court, jurisdiction, decision_date,
                   legal_issues, holding, citation, legal_area
            FROM case_law
            WHERE legal_issues LIKE ? OR holding LIKE ? OR case_name LIKE ?
        """

        params = [f"%{query}%", f"%{query}%", f"%{query}%"]

        if jurisdiction:
            sql += " AND jurisdiction = ?"
            params.append(jurisdiction)

        sql += " ORDER BY decision_date DESC LIMIT 10"

        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()

        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def search_statutes(self, query: str, jurisdiction: str = None) -> List[Dict]:
        """Search statutory database for relevant statutes"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT statute_id, statute_title, code_section, jurisdiction,
                   statute_text, legal_area, effective_date
            FROM statutes
            WHERE statute_title LIKE ? OR statute_text LIKE ? OR legal_area LIKE ?
        """

        params = [f"%{query}%", f"%{query}%", f"%{query}%"]

        if jurisdiction:
            sql += " AND jurisdiction = ?"
            params.append(jurisdiction)

        sql += " ORDER BY effective_date DESC LIMIT 10"

        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()

        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def search_precedents(self, query: str, jurisdiction: str = None) -> List[Dict]:
        """Search legal precedents database"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        sql = """
            SELECT p.precedent_id, p.legal_principle, p.binding_authority,
                   p.jurisdiction, p.precedent_weight, p.related_statutes,
                   c.case_name, c.citation
            FROM legal_precedents p
            JOIN case_law c ON p.case_id = c.case_id
            WHERE p.legal_principle LIKE ? OR p.related_statutes LIKE ?
        """

        params = [f"%{query}%", f"%{query}%"]

        if jurisdiction:
            sql += " AND p.jurisdiction = ?"
            params.append(jurisdiction)

        sql += " ORDER BY p.precedent_weight DESC LIMIT 10"

        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()

        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]

    def conduct_research(self, query: str, jurisdiction: str = "Federal", attorney_id: str = None) -> Dict:
        """Conduct comprehensive legal research using AI analysis"""
        try:
            # Search legal databases
            case_results = self.search_case_law(query, jurisdiction)
            statute_results = self.search_statutes(query, jurisdiction)
            precedent_results = self.search_precedents(query, jurisdiction)

            # Prepare data for AI analysis
            research_data = {
                'case_law': case_results,
                'statutes': statute_results,
                'precedents': precedent_results
            }

            # Generate AI analysis using comprehensive prompt
            prompt = self.research_prompts['comprehensive'].format(
                query=query,
                jurisdiction=jurisdiction,
                case_data=json.dumps(case_results, indent=2),
                statute_data=json.dumps(statute_results, indent=2),
                precedent_data=json.dumps(precedent_results, indent=2)
            )

            # Get AI analysis
            response = self.model.generate_content(prompt)
            ai_analysis = response.text

            # Store research in history
            if attorney_id:
                self._store_research_history(attorney_id, query, jurisdiction, research_data)

            return {
                'query': query,
                'jurisdiction': jurisdiction,
                'raw_data': research_data,
                'ai_analysis': ai_analysis,
                'case_count': len(case_results),
                'statute_count': len(statute_results),
                'precedent_count': len(precedent_results),
                'research_timestamp': datetime.utcnow().isoformat(),
                'attorney_id': attorney_id
            }

        except Exception as e:
            return {
                'error': f"Research failed: {str(e)}",
                'query': query,
                'jurisdiction': jurisdiction
            }

    def analyze_legal_issue(self, legal_issue: str, case_facts: str, jurisdiction: str = "Federal") -> Dict:
        """Analyze specific legal issue with contextual case facts"""
        try:
            # Enhanced search with case facts context
            combined_query = f"{legal_issue} {case_facts}"

            # Conduct research
            research_results = self.conduct_research(combined_query, jurisdiction)

            if 'error' in research_results:
                return research_results

            # Generate issue-specific analysis
            issue_prompt = f"""
                Legal Issue Analysis Request:

                Legal Issue: {legal_issue}
                Case Facts: {case_facts}
                Jurisdiction: {jurisdiction}

                Research Results: {research_results['ai_analysis']}

                Provide focused analysis:
                1. Issue Identification and Legal Framework
                2. Applicable Law and Controlling Authority
                3. Analysis of Case Facts Under Relevant Law
                4. Strength of Legal Position (Scale 1-10)
                5. Potential Challenges and Counterarguments
                6. Recommended Legal Strategy
                7. Additional Research Needed

                Provide practical, actionable legal guidance with proper citations.
            """

            response = self.model.generate_content(issue_prompt)
            issue_analysis = response.text

            return {
                'legal_issue': legal_issue,
                'case_facts': case_facts,
                'jurisdiction': jurisdiction,
                'research_foundation': research_results,
                'issue_analysis': issue_analysis,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Legal issue analysis failed: {str(e)}",
                'legal_issue': legal_issue
            }

    def _store_research_history(self, attorney_id: str, query: str, jurisdiction: str, results: Dict):
        """Store research history for future reference"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO research_history (research_id, attorney_id, query, jurisdiction, research_results)
            VALUES (?, ?, ?, ?, ?)
        """, (
            f"res_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{attorney_id}",
            attorney_id,
            query,
            jurisdiction,
            json.dumps(results)
        ))

        conn.commit()
        conn.close()

    def get_research_history(self, attorney_id: str, limit: int = 10) -> List[Dict]:
        """Get attorney's research history"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT research_id, query, jurisdiction, timestamp
            FROM research_history
            WHERE attorney_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (attorney_id, limit))

        results = cursor.fetchall()
        conn.close()

        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]