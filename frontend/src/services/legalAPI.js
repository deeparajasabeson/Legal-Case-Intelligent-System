// Legal Research API Service
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for legal research
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for authentication
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('legal_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);

    if (error.response?.status === 401) {
      // Handle authentication errors
      localStorage.removeItem('legal_token');
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

export const legalResearchAPI = {
  // Conduct comprehensive legal research
  conductResearch: async (query, jurisdiction = 'Federal', attorneyId) => {
    try {
      const response = await apiClient.post('/api/legal-research', {
        query,
        jurisdiction,
        attorney_id: attorneyId
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Legal research failed');
    }
  },

  // Analyze specific legal issue with case facts
  analyzeLegalIssue: async (legalIssue, caseFacts, jurisdiction = 'Federal', attorneyId) => {
    try {
      const response = await apiClient.post('/api/legal-research/analyze', {
        legal_issue: legalIssue,
        case_facts: caseFacts,
        jurisdiction,
        attorney_id: attorneyId
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Legal analysis failed');
    }
  },

  // Get research history for attorney
  getResearchHistory: async (attorneyId, limit = 10) => {
    try {
      const response = await apiClient.get(`/api/legal-research/history?attorney_id=${attorneyId}&limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load research history');
    }
  },

  // Search legal database directly
  searchDatabase: async (searchParams) => {
    try {
      const response = await apiClient.post('/api/legal-research/search', searchParams);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Database search failed');
    }
  }
};

export const caseAnalysisAPI = {
  // Analyze case merits and strength
  analyzeCaseStrength: async (caseData) => {
    try {
      const response = await apiClient.post('/api/case-analysis', caseData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Case analysis failed');
    }
  },

  // Get case analysis templates
  getAnalysisTemplates: async (caseType) => {
    try {
      const response = await apiClient.get(`/api/case-analysis/templates?type=${caseType}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load templates');
    }
  },

  // Save case analysis
  saveCaseAnalysis: async (analysisData) => {
    try {
      const response = await apiClient.post('/api/case-analysis/save', analysisData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to save analysis');
    }
  }
};

export const documentReviewAPI = {
  // Review and analyze legal document
  reviewDocument: async (documentData) => {
    try {
      const response = await apiClient.post('/api/document-review', documentData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Document review failed');
    }
  },

  // Get document templates and clauses
  getDocumentTemplates: async (documentType) => {
    try {
      const response = await apiClient.get(`/api/document-review/templates?type=${documentType}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load templates');
    }
  },

  // Analyze specific contract clause
  analyzeClause: async (clauseText, documentType) => {
    try {
      const response = await apiClient.post('/api/document-review/clause', {
        clause_text: clauseText,
        document_type: documentType
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Clause analysis failed');
    }
  }
};

export const precedentAPI = {
  // Search for legal precedents
  searchPrecedents: async (searchData) => {
    try {
      const response = await apiClient.post('/api/precedent-search', searchData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Precedent search failed');
    }
  },

  // Get detailed precedent information
  getPrecedentDetails: async (precedentId) => {
    try {
      const response = await apiClient.get(`/api/precedent-search/${precedentId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load precedent details');
    }
  },

  // Save precedent to favorites
  savePrecedent: async (precedentId, attorneyId) => {
    try {
      const response = await apiClient.post('/api/precedent-search/save', {
        precedent_id: precedentId,
        attorney_id: attorneyId
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to save precedent');
    }
  }
};

export const ragAPI = {
  // Perform RAG-powered legal search
  performSearch: async (query, caseContext = {}) => {
    try {
      const response = await apiClient.post('/api/rag-search', {
        query,
        case_context: caseContext
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'RAG search failed');
    }
  }
};

export const ethicsAPI = {
  // Get ethics compliance status
  getComplianceStatus: async (attorneyId) => {
    try {
      const response = await apiClient.get(`/api/ethics-compliance?attorney_id=${attorneyId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to load compliance status');
    }
  },

  // Report ethics violation or concern
  reportEthicsIssue: async (issueData) => {
    try {
      const response = await apiClient.post('/api/ethics-compliance/report', issueData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to report ethics issue');
    }
  },

  // Generate compliance report
  generateComplianceReport: async (attorneyId, reportType = 'monthly') => {
    try {
      const response = await apiClient.post('/api/ethics-compliance/report', {
        attorney_id: attorneyId,
        report_type: reportType
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to generate report');
    }
  }
};

// Health check API
export const healthAPI = {
  checkHealth: async () => {
    try {
      const response = await apiClient.get('/api/health');
      return response.data;
    } catch (error) {
      throw new Error('Health check failed');
    }
  }
};

// Error handling utility
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.error || error.response.data?.message || 'Server error occurred';
    return {
      type: 'server_error',
      message,
      status: error.response.status
    };
  } else if (error.request) {
    // Network error
    return {
      type: 'network_error',
      message: 'Network error. Please check your connection.',
      status: null
    };
  } else {
    // Other error
    return {
      type: 'client_error',
      message: error.message || 'An unexpected error occurred',
      status: null
    };
  }
};

export default {
  legalResearchAPI,
  caseAnalysisAPI,
  documentReviewAPI,
  precedentAPI,
  ragAPI,
  ethicsAPI,
  healthAPI,
  handleApiError
};