import google.generativeai as genai
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

class LegalRAGSystem:
    """RAG (Retrieval-Augmented Generation) system for legal documents"""

    def __init__(self):
        # Configure Gemini AI
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

        # Initialize embedding model for legal text
        try:
            # Try to use legal-specific embedding model if available
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Fallback to general model
        except:
            # Use a smaller model if resources are limited
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize vector database (ChromaDB)
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_legal_db"
        ))

        # Create or get collections for different document types
        self.collections = {
            'case_law': self._get_or_create_collection('legal_case_law'),
            'statutes': self._get_or_create_collection('legal_statutes'),
            'contracts': self._get_or_create_collection('legal_contracts'),
            'precedents': self._get_or_create_collection('legal_precedents')
        }

        # Initialize collections if empty
        self._initialize_collections()

        # Legal analysis prompt templates
        self.analysis_prompts = {
            'legal_synthesis': """
                You are a legal research AI synthesizing multiple legal authorities.

                Research Query: {query}
                Client Position: {client_position}
                Case Context: {case_context}

                Retrieved Legal Authorities:
                Case Law: {case_results}
                Statutory Authority: {statute_results}
                Precedents: {precedent_results}
                Contract Analysis: {contract_results}

                Provide comprehensive legal analysis:

                1. EXECUTIVE SUMMARY
                   - Key legal findings and implications
                   - Strength of legal position (1-10 scale)
                   - Primary legal authorities supporting position
                   - Critical legal issues identified

                2. LEGAL AUTHORITY ANALYSIS
                   - Controlling case law and holdings
                   - Applicable statutory framework
                   - Relevant precedents and their weight
                   - Hierarchical authority assessment

                3. LEGAL ARGUMENT SYNTHESIS
                   - Primary legal arguments available
                   - Supporting authority for each argument
                   - Potential counterarguments and weaknesses
                   - Strategic argument sequencing

                4. RISK ASSESSMENT
                   - Legal risks and exposure areas
                   - Strength of opposing positions
                   - Procedural and substantive challenges
                   - Mitigation strategies

                5. STRATEGIC RECOMMENDATIONS
                   - Recommended legal approach
                   - Priority legal research areas
                   - Evidence gathering priorities
                   - Next steps and action items

                Use proper legal citation format and maintain attorney-client privilege.
                Focus on practical, actionable legal guidance.
            """,

            'document_analysis': """
                You are analyzing legal documents using RAG-retrieved context.

                Document Type: {document_type}
                Analysis Request: {analysis_request}
                Retrieved Context: {retrieved_context}

                Document Analysis Requirements:
                1. Legal compliance assessment against retrieved authorities
                2. Risk identification based on similar document patterns
                3. Best practice recommendations from retrieved templates
                4. Regulatory compliance verification
                5. Strategic recommendations for document improvement

                Provide detailed analysis with specific citations and recommendations.
            """
        }

    def get_db_connection(self):
        """Get SQLite database connection"""
        return sqlite3.connect('database/legal_data.db')

    def _get_or_create_collection(self, collection_name: str):
        """Get or create a ChromaDB collection"""
        try:
            return self.chroma_client.get_collection(collection_name)
        except:
            return self.chroma_client.create_collection(collection_name)

    def _initialize_collections(self):
        """Initialize vector collections with legal documents"""
        # Check if collections are empty and populate if needed
        for collection_name, collection in self.collections.items():
            if collection.count() == 0:
                print(f"Populating {collection_name} collection...")
                self._populate_collection(collection_name, collection)

    def _populate_collection(self, collection_type: str, collection):
        """Populate vector collection with legal documents"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        if collection_type == 'case_law':
            cursor.execute("""
                SELECT case_id, case_name, citation, holding, legal_issues, full_text
                FROM case_law
            """)
        elif collection_type == 'statutes':
            cursor.execute("""
                SELECT statute_id, statute_title, code_section, statute_text, legal_area
                FROM statutes
            """)
        elif collection_type == 'contracts':
            cursor.execute("""
                SELECT contract_id, contract_type, contract_name, contract_text, standard_clauses
                FROM contracts
            """)
        elif collection_type == 'precedents':
            cursor.execute("""
                SELECT p.precedent_id, p.legal_principle, p.binding_authority,
                       c.case_name, c.citation, c.holding
                FROM legal_precedents p
                JOIN case_law c ON p.case_id = c.case_id
            """)

        results = cursor.fetchall()
        conn.close()

        if not results:
            return

        # Prepare documents for embedding
        documents = []
        metadatas = []
        ids = []

        for i, row in enumerate(results):
            if collection_type == 'case_law':
                doc_text = f"{row[1]} {row[3]} {row[4]} {row[5]}"  # case_name + holding + legal_issues + full_text
                metadata = {
                    'case_id': row[0],
                    'case_name': row[1],
                    'citation': row[2],
                    'type': 'case_law'
                }
            elif collection_type == 'statutes':
                doc_text = f"{row[1]} {row[3]} {row[4]}"  # statute_title + statute_text + legal_area
                metadata = {
                    'statute_id': row[0],
                    'statute_title': row[1],
                    'code_section': row[2],
                    'type': 'statute'
                }
            elif collection_type == 'contracts':
                doc_text = f"{row[2]} {row[3]} {row[4]}"  # contract_name + contract_text + standard_clauses
                metadata = {
                    'contract_id': row[0],
                    'contract_type': row[1],
                    'contract_name': row[2],
                    'type': 'contract'
                }
            elif collection_type == 'precedents':
                doc_text = f"{row[1]} {row[3]} {row[5]}"  # legal_principle + case_name + holding
                metadata = {
                    'precedent_id': row[0],
                    'legal_principle': row[1],
                    'binding_authority': row[2],
                    'case_name': row[3],
                    'type': 'precedent'
                }

            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(f"{collection_type}_{i}")

        # Generate embeddings and add to collection
        if documents:
            embeddings = self.embedding_model.encode(documents).tolist()
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

    def hybrid_legal_search(self, query: str, case_context: Dict = None, top_k: int = 5) -> Dict:
        """Perform hybrid search across all legal document types"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]

            # Search each collection
            search_results = {}

            for collection_name, collection in self.collections.items():
                if collection.count() > 0:
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(top_k, collection.count())
                    )

                    # Process results
                    processed_results = []
                    if results['documents'] and results['documents'][0]:
                        for i, doc in enumerate(results['documents'][0]):
                            processed_results.append({
                                'document': doc,
                                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                                'distance': results['distances'][0][i] if results['distances'] else 0,
                                'relevance_score': 1 - results['distances'][0][i] if results['distances'] else 1
                            })

                    search_results[collection_name] = processed_results

            # Also perform traditional keyword search for comparison
            keyword_results = self._keyword_search(query)

            # Combine and rank results
            combined_results = self._combine_search_results(search_results, keyword_results)

            return {
                'query': query,
                'vector_search_results': search_results,
                'keyword_search_results': keyword_results,
                'combined_results': combined_results,
                'search_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Hybrid search failed: {str(e)}",
                'query': query
            }

    def generate_legal_analysis(self, search_results: Dict, client_position: str = "", case_context: Dict = None) -> Dict:
        """Generate AI-powered legal analysis using RAG results"""
        try:
            # Prepare context from search results
            case_results = search_results.get('vector_search_results', {}).get('case_law', [])
            statute_results = search_results.get('vector_search_results', {}).get('statutes', [])
            precedent_results = search_results.get('vector_search_results', {}).get('precedents', [])
            contract_results = search_results.get('vector_search_results', {}).get('contracts', [])

            # Prepare analysis context
            analysis_context = {
                'query': search_results.get('query', ''),
                'client_position': client_position,
                'case_context': json.dumps(case_context or {}, indent=2),
                'case_results': self._format_results_for_prompt(case_results),
                'statute_results': self._format_results_for_prompt(statute_results),
                'precedent_results': self._format_results_for_prompt(precedent_results),
                'contract_results': self._format_results_for_prompt(contract_results)
            }

            # Generate comprehensive legal analysis
            prompt = self.analysis_prompts['legal_synthesis'].format(**analysis_context)
            response = self.model.generate_content(prompt)
            legal_analysis = response.text

            # Extract key insights
            legal_strength = self._extract_legal_strength(legal_analysis)
            key_authorities = self._extract_key_authorities(legal_analysis)
            recommendations = self._extract_recommendations(legal_analysis)

            return {
                'query': search_results.get('query', ''),
                'legal_analysis': legal_analysis,
                'legal_strength_score': legal_strength,
                'key_authorities': key_authorities,
                'strategic_recommendations': recommendations,
                'supporting_documents': {
                    'case_law_count': len(case_results),
                    'statute_count': len(statute_results),
                    'precedent_count': len(precedent_results),
                    'contract_count': len(contract_results)
                },
                'analysis_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"Legal analysis generation failed: {str(e)}",
                'query': search_results.get('query', '')
            }

    def analyze_document_with_rag(self, document_text: str, document_type: str, analysis_request: str) -> Dict:
        """Analyze a document using RAG-retrieved legal context"""
        try:
            # Search for relevant legal authorities
            search_query = f"{document_type} {analysis_request}"
            search_results = self.hybrid_legal_search(search_query, top_k=3)

            # Format retrieved context
            retrieved_context = self._format_rag_context(search_results)

            # Prepare document analysis context
            doc_analysis_context = {
                'document_type': document_type,
                'analysis_request': analysis_request,
                'retrieved_context': retrieved_context
            }

            # Generate document analysis
            prompt = self.analysis_prompts['document_analysis'].format(**doc_analysis_context)

            # Add document text to prompt
            full_prompt = f"{prompt}\n\nDocument to Analyze:\n{document_text}\n\nProvide comprehensive analysis:"

            response = self.model.generate_content(full_prompt)
            document_analysis = response.text

            return {
                'document_type': document_type,
                'analysis_request': analysis_request,
                'document_analysis': document_analysis,
                'supporting_authorities': search_results['combined_results'][:5],
                'context_sources': len(search_results['combined_results']),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'error': f"RAG document analysis failed: {str(e)}",
                'document_type': document_type
            }

    def _keyword_search(self, query: str, limit: int = 5) -> Dict:
        """Perform traditional keyword search in SQLite database"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        keyword_results = {}

        # Search case law
        cursor.execute("""
            SELECT case_name, citation, holding, legal_issues
            FROM case_law
            WHERE legal_issues LIKE ? OR holding LIKE ? OR case_name LIKE ?
            ORDER BY decision_date DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))

        keyword_results['case_law'] = [
            dict(zip([col[0] for col in cursor.description], row))
            for row in cursor.fetchall()
        ]

        # Search statutes
        cursor.execute("""
            SELECT statute_title, code_section, statute_text, legal_area
            FROM statutes
            WHERE statute_title LIKE ? OR statute_text LIKE ? OR legal_area LIKE ?
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))

        keyword_results['statutes'] = [
            dict(zip([col[0] for col in cursor.description], row))
            for row in cursor.fetchall()
        ]

        conn.close()
        return keyword_results

    def _combine_search_results(self, vector_results: Dict, keyword_results: Dict) -> List[Dict]:
        """Combine and rank vector and keyword search results"""
        combined = []

        # Add vector search results with higher weight
        for collection_type, results in vector_results.items():
            for result in results:
                combined.append({
                    **result,
                    'source_type': collection_type,
                    'search_method': 'vector',
                    'combined_score': result.get('relevance_score', 0) * 0.7  # Weight vector search higher
                })

        # Add keyword search results with lower weight
        for collection_type, results in keyword_results.items():
            for result in results:
                combined.append({
                    'document': str(result),
                    'metadata': result,
                    'source_type': collection_type,
                    'search_method': 'keyword',
                    'combined_score': 0.3  # Fixed score for keyword matches
                })

        # Sort by combined score
        combined.sort(key=lambda x: x['combined_score'], reverse=True)

        return combined[:10]  # Return top 10 results

    def _format_results_for_prompt(self, results: List[Dict]) -> str:
        """Format search results for AI prompt"""
        if not results:
            return "No relevant results found."

        formatted = []
        for i, result in enumerate(results[:3], 1):  # Limit to top 3 for prompt efficiency
            metadata = result.get('metadata', {})
            document = result.get('document', '')[:500]  # Limit document length

            formatted.append(f"""
            Result {i}:
            Type: {metadata.get('type', 'unknown')}
            Title/Name: {metadata.get('case_name') or metadata.get('statute_title') or metadata.get('contract_name', 'N/A')}
            Citation: {metadata.get('citation', 'N/A')}
            Relevance: {result.get('relevance_score', 0):.2f}
            Content: {document}
            """)

        return "\n".join(formatted)

    def _format_rag_context(self, search_results: Dict) -> str:
        """Format RAG search results as context for document analysis"""
        context_parts = []

        for source_type, results in search_results.get('vector_search_results', {}).items():
            if results:
                context_parts.append(f"\n{source_type.upper()} AUTHORITIES:")
                for result in results[:2]:  # Top 2 from each type
                    context_parts.append(f"- {result.get('document', '')[:200]}")

        return "\n".join(context_parts)

    def _extract_legal_strength(self, analysis: str) -> float:
        """Extract legal strength score from analysis"""
        import re

        # Look for strength score patterns
        strength_patterns = [
            r'strength.*?(\d+(?:\.\d+)?)',
            r'score.*?(\d+(?:\.\d+)?)',
            r'position.*?(\d+(?:\.\d+)?)/10'
        ]

        for pattern in strength_patterns:
            match = re.search(pattern, analysis, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                return score if score <= 10 else score / 10

        return 6.5  # Default moderate strength

    def _extract_key_authorities(self, analysis: str) -> List[str]:
        """Extract key legal authorities from analysis"""
        authorities = []

        # Look for case names and citations
        case_pattern = r'([A-Z][a-z]+ v\.? [A-Z][a-z]+|[A-Z][a-z]+ et al\.?)'
        citations = re.findall(case_pattern, analysis)
        authorities.extend(citations[:5])

        # Look for statute references
        statute_pattern = r'(\d+ U\.S\.C\.? §? \d+|\d+ C\.F\.R\.? §? \d+)'
        statutes = re.findall(statute_pattern, analysis)
        authorities.extend(statutes[:3])

        return authorities

    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract strategic recommendations from analysis"""
        recommendations = []
        lines = analysis.split('\n')
        in_recommendations = False

        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'next step', 'action']):
                in_recommendations = True
                continue
            elif in_recommendations and line.strip():
                if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line.strip()):
                    recommendations.append(line.strip().lstrip('- *•0123456789. '))
                elif line.strip().isupper():
                    break

        return recommendations[:6]

    def add_document_to_rag(self, document_text: str, document_type: str, metadata: Dict) -> Dict:
        """Add a new document to the RAG system"""
        try:
            if document_type not in self.collections:
                return {'error': f"Unknown document type: {document_type}"}

            collection = self.collections[document_type]

            # Generate embedding
            embedding = self.embedding_model.encode([document_text]).tolist()[0]

            # Generate unique ID
            doc_id = f"{document_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            # Add to collection
            collection.add(
                documents=[document_text],
                embeddings=[embedding],
                metadatas=[{**metadata, 'type': document_type}],
                ids=[doc_id]
            )

            return {
                'success': True,
                'document_id': doc_id,
                'document_type': document_type,
                'collection_size': collection.count()
            }

        except Exception as e:
            return {'error': f"Failed to add document to RAG: {str(e)}"}

    def search_similar_documents(self, document_text: str, document_type: str = None, top_k: int = 5) -> Dict:
        """Find documents similar to the provided text"""
        try:
            query_embedding = self.embedding_model.encode([document_text]).tolist()[0]

            similar_docs = {}

            collections_to_search = [document_type] if document_type and document_type in self.collections else self.collections.keys()

            for collection_name in collections_to_search:
                collection = self.collections[collection_name]

                if collection.count() > 0:
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(top_k, collection.count())
                    )

                    similar_docs[collection_name] = []
                    if results['documents'] and results['documents'][0]:
                        for i, doc in enumerate(results['documents'][0]):
                            similar_docs[collection_name].append({
                                'document': doc[:300],  # Truncate for display
                                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                                'similarity_score': 1 - results['distances'][0][i] if results['distances'] else 1
                            })

            return {
                'query_document_type': document_type,
                'similar_documents': similar_docs,
                'total_matches': sum(len(docs) for docs in similar_docs.values()),
                'search_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {'error': f"Similar document search failed: {str(e)}"}

    def get_rag_statistics(self) -> Dict:
        """Get statistics about the RAG system"""
        stats = {
            'collections': {},
            'total_documents': 0,
            'embedding_model': str(self.embedding_model),
            'last_updated': datetime.utcnow().isoformat()
        }

        for name, collection in self.collections.items():
            count = collection.count()
            stats['collections'][name] = count
            stats['total_documents'] += count

        return stats