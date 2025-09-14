import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import re
from collections import defaultdict
from enum import Enum

class EthicsRuleCategory(Enum):
    """Ethics rule categories"""
    COMPETENCE = "competence"
    CONFIDENTIALITY = "confidentiality"
    CONFLICTS = "conflicts_of_interest"
    CLIENT_PROPERTY = "client_property"
    FEES = "fees_and_billing"
    COMMUNICATION = "client_communication"
    SUPERVISION = "supervision"
    AI_DISCLOSURE = "ai_disclosure"

class ComplianceLevel(Enum):
    """Compliance assessment levels"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"

class LegalEthicsManager:
    """Legal Ethics Compliance and Professional Responsibility Manager"""

    def __init__(self):
        # Ethics rules database
        self.ethics_rules = {
            EthicsRuleCategory.COMPETENCE: {
                'rule_1_1': "A lawyer shall provide competent representation to a client",
                'rule_1_6': "A lawyer shall keep abreast of changes in the law and its practice, including the benefits and risks associated with relevant technology",
                'ai_competence': "Attorney must understand AI capabilities and limitations when using AI tools"
            },
            EthicsRuleCategory.CONFIDENTIALITY: {
                'rule_1_6': "A lawyer shall not reveal information relating to the representation of a client",
                'rule_1_6_c': "A lawyer shall make reasonable efforts to prevent inadvertent or unauthorized disclosure",
                'ai_confidentiality': "AI systems must maintain client confidentiality and attorney-client privilege"
            },
            EthicsRuleCategory.AI_DISCLOSURE: {
                'ai_transparency': "Attorney should disclose the use of AI tools to clients when material to representation",
                'ai_supervision': "Attorney must supervise and be responsible for AI-generated work product",
                'ai_accuracy': "Attorney must verify accuracy of AI-generated legal analysis and advice"
            },
            EthicsRuleCategory.CONFLICTS: {
                'rule_1_7': "A lawyer shall not represent a client if representation involves a concurrent conflict of interest",
                'rule_1_9': "A lawyer who has formerly represented a client shall not represent another person in the same or substantially related matter"
            }
        }

        # Compliance monitoring thresholds
        self.compliance_thresholds = {
            'ai_usage_disclosure_rate': 0.8,  # 80% of AI usage should be disclosed
            'privilege_access_violations': 0,  # Zero tolerance for privilege violations
            'competence_training_frequency': 90,  # Days between required training
            'client_communication_response_time': 48  # Hours for client response
        }

    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect('database/legal_data.db')

    def monitor_legal_ai_compliance(self) -> Dict:
        """Monitor compliance with legal AI usage ethics"""
        try:
            compliance_status = {
                'overall_compliance': ComplianceLevel.COMPLIANT.value,
                'compliance_score': 0.0,
                'category_compliance': {},
                'violations': [],
                'warnings': [],
                'recommendations': []
            }

            # Check each ethics category
            competence_check = self._check_ai_competence_compliance()
            confidentiality_check = self._check_confidentiality_compliance()
            disclosure_check = self._check_ai_disclosure_compliance()
            supervision_check = self._check_ai_supervision_compliance()

            # Aggregate compliance results
            category_results = {
                EthicsRuleCategory.COMPETENCE.value: competence_check,
                EthicsRuleCategory.CONFIDENTIALITY.value: confidentiality_check,
                EthicsRuleCategory.AI_DISCLOSURE.value: disclosure_check,
                EthicsRuleCategory.SUPERVISION.value: supervision_check
            }

            total_score = 0
            category_count = len(category_results)

            for category, result in category_results.items():
                compliance_status['category_compliance'][category] = result
                total_score += result.get('score', 0)

                # Collect violations and warnings
                compliance_status['violations'].extend(result.get('violations', []))
                compliance_status['warnings'].extend(result.get('warnings', []))

            # Calculate overall compliance score
            compliance_status['compliance_score'] = total_score / category_count if category_count > 0 else 0

            # Determine overall compliance level
            if compliance_status['compliance_score'] >= 8.0:
                compliance_status['overall_compliance'] = ComplianceLevel.COMPLIANT.value
            elif compliance_status['compliance_score'] >= 6.0:
                compliance_status['overall_compliance'] = ComplianceLevel.WARNING.value
            elif compliance_status['compliance_score'] >= 4.0:
                compliance_status['overall_compliance'] = ComplianceLevel.VIOLATION.value
            else:
                compliance_status['overall_compliance'] = ComplianceLevel.CRITICAL.value

            # Generate recommendations
            compliance_status['recommendations'] = self._generate_compliance_recommendations(compliance_status)

            # Log compliance check
            self._log_compliance_check(compliance_status)

            return compliance_status

        except Exception as e:
            return {
                'error': f"Compliance monitoring failed: {str(e)}",
                'overall_compliance': ComplianceLevel.CRITICAL.value
            }

    def _check_ai_competence_compliance(self) -> Dict:
        """Check AI competence requirements (Rule 1.1, 1.6)"""
        competence_result = {
            'score': 8.0,  # Default good score
            'violations': [],
            'warnings': [],
            'details': {}
        }

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Check for AI usage without proper training/understanding indicators
            cursor.execute("""
                SELECT COUNT(*) FROM research_history
                WHERE research_results LIKE '%AI%' OR query LIKE '%artificial intelligence%'
            """)
            ai_usage_count = cursor.fetchone()[0]

            # Check for error patterns that might indicate lack of competence
            cursor.execute("""
                SELECT COUNT(*) FROM ethics_audit_log
                WHERE action_type LIKE '%ERROR%' OR action_details LIKE '%failed%'
            """)
            error_count = cursor.fetchone()[0]

            conn.close()

            competence_result['details'] = {
                'ai_usage_instances': ai_usage_count,
                'error_instances': error_count,
                'competence_indicators': []
            }

            # Assess competence based on usage patterns
            if ai_usage_count > 10 and error_count < 2:
                competence_result['competence_indicators'].append("Regular AI usage with low error rate")
                competence_result['score'] = 9.0
            elif error_count > 5:
                competence_result['warnings'].append("High error rate may indicate competence gaps")
                competence_result['score'] = 6.0
            elif ai_usage_count == 0:
                competence_result['warnings'].append("No AI usage detected - consider technology competence training")
                competence_result['score'] = 7.0

            return competence_result

        except Exception as e:
            return {
                'score': 5.0,
                'violations': [f"Competence check failed: {str(e)}"],
                'warnings': [],
                'details': {}
            }

    def _check_confidentiality_compliance(self) -> Dict:
        """Check confidentiality and privilege protection (Rule 1.6)"""
        confidentiality_result = {
            'score': 9.0,  # Start with high score
            'violations': [],
            'warnings': [],
            'details': {}
        }

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Check for privilege violations
            cursor.execute("""
                SELECT COUNT(*) FROM ethics_audit_log
                WHERE action_type LIKE '%PRIVILEGE_VIOLATION%'
            """)
            privilege_violations = cursor.fetchone()[0]

            # Check encryption usage for privileged communications
            cursor.execute("""
                SELECT COUNT(*) FROM privileged_communications
                WHERE privilege_level = 'FULL'
            """)
            encrypted_communications = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM privileged_communications
            """)
            total_communications = cursor.fetchone()[0]

            conn.close()

            confidentiality_result['details'] = {
                'privilege_violations': privilege_violations,
                'encrypted_communications': encrypted_communications,
                'total_communications': total_communications,
                'encryption_rate': encrypted_communications / max(total_communications, 1)
            }

            # Assess confidentiality compliance
            if privilege_violations > 0:
                confidentiality_result['violations'].append(f"{privilege_violations} privilege violations detected")
                confidentiality_result['score'] = 3.0

            if confidentiality_result['details']['encryption_rate'] < 0.95:
                confidentiality_result['warnings'].append("Low encryption rate for privileged communications")
                confidentiality_result['score'] = min(confidentiality_result['score'], 7.0)

            return confidentiality_result

        except Exception as e:
            return {
                'score': 5.0,
                'violations': [f"Confidentiality check failed: {str(e)}"],
                'warnings': [],
                'details': {}
            }

    def _check_ai_disclosure_compliance(self) -> Dict:
        """Check AI usage disclosure compliance"""
        disclosure_result = {
            'score': 7.0,  # Default moderate score
            'violations': [],
            'warnings': [],
            'details': {}
        }

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Check for AI usage tracking
            cursor.execute("""
                SELECT COUNT(*) FROM ethics_audit_log
                WHERE action_type LIKE '%AI_DISCLOSURE%'
            """)
            disclosure_instances = cursor.fetchone()[0]

            # Check total AI usage
            cursor.execute("""
                SELECT COUNT(*) FROM research_history
            """)
            total_ai_usage = cursor.fetchone()[0]

            conn.close()

            disclosure_rate = disclosure_instances / max(total_ai_usage, 1)

            disclosure_result['details'] = {
                'disclosure_instances': disclosure_instances,
                'total_ai_usage': total_ai_usage,
                'disclosure_rate': disclosure_rate
            }

            # Assess disclosure compliance
            if disclosure_rate >= self.compliance_thresholds['ai_usage_disclosure_rate']:
                disclosure_result['score'] = 9.0
            elif disclosure_rate >= 0.5:
                disclosure_result['warnings'].append("AI disclosure rate below recommended threshold")
                disclosure_result['score'] = 6.0
            else:
                disclosure_result['violations'].append("Insufficient AI usage disclosure to clients")
                disclosure_result['score'] = 4.0

            return disclosure_result

        except Exception as e:
            return {
                'score': 5.0,
                'violations': [f"AI disclosure check failed: {str(e)}"],
                'warnings': [],
                'details': {}
            }

    def _check_ai_supervision_compliance(self) -> Dict:
        """Check AI supervision and verification requirements"""
        supervision_result = {
            'score': 8.0,
            'violations': [],
            'warnings': [],
            'details': {}
        }

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Check for human review/verification of AI outputs
            cursor.execute("""
                SELECT COUNT(*) FROM ethics_audit_log
                WHERE action_type LIKE '%AI_VERIFICATION%' OR action_type LIKE '%HUMAN_REVIEW%'
            """)
            verification_instances = cursor.fetchone()[0]

            # Check for unsupervised AI usage indicators
            cursor.execute("""
                SELECT COUNT(*) FROM ethics_audit_log
                WHERE action_details LIKE '%automatic%' OR action_details LIKE '%unsupervised%'
            """)
            unsupervised_usage = cursor.fetchone()[0]

            conn.close()

            supervision_result['details'] = {
                'verification_instances': verification_instances,
                'unsupervised_usage_instances': unsupervised_usage,
                'supervision_indicators': []
            }

            # Assess supervision compliance
            if unsupervised_usage > 0:
                supervision_result['warnings'].append(f"{unsupervised_usage} instances of potentially unsupervised AI usage")
                supervision_result['score'] = 6.0

            if verification_instances > 0:
                supervision_result['supervision_indicators'].append("Evidence of AI output verification")
                supervision_result['score'] = min(supervision_result['score'] + 1.0, 10.0)

            return supervision_result

        except Exception as e:
            return {
                'score': 5.0,
                'violations': [f"Supervision check failed: {str(e)}"],
                'warnings': [],
                'details': {}
            }

    def generate_ethics_alerts(self) -> List[str]:
        """Generate ethics compliance alerts"""
        alerts = []

        try:
            # Check for immediate ethics concerns
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Check for recent privilege violations
            cursor.execute("""
                SELECT COUNT(*) FROM ethics_audit_log
                WHERE action_type LIKE '%PRIVILEGE_VIOLATION%'
                  AND audit_timestamp >= ?
            """, ((datetime.utcnow() - timedelta(days=7)).isoformat(),))

            recent_violations = cursor.fetchone()[0]

            if recent_violations > 0:
                alerts.append(f"CRITICAL: {recent_violations} privilege violations in the past 7 days")

            # Check for missing AI disclosures
            cursor.execute("""
                SELECT COUNT(*) FROM research_history
                WHERE timestamp >= ? AND research_id NOT IN (
                    SELECT DISTINCT SUBSTR(action_details, INSTR(action_details, 'research_') + 9)
                    FROM ethics_audit_log
                    WHERE action_type = 'AI_DISCLOSURE'
                )
            """, ((datetime.utcnow() - timedelta(days=30)).isoformat(),))

            undisclosed_ai_usage = cursor.fetchone()[0]

            if undisclosed_ai_usage > 5:
                alerts.append(f"WARNING: {undisclosed_ai_usage} undisclosed AI usage instances in past 30 days")

            # Check for competence training needs
            cursor.execute("""
                SELECT COUNT(*) FROM ethics_audit_log
                WHERE action_type LIKE '%ERROR%'
                  AND audit_timestamp >= ?
            """, ((datetime.utcnow() - timedelta(days=30)).isoformat(),))

            recent_errors = cursor.fetchone()[0]

            if recent_errors > 10:
                alerts.append(f"ATTENTION: {recent_errors} errors in past 30 days - consider additional training")

            conn.close()

            # Add system-level alerts
            if not alerts:
                alerts.append("All ethics compliance checks passing")

            return alerts

        except Exception as e:
            return [f"ERROR: Ethics alert generation failed - {str(e)}"]

    def log_research_activity(self, attorney_id: str, query: str, results: Dict):
        """Log research activity for ethics compliance tracking"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Detect AI usage in research
            ai_usage_detected = any(
                keyword in query.lower()
                for keyword in ['ai', 'artificial intelligence', 'machine learning', 'automated']
            ) or 'ai_analysis' in str(results).lower()

            # Log the research activity
            audit_id = f"research_audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"

            cursor.execute("""
                INSERT INTO ethics_audit_log
                (audit_id, attorney_id, action_type, action_details, compliance_status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                audit_id,
                attorney_id,
                'LEGAL_RESEARCH_CONDUCTED',
                f"Query: {query[:100]}... AI detected: {ai_usage_detected}",
                'compliant'
            ))

            # If AI usage detected, check for disclosure requirements
            if ai_usage_detected:
                cursor.execute("""
                    INSERT INTO ethics_audit_log
                    (audit_id, attorney_id, action_type, action_details, compliance_status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    f"ai_usage_{audit_id}",
                    attorney_id,
                    'AI_USAGE_DETECTED',
                    f"AI usage in research query: {query[:50]}",
                    'requires_disclosure'
                ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Warning: Failed to log research activity: {str(e)}")

    def _generate_compliance_recommendations(self, compliance_status: Dict) -> List[str]:
        """Generate recommendations based on compliance assessment"""
        recommendations = []

        overall_score = compliance_status.get('compliance_score', 0)

        if overall_score < 6.0:
            recommendations.extend([
                "Implement immediate ethics compliance review",
                "Conduct emergency training on professional responsibility",
                "Establish daily compliance monitoring procedures"
            ])

        if compliance_status.get('violations'):
            recommendations.append("Address all identified violations immediately")
            recommendations.append("Implement corrective action plan with timeline")

        # Category-specific recommendations
        category_compliance = compliance_status.get('category_compliance', {})

        for category, result in category_compliance.items():
            if result.get('score', 10) < 7.0:
                if category == EthicsRuleCategory.COMPETENCE.value:
                    recommendations.append("Schedule AI and technology competence training")
                elif category == EthicsRuleCategory.CONFIDENTIALITY.value:
                    recommendations.append("Review and strengthen confidentiality procedures")
                elif category == EthicsRuleCategory.AI_DISCLOSURE.value:
                    recommendations.append("Implement systematic AI usage disclosure protocol")

        if not recommendations:
            recommendations.append("Continue maintaining excellent ethics compliance standards")

        return recommendations

    def _log_compliance_check(self, compliance_status: Dict):
        """Log compliance check results"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            audit_id = f"compliance_check_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            cursor.execute("""
                INSERT INTO ethics_audit_log
                (audit_id, attorney_id, action_type, action_details, compliance_status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                audit_id,
                'SYSTEM',
                'COMPLIANCE_MONITORING',
                f"Overall score: {compliance_status.get('compliance_score', 0):.1f}, "
                f"Violations: {len(compliance_status.get('violations', []))}, "
                f"Warnings: {len(compliance_status.get('warnings', []))}",
                compliance_status.get('overall_compliance', 'unknown')
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Warning: Failed to log compliance check: {str(e)}")

    def create_ethics_training_requirement(self, attorney_id: str, training_type: str, due_date: str) -> Dict:
        """Create ethics training requirement for attorney"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            training_id = f"training_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{attorney_id}"

            cursor.execute("""
                INSERT INTO ethics_audit_log
                (audit_id, attorney_id, action_type, action_details, compliance_status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                training_id,
                attorney_id,
                'TRAINING_REQUIREMENT_CREATED',
                f"Training type: {training_type}, Due date: {due_date}",
                'pending'
            ))

            conn.commit()
            conn.close()

            return {
                'success': True,
                'training_id': training_id,
                'attorney_id': attorney_id,
                'training_type': training_type,
                'due_date': due_date,
                'status': 'pending'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create training requirement: {str(e)}"
            }

    def conduct_conflict_check(self, attorney_id: str, new_client_info: Dict, matter_description: str) -> Dict:
        """Conduct conflict of interest check"""
        try:
            conflicts_found = []
            potential_conflicts = []

            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Check for existing clients with similar matters
            cursor.execute("""
                SELECT client_id, case_name, legal_issues
                FROM client_cases
                WHERE attorney_id = ? AND case_status = 'Active'
            """, (attorney_id,))

            existing_cases = cursor.fetchall()

            # Simple conflict detection (would be more sophisticated in practice)
            new_client_name = new_client_info.get('client_name', '').lower()

            for case in existing_cases:
                existing_client_id, case_name, legal_issues = case

                # Check for direct client conflicts
                if new_client_name in case_name.lower():
                    conflicts_found.append({
                        'type': 'DIRECT_CLIENT_CONFLICT',
                        'existing_case': case_name,
                        'description': 'Same or related client already represented'
                    })

                # Check for matter conflicts
                if any(keyword in legal_issues.lower() for keyword in matter_description.lower().split()):
                    potential_conflicts.append({
                        'type': 'RELATED_MATTER',
                        'existing_case': case_name,
                        'description': 'Similar legal matter for different client'
                    })

            # Log conflict check
            cursor.execute("""
                INSERT INTO ethics_audit_log
                (audit_id, attorney_id, action_type, action_details, compliance_status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"conflict_check_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                attorney_id,
                'CONFLICT_OF_INTEREST_CHECK',
                f"New client: {new_client_name}, Conflicts found: {len(conflicts_found)}, Potential: {len(potential_conflicts)}",
                'compliant' if len(conflicts_found) == 0 else 'conflict_detected'
            ))

            conn.commit()
            conn.close()

            return {
                'attorney_id': attorney_id,
                'new_client_info': new_client_info,
                'conflicts_found': conflicts_found,
                'potential_conflicts': potential_conflicts,
                'can_represent': len(conflicts_found) == 0,
                'requires_review': len(potential_conflicts) > 0,
                'check_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Conflict check failed: {str(e)}",
                'can_represent': False
            }

    def generate_ethics_compliance_report(self, attorney_id: str = None, period_days: int = 30) -> Dict:
        """Generate comprehensive ethics compliance report"""
        try:
            start_date = (datetime.utcnow() - timedelta(days=period_days)).isoformat()
            end_date = datetime.utcnow().isoformat()

            # Get current compliance status
            current_compliance = self.monitor_legal_ai_compliance()

            # Get audit history
            conn = self.get_db_connection()
            cursor = conn.cursor()

            query = """
                SELECT action_type, compliance_status, COUNT(*) as count
                FROM ethics_audit_log
                WHERE audit_timestamp BETWEEN ? AND ?
            """
            params = [start_date, end_date]

            if attorney_id:
                query += " AND attorney_id = ?"
                params.append(attorney_id)

            query += " GROUP BY action_type, compliance_status ORDER BY count DESC"

            cursor.execute(query, params)
            audit_summary = cursor.fetchall()

            conn.close()

            # Format audit summary
            audit_data = []
            for row in audit_summary:
                audit_data.append({
                    'action_type': row[0],
                    'compliance_status': row[1],
                    'count': row[2]
                })

            # Generate report
            report = {
                'report_period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'period_days': period_days
                },
                'attorney_id': attorney_id,
                'current_compliance': current_compliance,
                'audit_summary': audit_data,
                'total_audit_entries': sum(item['count'] for item in audit_data),
                'compliance_trends': self._analyze_compliance_trends(audit_data),
                'report_generated': datetime.utcnow().isoformat()
            }

            return report

        except Exception as e:
            return {
                'success': False,
                'error': f"Ethics compliance report generation failed: {str(e)}"
            }

    def _analyze_compliance_trends(self, audit_data: List[Dict]) -> Dict:
        """Analyze compliance trends from audit data"""
        trends = {
            'compliance_indicators': [],
            'risk_indicators': [],
            'improvement_areas': []
        }

        for item in audit_data:
            action_type = item['action_type']
            status = item['compliance_status']
            count = item['count']

            if status == 'compliant' and count > 5:
                trends['compliance_indicators'].append(f"Regular {action_type.lower()} activity")
            elif status in ['violation', 'critical'] and count > 0:
                trends['risk_indicators'].append(f"{count} instances of {action_type}")
            elif 'ERROR' in action_type or 'FAILED' in action_type:
                trends['improvement_areas'].append(f"Address {action_type.lower()} issues ({count} occurrences)")

        return trends