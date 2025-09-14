// Legal Citation Formatting Utilities
// Follows The Bluebook: A Uniform System of Citation standards

/**
 * Format case citation according to Bluebook standards
 * @param {Object} caseData - Case information
 * @returns {string} Formatted citation
 */
export const formatCaseCitation = (caseData) => {
  if (!caseData) return '';

  const {
    case_name,
    volume,
    reporter,
    page,
    court,
    year,
    jurisdiction
  } = caseData;

  if (!case_name) return '';

  // Basic case name formatting
  let citation = case_name;

  // Add volume, reporter, and page if available
  if (volume && reporter && page) {
    citation += `, ${volume} ${reporter} ${page}`;
  }

  // Add court and year if available
  if (court && year) {
    citation += ` (${court} ${year})`;
  } else if (year) {
    citation += ` (${year})`;
  }

  return citation;
};

/**
 * Format statute citation according to Bluebook standards
 * @param {Object} statuteData - Statute information
 * @returns {string} Formatted citation
 */
export const formatStatuteCitation = (statuteData) => {
  if (!statuteData) return '';

  const {
    title,
    code_section,
    code_name,
    jurisdiction,
    year,
    publisher
  } = statuteData;

  if (!title && !code_section) return '';

  let citation = '';

  // Federal statute format: Title U.S.C. § Section (Year)
  if (jurisdiction === 'Federal' || jurisdiction === 'federal') {
    if (title && code_section) {
      citation = `${title} U.S.C. § ${code_section}`;
      if (year) {
        citation += ` (${year})`;
      }
    }
  } else {
    // State statute format: State Code § Section (Year)
    if (code_name && code_section) {
      citation = `${code_name} § ${code_section}`;
    } else if (title && code_section) {
      citation = `${jurisdiction || 'State'} Code § ${code_section}`;
    }

    if (year) {
      citation += ` (${year})`;
    }
  }

  return citation;
};

/**
 * Format constitutional citation
 * @param {Object} constitutionData - Constitution information
 * @returns {string} Formatted citation
 */
export const formatConstitutionalCitation = (constitutionData) => {
  if (!constitutionData) return '';

  const {
    article,
    section,
    clause,
    amendment,
    jurisdiction = 'U.S.'
  } = constitutionData;

  let citation = '';

  if (jurisdiction === 'U.S.' || jurisdiction === 'Federal') {
    // Federal constitution
    if (amendment) {
      citation = `U.S. Const. amend. ${amendment}`;
      if (section) {
        citation += `, § ${section}`;
      }
    } else if (article) {
      citation = `U.S. Const. art. ${article}`;
      if (section) {
        citation += `, § ${section}`;
      }
      if (clause) {
        citation += `, cl. ${clause}`;
      }
    }
  } else {
    // State constitution
    citation = `${jurisdiction} Const.`;
    if (article) {
      citation += ` art. ${article}`;
    }
    if (section) {
      citation += `, § ${section}`;
    }
  }

  return citation;
};

/**
 * Format law review or journal citation
 * @param {Object} articleData - Article information
 * @returns {string} Formatted citation
 */
export const formatJournalCitation = (articleData) => {
  if (!articleData) return '';

  const {
    author,
    title,
    volume,
    journal,
    page,
    year
  } = articleData;

  if (!title || !journal) return '';

  let citation = '';

  // Author, Title, Volume Journal Page (Year)
  if (author) {
    citation += `${author}, `;
  }

  citation += `${title}`;

  if (volume && page) {
    citation += `, ${volume} ${journal} ${page}`;
  } else {
    citation += `, ${journal}`;
  }

  if (year) {
    citation += ` (${year})`;
  }

  return citation;
};

/**
 * Format book citation
 * @param {Object} bookData - Book information
 * @returns {string} Formatted citation
 */
export const formatBookCitation = (bookData) => {
  if (!bookData) return '';

  const {
    author,
    title,
    page,
    edition,
    year,
    publisher
  } = bookData;

  if (!author || !title) return '';

  let citation = `${author}, ${title}`;

  if (page) {
    citation += `, at ${page}`;
  }

  // Add edition and publication information
  let pubInfo = [];
  if (edition && edition !== '1') {
    pubInfo.push(`${edition} ed.`);
  }
  if (year) {
    pubInfo.push(year);
  }

  if (pubInfo.length > 0) {
    citation += ` (${pubInfo.join(' ')})`;
  }

  return citation;
};

/**
 * Format regulation citation
 * @param {Object} regulationData - Regulation information
 * @returns {string} Formatted citation
 */
export const formatRegulationCitation = (regulationData) => {
  if (!regulationData) return '';

  const {
    title,
    section,
    year,
    jurisdiction
  } = regulationData;

  if (!title || !section) return '';

  let citation = '';

  if (jurisdiction === 'Federal' || jurisdiction === 'federal') {
    // Federal regulation: Title C.F.R. § Section (Year)
    citation = `${title} C.F.R. § ${section}`;
  } else {
    // State regulation
    citation = `${jurisdiction || 'State'} Reg. § ${section}`;
  }

  if (year) {
    citation += ` (${year})`;
  }

  return citation;
};

/**
 * Validate citation format
 * @param {string} citation - Citation to validate
 * @param {string} type - Type of citation (case, statute, etc.)
 * @returns {Object} Validation result
 */
export const validateCitation = (citation, type = 'case') => {
  if (!citation || typeof citation !== 'string') {
    return {
      isValid: false,
      errors: ['Citation is required and must be a string'],
      suggestions: []
    };
  }

  const errors = [];
  const suggestions = [];

  switch (type) {
    case 'case':
      // Basic case citation validation
      if (!citation.includes('v.') && !citation.includes(' v ')) {
        errors.push('Case name should include "v." between parties');
        suggestions.push('Format: Plaintiff v. Defendant, Citation (Court Year)');
      }
      break;

    case 'statute':
      // Basic statute validation
      if (!citation.includes('§') && !citation.includes('sec.')) {
        errors.push('Statute citation should include section symbol (§)');
        suggestions.push('Format: Title Code § Section (Year)');
      }
      break;

    case 'constitution':
      // Constitution validation
      if (!citation.includes('Const.')) {
        errors.push('Constitutional citation should include "Const."');
        suggestions.push('Format: U.S. Const. art. I, § 8 or U.S. Const. amend. XIV');
      }
      break;

    default:
      break;
  }

  return {
    isValid: errors.length === 0,
    errors,
    suggestions
  };
};

/**
 * Extract citation components from formatted citation
 * @param {string} citation - Formatted citation
 * @param {string} type - Type of citation
 * @returns {Object} Citation components
 */
export const parseCitation = (citation, type = 'case') => {
  if (!citation) return null;

  const result = {
    original: citation,
    type,
    components: {}
  };

  try {
    switch (type) {
      case 'case':
        // Parse case citation: Case Name, Volume Reporter Page (Court Year)
        const caseMatch = citation.match(/^(.+?),\s*(\d+)\s+(.+?)\s+(\d+)\s*\((.+?)\s+(\d{4})\)$/);
        if (caseMatch) {
          result.components = {
            case_name: caseMatch[1].trim(),
            volume: caseMatch[2],
            reporter: caseMatch[3],
            page: caseMatch[4],
            court: caseMatch[5],
            year: caseMatch[6]
          };
        }
        break;

      case 'statute':
        // Parse statute citation: Title Code § Section (Year)
        const statuteMatch = citation.match(/^(\d+)\s+(.+?)\s+§\s+([^\s\(]+)(?:\s*\((\d{4})\))?$/);
        if (statuteMatch) {
          result.components = {
            title: statuteMatch[1],
            code_name: statuteMatch[2],
            section: statuteMatch[3],
            year: statuteMatch[4]
          };
        }
        break;

      default:
        result.components = { text: citation };
    }
  } catch (error) {
    console.error('Citation parsing error:', error);
    result.components = { text: citation, error: error.message };
  }

  return result;
};

/**
 * Generate short form citation
 * @param {string} fullCitation - Full citation
 * @param {string} type - Citation type
 * @returns {string} Short form citation
 */
export const generateShortForm = (fullCitation, type = 'case') => {
  if (!fullCitation) return '';

  try {
    switch (type) {
      case 'case':
        // Extract case name for short form
        const match = fullCitation.match(/^([^,]+)/);
        if (match) {
          const caseName = match[1];
          // Use first named party for short form
          const firstParty = caseName.split(/\s+v\.?\s+/)[0];
          return firstParty;
        }
        break;

      case 'statute':
        // Use section for short form
        const sectionMatch = fullCitation.match(/§\s*([^\s\(]+)/);
        if (sectionMatch) {
          return `§ ${sectionMatch[1]}`;
        }
        break;

      default:
        return fullCitation;
    }
  } catch (error) {
    console.error('Short form generation error:', error);
  }

  return fullCitation;
};

/**
 * Format multiple citations in a string
 * @param {Array} citations - Array of citation objects
 * @param {string} format - Format style ('bluebook', 'apa', 'mla')
 * @returns {string} Formatted citation string
 */
export const formatMultipleCitations = (citations, format = 'bluebook') => {
  if (!Array.isArray(citations) || citations.length === 0) return '';

  const formattedCitations = citations.map(citation => {
    switch (citation.type) {
      case 'case':
        return formatCaseCitation(citation);
      case 'statute':
        return formatStatuteCitation(citation);
      case 'constitution':
        return formatConstitutionalCitation(citation);
      case 'journal':
        return formatJournalCitation(citation);
      case 'book':
        return formatBookCitation(citation);
      case 'regulation':
        return formatRegulationCitation(citation);
      default:
        return citation.citation || citation.text || '';
    }
  }).filter(citation => citation.trim() !== '');

  // Join citations with semicolons for Bluebook style
  return formattedCitations.join('; ');
};

export default {
  formatCaseCitation,
  formatStatuteCitation,
  formatConstitutionalCitation,
  formatJournalCitation,
  formatBookCitation,
  formatRegulationCitation,
  validateCitation,
  parseCitation,
  generateShortForm,
  formatMultipleCitations
};