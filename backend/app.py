from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import json
from dotenv import load_dotenv

from agents.research_agent import LegalResearchAgent
from agents.case_agent import CaseAnalysisAgent
from agents.document_agent import DocumentReviewAgent
from agents.precedent_agent import PrecedentMiningAgent
from utils.privilege_protection import AttorneyClientPrivilege
from utils.ethics_compliance import LegalEthicsManager
from utils.rag_system import LegalRAGSystem

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize agents and services
research_agent = LegalResearchAgent()
case_agent = CaseAnalysisAgent()
document_agent = DocumentReviewAgent()
precedent_agent = PrecedentMiningAgent()
privilege_system = AttorneyClientPrivilege()
ethics_manager = LegalEthicsManager()
rag_system = LegalRAGSystem()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('database/legal_data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

@app.route('/api/legal-research', methods=['POST'])
def legal_research():
    """Conduct legal research using AI agent"""
    try:
        data = request.get_json()
        query = data.get('query')
        jurisdiction = data.get('jurisdiction', 'Federal')
        attorney_id = data.get('attorney_id')

        # Conduct legal research
        research_results = research_agent.conduct_research(
            query=query,
            jurisdiction=jurisdiction,
            attorney_id=attorney_id
        )

        # Log for ethics compliance
        ethics_manager.log_research_activity(attorney_id, query, research_results)

        return jsonify({
            "success": True,
            "results": research_results,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/case-analysis', methods=['POST'])
def case_analysis():
    """Analyze case strength and strategy"""
    try:
        data = request.get_json()
        case_facts = data.get('case_facts')
        legal_issues = data.get('legal_issues')
        attorney_id = data.get('attorney_id')
        client_id = data.get('client_id')

        # Verify attorney-client relationship
        if not privilege_system.verify_privilege_relationship(attorney_id, client_id):
            return jsonify({"success": False, "error": "Unauthorized access"}), 403

        # Analyze case
        analysis_results = case_agent.analyze_case_merits(
            case_facts=case_facts,
            legal_issues=legal_issues,
            client_context=privilege_system.get_client_context(attorney_id, client_id)
        )

        # Store privileged communication
        privilege_system.store_privileged_communication(
            attorney_id=attorney_id,
            client_id=client_id,
            communication=analysis_results
        )

        return jsonify({
            "success": True,
            "analysis": analysis_results,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/document-review', methods=['POST'])
def document_review():
    """Review and analyze legal documents"""
    try:
        data = request.get_json()
        document_text = data.get('document_text')
        document_type = data.get('document_type')
        attorney_id = data.get('attorney_id')

        # Review document
        review_results = document_agent.review_document(
            document_text=document_text,
            document_type=document_type,
            attorney_id=attorney_id
        )

        return jsonify({
            "success": True,
            "review": review_results,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/precedent-search', methods=['POST'])
def precedent_search():
    """Search for legal precedents"""
    try:
        data = request.get_json()
        legal_issue = data.get('legal_issue')
        jurisdiction = data.get('jurisdiction')
        case_facts = data.get('case_facts')
        attorney_id = data.get('attorney_id')

        # Search precedents
        precedent_results = precedent_agent.discover_relevant_precedents(
            legal_issue=legal_issue,
            jurisdiction=jurisdiction,
            case_facts=case_facts
        )

        return jsonify({
            "success": True,
            "precedents": precedent_results,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/rag-search', methods=['POST'])
def rag_search():
    """RAG-powered legal document search"""
    try:
        data = request.get_json()
        query = data.get('query')
        case_context = data.get('case_context', {})

        # Perform RAG search
        search_results = rag_system.hybrid_legal_search(
            query=query,
            case_context=case_context
        )

        # Generate legal analysis
        analysis = rag_system.generate_legal_analysis(
            results=search_results,
            client_position=case_context.get('client_position', '')
        )

        return jsonify({
            "success": True,
            "search_results": search_results,
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ethics-compliance', methods=['GET'])
def ethics_compliance():
    """Get ethics compliance status"""
    try:
        attorney_id = request.args.get('attorney_id')

        # Check compliance
        compliance_status = ethics_manager.monitor_legal_ai_compliance()
        ethics_alerts = ethics_manager.generate_ethics_alerts()

        return jsonify({
            "success": True,
            "compliance_status": compliance_status,
            "ethics_alerts": ethics_alerts,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000)