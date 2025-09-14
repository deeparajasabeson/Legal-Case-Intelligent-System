#!/usr/bin/env python3
"""
Legal AI System Integration Tests
Tests core functionality and compliance features
"""

import unittest
import json
import sqlite3
from pathlib import Path
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.research_agent import LegalResearchAgent
from agents.case_agent import CaseAnalysisAgent
from agents.document_agent import DocumentReviewAgent
from agents.precedent_agent import PrecedentMiningAgent
from utils.privilege_protection import AttorneyClientPrivilege
from utils.ethics_compliance import LegalEthicsManager
from utils.rag_system import LegalRAGSystem

class TestLegalAISystem(unittest.TestCase):
    """Test suite for Legal AI system components"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_db = "database/test_legal_data.db"
        cls.setup_test_database()

        # Initialize agents
        cls.research_agent = LegalResearchAgent()
        cls.case_agent = CaseAnalysisAgent()
        cls.document_agent = DocumentReviewAgent()
        cls.precedent_agent = PrecedentMiningAgent()
        cls.privilege_system = AttorneyClientPrivilege()
        cls.ethics_manager = LegalEthicsManager()
        cls.rag_system = LegalRAGSystem()

    @classmethod
    def setup_test_database(cls):
        """Set up test database with sample data"""
        # Use main database for testing
        pass

    def test_legal_research_agent(self):
        """Test legal research functionality"""
        query = "breach of contract damages"
        jurisdiction = "California"
        attorney_id = "att_001"

        try:
            results = self.research_agent.conduct_research(
                query=query,
                jurisdiction=jurisdiction,
                attorney_id=attorney_id
            )

            self.assertIsInstance(results, dict)
            self.assertIn("research_summary", results)
            self.assertIn("relevant_cases", results)
            self.assertIn("applicable_statutes", results)
            print("✅ Legal Research Agent: PASSED")

        except Exception as e:
            print(f"❌ Legal Research Agent: FAILED - {e}")
            self.fail(f"Legal research failed: {e}")

    def test_case_analysis_agent(self):
        """Test case analysis functionality"""
        case_facts = "Contract dispute over software licensing agreement"
        legal_issues = "Breach of contract, damages calculation"
        client_context = {"client_id": "CLIENT_001", "privilege_level": "high"}

        try:
            analysis = self.case_agent.analyze_case_merits(
                case_facts=case_facts,
                legal_issues=legal_issues,
                client_context=client_context
            )

            self.assertIsInstance(analysis, dict)
            self.assertIn("case_strength", analysis)
            self.assertIn("legal_strategy", analysis)
            self.assertIn("risk_assessment", analysis)
            print("✅ Case Analysis Agent: PASSED")

        except Exception as e:
            print(f"❌ Case Analysis Agent: FAILED - {e}")
            self.fail(f"Case analysis failed: {e}")

    def test_document_review_agent(self):
        """Test document review functionality"""
        document_text = "This Software License Agreement governs the use of proprietary software..."
        document_type = "license"
        attorney_id = "att_001"

        try:
            review = self.document_agent.review_document(
                document_text=document_text,
                document_type=document_type,
                attorney_id=attorney_id
            )

            self.assertIsInstance(review, dict)
            self.assertIn("document_analysis", review)
            self.assertIn("risk_factors", review)
            self.assertIn("recommendations", review)
            print("✅ Document Review Agent: PASSED")

        except Exception as e:
            print(f"❌ Document Review Agent: FAILED - {e}")
            self.fail(f"Document review failed: {e}")

    def test_precedent_mining_agent(self):
        """Test precedent discovery functionality"""
        legal_issue = "breach of contract damages"
        jurisdiction = "Federal"
        case_facts = "Software licensing dispute"

        try:
            precedents = self.precedent_agent.discover_relevant_precedents(
                legal_issue=legal_issue,
                jurisdiction=jurisdiction,
                case_facts=case_facts
            )

            self.assertIsInstance(precedents, dict)
            self.assertIn("relevant_precedents", precedents)
            self.assertIn("binding_authority", precedents)
            print("✅ Precedent Mining Agent: PASSED")

        except Exception as e:
            print(f"❌ Precedent Mining Agent: FAILED - {e}")
            self.fail(f"Precedent discovery failed: {e}")

    def test_privilege_protection(self):
        """Test attorney-client privilege protection"""
        attorney_id = "att_001"
        client_id = "CLIENT_001"
        communication = {"type": "case_strategy", "content": "Confidential legal advice"}

        try:
            # Test privilege verification
            has_privilege = self.privilege_system.verify_privilege_relationship(
                attorney_id, client_id
            )
            self.assertTrue(has_privilege)

            # Test communication storage
            stored = self.privilege_system.store_privileged_communication(
                attorney_id=attorney_id,
                client_id=client_id,
                communication=communication
            )
            self.assertTrue(stored)
            print("✅ Privilege Protection: PASSED")

        except Exception as e:
            print(f"❌ Privilege Protection: FAILED - {e}")
            self.fail(f"Privilege protection failed: {e}")

    def test_ethics_compliance(self):
        """Test ethics compliance monitoring"""
        try:
            # Test compliance monitoring
            compliance = self.ethics_manager.monitor_legal_ai_compliance()
            self.assertIsInstance(compliance, dict)
            self.assertIn("overall_compliance", compliance)

            # Test ethics alerts
            alerts = self.ethics_manager.generate_ethics_alerts()
            self.assertIsInstance(alerts, list)
            print("✅ Ethics Compliance: PASSED")

        except Exception as e:
            print(f"❌ Ethics Compliance: FAILED - {e}")
            self.fail(f"Ethics compliance failed: {e}")

    def test_rag_system(self):
        """Test RAG legal search system"""
        query = "contract breach remedies"
        case_context = {"client_position": "plaintiff", "jurisdiction": "California"}

        try:
            # Test hybrid search
            results = self.rag_system.hybrid_legal_search(
                query=query,
                case_context=case_context
            )
            self.assertIsInstance(results, dict)
            self.assertIn("cases", results)
            self.assertIn("statutes", results)

            # Test legal analysis generation
            analysis = self.rag_system.generate_legal_analysis(
                results=results,
                client_position=case_context.get("client_position", "")
            )
            self.assertIsInstance(analysis, dict)
            print("✅ RAG System: PASSED")

        except Exception as e:
            print(f"❌ RAG System: FAILED - {e}")
            self.fail(f"RAG system failed: {e}")

    def test_database_connectivity(self):
        """Test database connectivity and data integrity"""
        try:
            conn = sqlite3.connect('database/legal_data.db')
            cursor = conn.cursor()

            # Test case law table
            cursor.execute("SELECT COUNT(*) FROM case_law")
            case_count = cursor.fetchone()[0]
            self.assertGreater(case_count, 0)

            # Test statutes table
            cursor.execute("SELECT COUNT(*) FROM statutes")
            statute_count = cursor.fetchone()[0]
            self.assertGreater(statute_count, 0)

            # Test precedents table
            cursor.execute("SELECT COUNT(*) FROM legal_precedents")
            precedent_count = cursor.fetchone()[0]
            self.assertGreater(precedent_count, 0)

            conn.close()
            print("✅ Database Connectivity: PASSED")

        except Exception as e:
            print(f"❌ Database Connectivity: FAILED - {e}")
            self.fail(f"Database connectivity failed: {e}")

def run_integration_tests():
    """Run comprehensive integration tests"""
    print("⚖️  Legal AI System Integration Tests")
    print("=" * 50)

    # Check environment
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found - some tests may fail")

    # Check database
    db_file = Path("database/legal_data.db")
    if not db_file.exists():
        print("❌ Database not found. Run: python init_database.py")
        return False

    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLegalAISystem)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All Legal AI System Tests PASSED!")
        print("🚀 System ready for deployment")
        return True
    else:
        print("❌ Some tests FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)