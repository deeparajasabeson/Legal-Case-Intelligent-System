-- Legal AI Database Schema

-- Case law table
CREATE TABLE case_law (
    case_id TEXT PRIMARY KEY,
    case_name TEXT NOT NULL,
    court TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    decision_date DATE NOT NULL,
    legal_issues TEXT NOT NULL,
    holding TEXT NOT NULL,
    citation TEXT NOT NULL,
    full_text TEXT NOT NULL,
    case_category TEXT,
    legal_area TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Legal precedents table
CREATE TABLE legal_precedents (
    precedent_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    legal_principle TEXT NOT NULL,
    binding_authority TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    precedent_weight INTEGER DEFAULT 5,
    related_statutes TEXT,
    applicability_score REAL DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES case_law (case_id)
);

-- Statutes table
CREATE TABLE statutes (
    statute_id TEXT PRIMARY KEY,
    statute_title TEXT NOT NULL,
    code_section TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    statute_text TEXT NOT NULL,
    effective_date DATE,
    last_updated DATE,
    legal_area TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contracts table
CREATE TABLE contracts (
    contract_id TEXT PRIMARY KEY,
    contract_type TEXT NOT NULL,
    contract_name TEXT NOT NULL,
    contract_text TEXT NOT NULL,
    standard_clauses TEXT,
    risk_factors TEXT,
    enforceability_score REAL DEFAULT 0.7,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Court records table
CREATE TABLE court_records (
    record_id TEXT PRIMARY KEY,
    case_id TEXT,
    record_type TEXT NOT NULL,
    filing_date DATE NOT NULL,
    court TEXT NOT NULL,
    parties TEXT NOT NULL,
    document_text TEXT NOT NULL,
    legal_issues TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES case_law (case_id)
);

-- Legal entities table
CREATE TABLE legal_entities (
    entity_id TEXT PRIMARY KEY,
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    jurisdiction TEXT,
    contact_info TEXT,
    practice_areas TEXT,
    bar_number TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Client cases table
CREATE TABLE client_cases (
    case_id TEXT PRIMARY KEY,
    attorney_id TEXT NOT NULL,
    client_id TEXT NOT NULL,
    case_name TEXT NOT NULL,
    case_type TEXT NOT NULL,
    case_status TEXT DEFAULT 'Active',
    case_facts TEXT,
    legal_issues TEXT,
    strategy_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attorney-client communications (encrypted)
CREATE TABLE privileged_communications (
    comm_id TEXT PRIMARY KEY,
    attorney_id TEXT NOT NULL,
    client_id TEXT NOT NULL,
    communication_text TEXT NOT NULL, -- Encrypted
    communication_type TEXT NOT NULL,
    privilege_level TEXT DEFAULT 'full',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ethics audit log
CREATE TABLE ethics_audit_log (
    audit_id TEXT PRIMARY KEY,
    attorney_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    action_details TEXT,
    compliance_status TEXT DEFAULT 'compliant',
    audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Legal research history
CREATE TABLE research_history (
    research_id TEXT PRIMARY KEY,
    attorney_id TEXT NOT NULL,
    query TEXT NOT NULL,
    jurisdiction TEXT,
    research_results TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_case_law_jurisdiction ON case_law(jurisdiction);
CREATE INDEX idx_case_law_legal_area ON case_law(legal_area);
CREATE INDEX idx_precedents_jurisdiction ON legal_precedents(jurisdiction);
CREATE INDEX idx_statutes_jurisdiction ON statutes(jurisdiction);
CREATE INDEX idx_client_cases_attorney ON client_cases(attorney_id);
CREATE INDEX idx_privileged_comms_attorney_client ON privileged_communications(attorney_id, client_id);

-- Insert sample legal data for testing

-- Sample attorneys
INSERT OR IGNORE INTO legal_entities (entity_id, entity_name, entity_type, jurisdiction, bar_number) VALUES
('att_001', 'Attorney Smith', 'attorney', 'California', 'CA12345'),
('att_002', 'Attorney Johnson', 'attorney', 'New York', 'NY67890');

-- Sample clients
INSERT OR IGNORE INTO legal_entities (entity_id, entity_name, entity_type, jurisdiction) VALUES
('CLIENT_001', 'Smith Corporation', 'corporation', 'California'),
('CLIENT_002', 'Johnson LLC', 'llc', 'New York');

-- Sample case law
INSERT OR IGNORE INTO case_law (case_id, case_name, court, jurisdiction, decision_date, legal_issues, holding, citation, full_text, legal_area) VALUES
('CASE_001', 'Smith v. Johnson', 'Supreme Court', 'Federal', '2020-06-15', 'Breach of contract damages', 'Compensatory damages awarded for material breach', '123 U.S. 456 (2020)', 'Contract dispute regarding software licensing agreement...', 'Contract Law'),
('CASE_002', 'Brown v. ABC Corp', 'Circuit Court', 'California', '2021-03-10', 'Employment discrimination', 'Employee rights protected under state law', '789 Cal.App. 123 (2021)', 'Employment discrimination case involving wrongful termination...', 'Employment Law'),
('CASE_003', 'Davis v. Insurance Co', 'District Court', 'New York', '2019-11-20', 'Insurance bad faith', 'Punitive damages allowed for bad faith denial', '456 F.Supp. 789 (2019)', 'Insurance company denied claim without reasonable basis...', 'Insurance Law'),
('CASE_004', 'Wilson v. Tech Inc', 'Court of Appeals', 'Federal', '2022-01-30', 'Intellectual property infringement', 'Patent infringement requires clear and convincing evidence', '321 F.3d 654 (2022)', 'Patent dispute over software algorithm...', 'IP Law'),
('CASE_005', 'Miller v. State Bank', 'Supreme Court', 'California', '2021-09-05', 'Consumer protection violation', 'Banks must disclose all fees under state consumer law', '987 Cal.4th 321 (2021)', 'Consumer sued bank for undisclosed fees...', 'Consumer Law');

-- Sample statutes
INSERT OR IGNORE INTO statutes (statute_id, statute_title, code_section, jurisdiction, statute_text, effective_date, legal_area) VALUES
('STAT_001', 'Consumer Protection Act', '15 USC 45', 'Federal', 'Prohibits unfair or deceptive practices in commerce affecting consumers', '1975-01-01', 'Consumer Law'),
('STAT_002', 'Employment Standards Act', 'Labor Code 200', 'California', 'Establishes minimum wage and working conditions for employees', '1976-01-01', 'Employment Law'),
('STAT_003', 'Contract Statute of Limitations', 'Civil Code 337', 'California', 'Four-year limitation period for actions on written contracts', '1872-01-01', 'Contract Law'),
('STAT_004', 'Patent Act', '35 USC 101', 'Federal', 'Defines patentable subject matter for inventions', '1952-07-19', 'IP Law'),
('STAT_005', 'Truth in Lending Act', '15 USC 1601', 'Federal', 'Requires disclosure of credit terms to consumers', '1968-05-29', 'Consumer Law');

-- Sample legal precedents
INSERT OR IGNORE INTO legal_precedents (precedent_id, case_id, legal_principle, binding_authority, jurisdiction, precedent_weight, related_statutes) VALUES
('PREC_001', 'CASE_001', 'Expectation damages for breach of contract', 'Binding', 'Federal', 9, 'UCC 2-712, 2-713'),
('PREC_002', 'CASE_002', 'At-will employment exceptions for discrimination', 'Binding', 'California', 8, 'Labor Code 1102.5'),
('PREC_003', 'CASE_003', 'Insurance bad faith requires unreasonable conduct', 'Persuasive', 'New York', 7, 'Insurance Code 790.03'),
('PREC_004', 'CASE_004', 'Clear and convincing evidence standard for patents', 'Binding', 'Federal', 9, '35 USC 282'),
('PREC_005', 'CASE_005', 'Consumer protection requires clear disclosure', 'Binding', 'California', 8, 'Civil Code 1750');

-- Sample contracts
INSERT OR IGNORE INTO contracts (contract_id, contract_type, contract_name, contract_text, standard_clauses, risk_factors) VALUES
('CONT_001', 'employment', 'Software Engineer Employment Agreement', 'Employment agreement for software engineer position...', 'At-will employment, confidentiality, non-compete', 'Non-compete enforceability varies by state'),
('CONT_002', 'service', 'IT Services Agreement', 'Agreement for managed IT services...', 'Service level agreements, limitation of liability, termination', 'Service level penalties, data security requirements'),
('CONT_003', 'nda', 'Mutual Non-Disclosure Agreement', 'Mutual confidentiality agreement for business discussions...', 'Confidential information definition, use restrictions, term', 'Overly broad definitions, enforcement challenges'),
('CONT_004', 'license', 'Software License Agreement', 'License for use of proprietary software...', 'Grant of license, restrictions, warranty disclaimers', 'Scope of license, update obligations'),
('CONT_005', 'purchase', 'Equipment Purchase Agreement', 'Agreement for purchase of office equipment...', 'Purchase price, delivery terms, warranties', 'Title transfer, risk of loss, inspection rights');

-- Sample client cases
INSERT OR IGNORE INTO client_cases (case_id, attorney_id, client_id, case_name, case_type, case_facts, legal_issues) VALUES
('CC_001', 'att_001', 'CLIENT_001', 'Contract Dispute Matter', 'contract', 'Client signed software license agreement but vendor failed to deliver', 'Breach of contract, damages calculation'),
('CC_002', 'att_001', 'CLIENT_002', 'Employment Issue', 'employment', 'Employee claims wrongful termination after reporting safety violations', 'Wrongful termination, whistleblower protection');