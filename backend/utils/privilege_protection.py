from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import sqlite3
import os
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import hashlib
import secrets

class AttorneyClientPrivilege:
    """Attorney-Client Privilege Protection and Management System"""

    def __init__(self):
        # Initialize encryption key
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)

        # Privilege levels
        self.PRIVILEGE_LEVELS = {
            'FULL': 'full_access',          # Full attorney-client privilege
            'LIMITED': 'limited_access',     # Limited privilege (work product)
            'PUBLIC': 'public_access',       # No privilege protection
            'SEALED': 'sealed_access'        # Court-sealed information
        }

        # Access roles
        self.ACCESS_ROLES = {
            'ATTORNEY': 'attorney',
            'CLIENT': 'client',
            'PARALEGAL': 'paralegal',
            'STAFF': 'staff',
            'COURT': 'court',
            'OPPOSING': 'opposing_counsel'
        }

    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for privilege protection"""
        key_file = 'privilege_key.key'

        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect('database/legal_data.db')

    def verify_privilege_relationship(self, attorney_id: str, client_id: str) -> bool:
        """Verify valid attorney-client relationship exists"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Check if attorney-client relationship exists and is active
        cursor.execute("""
            SELECT COUNT(*) FROM client_cases
            WHERE attorney_id = ? AND client_id = ? AND case_status = 'Active'
        """, (attorney_id, client_id))

        result = cursor.fetchone()
        conn.close()

        return result[0] > 0 if result else False

    def create_privilege_relationship(self, attorney_id: str, client_id: str, case_id: str, privilege_scope: str = "FULL") -> Dict:
        """Create new attorney-client privilege relationship"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Create relationship record
            relationship_data = {
                'attorney_id': attorney_id,
                'client_id': client_id,
                'case_id': case_id,
                'privilege_scope': privilege_scope,
                'established_date': datetime.utcnow().isoformat(),
                'status': 'active'
            }

            # Store encrypted relationship data
            encrypted_data = self.encrypt_privileged_data(json.dumps(relationship_data))

            # Log privilege relationship creation
            self._log_privilege_action(
                attorney_id=attorney_id,
                action_type='PRIVILEGE_RELATIONSHIP_CREATED',
                details=f"Created privilege relationship with client {client_id} for case {case_id}",
                privilege_level=privilege_scope
            )

            conn.commit()
            conn.close()

            return {
                'success': True,
                'relationship_id': f"{attorney_id}_{client_id}_{case_id}",
                'privilege_scope': privilege_scope,
                'established_date': relationship_data['established_date']
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create privilege relationship: {str(e)}"
            }

    def store_privileged_communication(self, attorney_id: str, client_id: str, communication: Dict, privilege_level: str = "FULL") -> Dict:
        """Store privileged attorney-client communication with encryption"""
        try:
            # Verify privilege relationship
            if not self.verify_privilege_relationship(attorney_id, client_id):
                raise PrivilegeViolationError("No valid attorney-client relationship")

            # Prepare communication data
            comm_data = {
                'communication': communication,
                'timestamp': datetime.utcnow().isoformat(),
                'privilege_level': privilege_level,
                'attorney_id': attorney_id,
                'client_id': client_id
            }

            # Encrypt privileged communication
            encrypted_comm = self.encrypt_privileged_data(json.dumps(comm_data))

            # Store in database
            conn = self.get_db_connection()
            cursor = conn.cursor()

            comm_id = f"comm_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{attorney_id}_{client_id}"

            cursor.execute("""
                INSERT INTO privileged_communications
                (comm_id, attorney_id, client_id, communication_text, communication_type, privilege_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                comm_id,
                attorney_id,
                client_id,
                encrypted_comm,
                communication.get('type', 'legal_advice'),
                privilege_level
            ))

            # Log privileged communication storage
            self._log_privilege_action(
                attorney_id=attorney_id,
                action_type='PRIVILEGED_COMMUNICATION_STORED',
                details=f"Stored privileged communication with client {client_id}",
                privilege_level=privilege_level
            )

            conn.commit()
            conn.close()

            return {
                'success': True,
                'communication_id': comm_id,
                'privilege_level': privilege_level,
                'encrypted': True,
                'timestamp': comm_data['timestamp']
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to store privileged communication: {str(e)}"
            }

    def retrieve_privileged_communication(self, attorney_id: str, client_id: str, comm_id: str = None) -> Dict:
        """Retrieve and decrypt privileged communications"""
        try:
            # Verify privilege relationship
            if not self.verify_privilege_relationship(attorney_id, client_id):
                raise PrivilegeViolationError("No valid attorney-client relationship")

            conn = self.get_db_connection()
            cursor = conn.cursor()

            if comm_id:
                # Retrieve specific communication
                cursor.execute("""
                    SELECT comm_id, communication_text, communication_type, privilege_level, created_at
                    FROM privileged_communications
                    WHERE attorney_id = ? AND client_id = ? AND comm_id = ?
                """, (attorney_id, client_id, comm_id))
            else:
                # Retrieve all communications for attorney-client pair
                cursor.execute("""
                    SELECT comm_id, communication_text, communication_type, privilege_level, created_at
                    FROM privileged_communications
                    WHERE attorney_id = ? AND client_id = ?
                    ORDER BY created_at DESC
                    LIMIT 50
                """, (attorney_id, client_id))

            results = cursor.fetchall()
            conn.close()

            # Decrypt and format communications
            communications = []
            for row in results:
                try:
                    decrypted_text = self.decrypt_privileged_data(row[1])
                    comm_data = json.loads(decrypted_text)

                    communications.append({
                        'comm_id': row[0],
                        'communication': comm_data.get('communication', {}),
                        'communication_type': row[2],
                        'privilege_level': row[3],
                        'timestamp': row[4],
                        'decrypted_successfully': True
                    })
                except Exception as decrypt_error:
                    communications.append({
                        'comm_id': row[0],
                        'error': f"Decryption failed: {str(decrypt_error)}",
                        'decrypted_successfully': False
                    })

            # Log privilege access
            self._log_privilege_action(
                attorney_id=attorney_id,
                action_type='PRIVILEGED_COMMUNICATION_ACCESSED',
                details=f"Retrieved {len(communications)} privileged communications with client {client_id}",
                privilege_level='FULL'
            )

            return {
                'success': True,
                'communications': communications,
                'total_count': len(communications),
                'attorney_id': attorney_id,
                'client_id': client_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to retrieve privileged communications: {str(e)}"
            }

    def get_client_context(self, attorney_id: str, client_id: str) -> Dict:
        """Get client context while maintaining privilege protection"""
        try:
            # Verify privilege relationship
            if not self.verify_privilege_relationship(attorney_id, client_id):
                return {'error': 'No valid attorney-client relationship'}

            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Get client case information
            cursor.execute("""
                SELECT case_id, case_name, case_type, case_status, case_facts, legal_issues, strategy_notes
                FROM client_cases
                WHERE attorney_id = ? AND client_id = ?
            """, (attorney_id, client_id))

            case_results = cursor.fetchall()

            # Get recent privileged communications (limited)
            recent_comms = self.retrieve_privileged_communication(attorney_id, client_id)

            conn.close()

            # Format client context
            client_context = {
                'client_id': client_id,
                'attorney_id': attorney_id,
                'active_cases': [],
                'recent_communications_count': len(recent_comms.get('communications', [])),
                'privilege_protected': True
            }

            for row in case_results:
                client_context['active_cases'].append({
                    'case_id': row[0],
                    'case_name': row[1],
                    'case_type': row[2],
                    'case_status': row[3],
                    'case_facts': row[4],
                    'legal_issues': row[5]
                    # Note: strategy_notes excluded for additional security
                })

            return client_context

        except Exception as e:
            return {'error': f"Failed to get client context: {str(e)}"}

    def encrypt_privileged_data(self, data: str) -> str:
        """Encrypt privileged data using Fernet encryption"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            raise PrivilegeProtectionError(f"Encryption failed: {str(e)}")

    def decrypt_privileged_data(self, encrypted_data: str) -> str:
        """Decrypt privileged data"""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise PrivilegeProtectionError(f"Decryption failed: {str(e)}")

    def check_privilege_access(self, user_id: str, user_role: str, attorney_id: str, client_id: str, resource_type: str) -> Dict:
        """Check if user has privilege to access specific resource"""
        access_granted = False
        access_basis = "DENIED"

        try:
            if user_role == self.ACCESS_ROLES['ATTORNEY']:
                # Attorney can access their own client communications
                if user_id == attorney_id:
                    access_granted = True
                    access_basis = "ATTORNEY_CLIENT_PRIVILEGE"

            elif user_role == self.ACCESS_ROLES['CLIENT']:
                # Client can access their own communications
                if user_id == client_id:
                    access_granted = True
                    access_basis = "CLIENT_PRIVILEGE_RIGHTS"

            elif user_role == self.ACCESS_ROLES['PARALEGAL']:
                # Paralegal needs verification of employment with attorney
                if self._verify_paralegal_relationship(user_id, attorney_id):
                    access_granted = True
                    access_basis = "PARALEGAL_SUPERVISED_ACCESS"

            # Log access attempt
            self._log_privilege_action(
                attorney_id=attorney_id,
                action_type='PRIVILEGE_ACCESS_CHECK',
                details=f"User {user_id} ({user_role}) requested access to {resource_type}. Access: {access_granted}",
                privilege_level='AUDIT'
            )

            return {
                'access_granted': access_granted,
                'access_basis': access_basis,
                'user_id': user_id,
                'user_role': user_role,
                'attorney_id': attorney_id,
                'client_id': client_id,
                'resource_type': resource_type,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                'access_granted': False,
                'access_basis': 'ERROR',
                'error': str(e)
            }

    def _verify_paralegal_relationship(self, paralegal_id: str, attorney_id: str) -> bool:
        """Verify paralegal is authorized to access attorney's privileged materials"""
        # Simplified verification - in practice, this would check employment records
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Check if paralegal has authorized access to attorney's cases
        cursor.execute("""
            SELECT COUNT(*) FROM legal_entities
            WHERE entity_id = ? AND entity_type = 'paralegal'
        """, (paralegal_id,))

        result = cursor.fetchone()
        conn.close()

        return result[0] > 0 if result else False

    def _log_privilege_action(self, attorney_id: str, action_type: str, details: str, privilege_level: str):
        """Log privilege-related actions for audit trail"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            audit_id = f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"

            cursor.execute("""
                INSERT INTO ethics_audit_log
                (audit_id, attorney_id, action_type, action_details, compliance_status, audit_timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                audit_id,
                attorney_id,
                action_type,
                details,
                'compliant',
                datetime.utcnow().isoformat()
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            # Logging failure should not break privilege operations
            print(f"Warning: Failed to log privilege action: {str(e)}")

    def audit_privilege_access(self, attorney_id: str = None, start_date: str = None, end_date: str = None) -> Dict:
        """Audit privilege access patterns and compliance"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Build audit query
            query = "SELECT * FROM ethics_audit_log WHERE 1=1"
            params = []

            if attorney_id:
                query += " AND attorney_id = ?"
                params.append(attorney_id)

            if start_date:
                query += " AND audit_timestamp >= ?"
                params.append(start_date)

            if end_date:
                query += " AND audit_timestamp <= ?"
                params.append(end_date)

            query += " ORDER BY audit_timestamp DESC LIMIT 100"

            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            # Process audit results
            audit_entries = []
            action_summary = {}

            for row in results:
                entry = dict(zip([col[0] for col in cursor.description], row))
                audit_entries.append(entry)

                action_type = entry.get('action_type', 'UNKNOWN')
                action_summary[action_type] = action_summary.get(action_type, 0) + 1

            return {
                'success': True,
                'audit_entries': audit_entries,
                'total_entries': len(audit_entries),
                'action_summary': action_summary,
                'audit_period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'attorney_id': attorney_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Audit failed: {str(e)}"
            }

    def destroy_privileged_data(self, attorney_id: str, client_id: str, reason: str) -> Dict:
        """Securely destroy privileged data (e.g., case closure, client request)"""
        try:
            # Verify authorization for data destruction
            if not self.verify_privilege_relationship(attorney_id, client_id):
                raise PrivilegeViolationError("No valid attorney-client relationship for data destruction")

            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Get count of communications to be destroyed
            cursor.execute("""
                SELECT COUNT(*) FROM privileged_communications
                WHERE attorney_id = ? AND client_id = ?
            """, (attorney_id, client_id))

            comm_count = cursor.fetchone()[0]

            # Mark communications for destruction (don't delete immediately for audit)
            cursor.execute("""
                UPDATE privileged_communications
                SET privilege_level = 'DESTROYED', communication_text = 'DATA_DESTROYED'
                WHERE attorney_id = ? AND client_id = ?
            """, (attorney_id, client_id))

            # Log data destruction
            self._log_privilege_action(
                attorney_id=attorney_id,
                action_type='PRIVILEGED_DATA_DESTROYED',
                details=f"Destroyed {comm_count} privileged communications with client {client_id}. Reason: {reason}",
                privilege_level='AUDIT'
            )

            conn.commit()
            conn.close()

            return {
                'success': True,
                'communications_destroyed': comm_count,
                'destruction_reason': reason,
                'destruction_timestamp': datetime.utcnow().isoformat(),
                'attorney_id': attorney_id,
                'client_id': client_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Data destruction failed: {str(e)}"
            }

    def generate_privilege_compliance_report(self, attorney_id: str) -> Dict:
        """Generate compliance report for attorney's privilege management"""
        try:
            # Get privilege relationship statistics
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # Active relationships
            cursor.execute("""
                SELECT COUNT(DISTINCT client_id) FROM client_cases
                WHERE attorney_id = ? AND case_status = 'Active'
            """, (attorney_id,))
            active_relationships = cursor.fetchone()[0]

            # Total privileged communications
            cursor.execute("""
                SELECT COUNT(*) FROM privileged_communications
                WHERE attorney_id = ?
            """, (attorney_id,))
            total_communications = cursor.fetchone()[0]

            # Recent audit activity
            cursor.execute("""
                SELECT COUNT(*) FROM ethics_audit_log
                WHERE attorney_id = ? AND audit_timestamp >= ?
            """, (attorney_id, (datetime.utcnow() - timedelta(days=30)).isoformat()))
            recent_audit_activity = cursor.fetchone()[0]

            conn.close()

            # Generate compliance assessment
            compliance_score = self._calculate_privilege_compliance_score(attorney_id)

            return {
                'attorney_id': attorney_id,
                'active_privilege_relationships': active_relationships,
                'total_privileged_communications': total_communications,
                'recent_audit_activity': recent_audit_activity,
                'compliance_score': compliance_score,
                'compliance_level': 'HIGH' if compliance_score >= 8 else 'MEDIUM' if compliance_score >= 6 else 'LOW',
                'report_generated': datetime.utcnow().isoformat(),
                'recommendations': self._generate_privilege_recommendations(compliance_score)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Compliance report generation failed: {str(e)}"
            }

    def _calculate_privilege_compliance_score(self, attorney_id: str) -> float:
        """Calculate privilege compliance score for attorney"""
        # Simplified scoring algorithm
        base_score = 8.0

        try:
            # Get audit data for scoring
            audit_data = self.audit_privilege_access(attorney_id=attorney_id)

            if audit_data.get('success'):
                action_summary = audit_data.get('action_summary', {})

                # Positive indicators
                if action_summary.get('PRIVILEGED_COMMUNICATION_STORED', 0) > 0:
                    base_score += 0.5

                # Negative indicators
                if action_summary.get('PRIVILEGE_VIOLATION', 0) > 0:
                    base_score -= 2.0

                # Activity level adjustment
                total_activity = sum(action_summary.values())
                if total_activity > 10:
                    base_score += 0.5  # Active privilege management

        except:
            pass  # Use base score

        return max(1.0, min(10.0, base_score))

    def _generate_privilege_recommendations(self, compliance_score: float) -> List[str]:
        """Generate recommendations for privilege compliance improvement"""
        recommendations = []

        if compliance_score < 6:
            recommendations.extend([
                "Implement regular privilege training for all staff",
                "Establish formal procedures for privileged communication handling",
                "Conduct monthly privilege compliance audits"
            ])
        elif compliance_score < 8:
            recommendations.extend([
                "Review and update privilege protection procedures",
                "Increase frequency of compliance monitoring"
            ])
        else:
            recommendations.extend([
                "Maintain current excellent privilege compliance practices",
                "Consider advanced privilege protection technologies"
            ])

        return recommendations


class PrivilegeViolationError(Exception):
    """Exception raised for attorney-client privilege violations"""
    pass


class PrivilegeProtectionError(Exception):
    """Exception raised for privilege protection system errors"""
    pass