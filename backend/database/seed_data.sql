-- Sample legal data for Legal AI System

-- Sample case law
INSERT INTO case_law (case_id, case_name, court, jurisdiction, decision_date, legal_issues, holding, citation, full_text, case_category, legal_area) VALUES
('case_001', 'Miranda v. Arizona', 'U.S. Supreme Court', 'Federal', '1966-06-13', 'Fifth Amendment rights, custodial interrogation', 'Suspects must be informed of their constitutional rights before custodial interrogation', '384 U.S. 436 (1966)', 'The Supreme Court held that defendants have the right to remain silent and to an attorney during police interrogation.', 'Criminal', 'Constitutional Law'),
('case_002', 'Brown v. Board of Education', 'U.S. Supreme Court', 'Federal', '1954-05-17', 'Equal protection, racial segregation in schools', 'Separate educational facilities are inherently unequal', '347 U.S. 483 (1954)', 'Landmark case that declared state laws establishing separate public schools for black and white students to be unconstitutional.', 'Civil Rights', 'Constitutional Law'),
('case_003', 'Roe v. Wade', 'U.S. Supreme Court', 'Federal', '1973-01-22', 'Privacy rights, abortion regulation', 'Women have a constitutional right to abortion under certain circumstances', '410 U.S. 113 (1973)', 'The Court ruled that the Constitution protects a womans right to choose to have an abortion without excessive government restriction.', 'Civil Rights', 'Constitutional Law'),
('case_004', 'Hadley v. Baxendale', 'Court of Exchequer', 'English', '1854-02-01', 'Contract damages, foreseeability', 'Damages for breach of contract limited to those reasonably foreseeable', '9 Exch. 341 (1854)', 'Established the principle that damages for breach of contract should be limited to those that were reasonably foreseeable at the time of contracting.', 'Contract', 'Contract Law'),
('case_005', 'Marbury v. Madison', 'U.S. Supreme Court', 'Federal', '1803-02-24', 'Judicial review, separation of powers', 'Supreme Court has power to declare laws unconstitutional', '5 U.S. 137 (1803)', 'Established the principle of judicial review, giving federal courts the power to declare legislative and executive acts unconstitutional.', 'Constitutional', 'Constitutional Law');

-- Sample legal precedents
INSERT INTO legal_precedents (precedent_id, case_id, legal_principle, binding_authority, jurisdiction, precedent_weight, related_statutes) VALUES
('prec_001', 'case_001', 'Miranda Rights must be read before custodial interrogation', 'Supreme Court Decision', 'Federal', 10, 'Fifth Amendment, Sixth Amendment'),
('prec_002', 'case_002', 'Separate but equal doctrine is unconstitutional in public education', 'Supreme Court Decision', 'Federal', 10, 'Fourteenth Amendment'),
('prec_003', 'case_003', 'Privacy right includes reproductive autonomy', 'Supreme Court Decision', 'Federal', 9, 'Fourteenth Amendment'),
('prec_004', 'case_004', 'Contract damages limited to foreseeable harm', 'Court of Exchequer', 'English', 8, 'Common Law Contract Principles'),
('prec_005', 'case_005', 'Courts have power to review constitutionality of laws', 'Supreme Court Decision', 'Federal', 10, 'Article III Constitution');

-- Sample statutes
INSERT INTO statutes (statute_id, statute_title, code_section, jurisdiction, statute_text, effective_date, legal_area) VALUES
('stat_001', 'Americans with Disabilities Act', '42 U.S.C. § 12101', 'Federal', 'Prohibits discrimination based on disability in employment, public accommodations, and other areas', '1990-07-26', 'Civil Rights'),
('stat_002', 'Securities Exchange Act', '15 U.S.C. § 78', 'Federal', 'Regulates securities trading and provides framework for securities markets', '1934-06-06', 'Securities'),
('stat_003', 'Fair Labor Standards Act', '29 U.S.C. § 201', 'Federal', 'Establishes minimum wage, overtime pay, recordkeeping, and youth employment standards', '1938-06-25', 'Employment'),
('stat_004', 'Uniform Commercial Code Article 2', 'UCC § 2-101', 'State Model', 'Governs transactions in goods between merchants and consumers', '1962-01-01', 'Commercial'),
('stat_005', 'Civil Rights Act of 1964', '42 U.S.C. § 2000e', 'Federal', 'Prohibits employment discrimination based on race, color, religion, sex, or national origin', '1964-07-02', 'Civil Rights');

-- Sample contracts
INSERT INTO contracts (contract_id, contract_type, contract_name, contract_text, standard_clauses, risk_factors) VALUES
('cont_001', 'Employment', 'Standard Employment Agreement', 'This agreement establishes the terms of employment between employer and employee...', 'At-will employment, confidentiality, non-compete', 'Non-compete enforceability varies by state'),
('cont_002', 'NDA', 'Non-Disclosure Agreement', 'The parties agree to maintain confidentiality of proprietary information...', 'Definition of confidential info, return of materials, duration', 'Overly broad definitions may be unenforceable'),
('cont_003', 'Service Agreement', 'Professional Services Contract', 'Contractor agrees to provide specified services in exchange for payment...', 'Scope of work, payment terms, intellectual property', 'Independent contractor classification risks'),
('cont_004', 'Purchase Agreement', 'Asset Purchase Agreement', 'Buyer agrees to purchase specified assets from Seller...', 'Representations, warranties, indemnification', 'Due diligence limitations, unknown liabilities'),
('cont_005', 'Lease Agreement', 'Commercial Lease', 'Landlord leases premises to Tenant for commercial purposes...', 'Rent escalation, maintenance obligations, default terms', 'Personal guarantees, environmental liability');

-- Sample court records
INSERT INTO court_records (record_id, case_id, record_type, filing_date, court, parties, document_text, legal_issues) VALUES
('rec_001', 'case_001', 'Opinion', '1966-06-13', 'U.S. Supreme Court', 'Miranda v. Arizona', 'The procedural safeguards we adopt today...', 'Fifth Amendment, custodial interrogation'),
('rec_002', 'case_002', 'Opinion', '1954-05-17', 'U.S. Supreme Court', 'Brown v. Board of Education', 'We conclude that in the field of public education...', 'Equal protection, school segregation'),
('rec_003', 'case_003', 'Motion', '1972-12-01', 'U.S. District Court', 'Roe v. Wade', 'Plaintiff moves for summary judgment...', 'Privacy rights, state regulation'),
('rec_004', 'case_004', 'Judgment', '1854-02-01', 'Court of Exchequer', 'Hadley v. Baxendale', 'The damages must be such as may fairly...', 'Contract damages, foreseeability'),
('rec_005', 'case_005', 'Opinion', '1803-02-24', 'U.S. Supreme Court', 'Marbury v. Madison', 'It is emphatically the province and duty...', 'Judicial review, constitutional interpretation');

-- Sample legal entities
INSERT INTO legal_entities (entity_id, entity_name, entity_type, jurisdiction, practice_areas, bar_number) VALUES
('ent_001', 'Supreme Court of the United States', 'Court', 'Federal', 'Constitutional Law, Federal Law', NULL),
('ent_002', 'American Bar Association', 'Professional Organization', 'National', 'Legal Ethics, Professional Standards', NULL),
('ent_003', 'John Smith, Esq.', 'Attorney', 'California', 'Corporate Law, Securities', 'CA12345'),
('ent_004', 'Jane Doe, Esq.', 'Attorney', 'New York', 'Employment Law, Civil Rights', 'NY67890'),
('ent_005', 'Legal Aid Society', 'Non-Profit', 'Multi-State', 'Public Interest, Criminal Defense', NULL);

-- Sample client cases
INSERT INTO client_cases (case_id, attorney_id, client_id, case_name, case_type, case_facts, legal_issues, strategy_notes) VALUES
('client_001', 'att_001', 'cli_001', 'Employment Discrimination Case', 'Employment', 'Client terminated after filing EEOC complaint', 'Retaliation, wrongful termination', 'Strong case, document timeline carefully'),
('client_002', 'att_002', 'cli_002', 'Contract Dispute', 'Contract', 'Breach of service agreement by vendor', 'Material breach, damages calculation', 'Review force majeure clause applicability'),
('client_003', 'att_001', 'cli_003', 'Personal Injury', 'Tort', 'Slip and fall at commercial property', 'Premises liability, negligence', 'Obtain security footage, witness statements'),
('client_004', 'att_003', 'cli_004', 'Intellectual Property Dispute', 'IP', 'Patent infringement allegations', 'Patent validity, infringement analysis', 'Prior art search needed'),
('client_005', 'att_002', 'cli_005', 'Corporate Merger', 'Corporate', 'M&A transaction regulatory approval', 'Antitrust, securities compliance', 'HSR filing requirements');

-- Sample research history
INSERT INTO research_history (research_id, attorney_id, query, jurisdiction, research_results) VALUES
('res_001', 'att_001', 'employment at-will exceptions', 'California', 'Found public policy exception cases'),
('res_002', 'att_002', 'force majeure COVID-19', 'Federal', 'Mixed results on pandemic as force majeure'),
('res_003', 'att_003', 'patent claim construction', 'Federal Circuit', 'Recent trends in claim interpretation'),
('res_004', 'att_001', 'premises liability standards', 'Multi-State', 'State-by-state liability standards'),
('res_005', 'att_002', 'merger antitrust thresholds', 'Federal', 'Current HSR thresholds and DOJ guidance');