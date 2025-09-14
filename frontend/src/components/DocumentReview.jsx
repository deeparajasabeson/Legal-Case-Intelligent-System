import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Alert,
  CircularProgress,
  Paper,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Description as DocumentIcon,
  CloudUpload as UploadIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  Share as ShareIcon
} from '@mui/icons-material';

function DocumentReview({ currentUser }) {
  const [documentData, setDocumentData] = useState({
    text: '',
    type: 'contract',
    fileName: '',
    uploadMethod: 'paste'
  });
  const [loading, setLoading] = useState(false);
  const [review, setReview] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const fileInputRef = useRef(null);

  const documentTypes = [
    { value: 'contract', label: 'Contract' },
    { value: 'agreement', label: 'Agreement' },
    { value: 'lease', label: 'Lease' },
    { value: 'employment', label: 'Employment Agreement' },
    { value: 'nda', label: 'Non-Disclosure Agreement' },
    { value: 'terms', label: 'Terms of Service' },
    { value: 'license', label: 'License Agreement' },
    { value: 'other', label: 'Other Legal Document' }
  ];

  const handleInputChange = (field) => (event) => {
    setDocumentData({
      ...documentData,
      [field]: event.target.value
    });
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type === 'text/plain') {
        const reader = new FileReader();
        reader.onload = (e) => {
          setDocumentData({
            ...documentData,
            text: e.target.result,
            fileName: file.name,
            uploadMethod: 'file'
          });
        };
        reader.readAsText(file);
      } else {
        setError('Please upload a text file (.txt)');
      }
    }
  };

  const handleReview = useCallback(async () => {
    if (!documentData.text.trim()) {
      setError('Please provide document text or upload a file');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/document-review', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_text: documentData.text,
          document_type: documentData.type,
          attorney_id: currentUser.id,
          document_name: documentData.fileName || 'Unnamed Document'
        })
      });

      const data = await response.json();

      if (data.success) {
        setReview(data.review);
        setActiveTab(1); // Switch to results tab
      } else {
        setError(data.error || 'Document review failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
      console.error('Review error:', err);
    } finally {
      setLoading(false);
    }
  }, [documentData, currentUser.id]);

  const getRiskLevel = (score) => {
    if (score >= 8) return { level: 'High', color: 'error', icon: <ErrorIcon /> };
    if (score >= 5) return { level: 'Medium', color: 'warning', icon: <WarningIcon /> };
    return { level: 'Low', color: 'success', icon: <CheckIcon /> };
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        <DocumentIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
        Document Review & Analysis
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Document Input" />
        <Tab label="Analysis Results" disabled={!review} />
      </Tabs>

      {/* Document Input Tab */}
      {activeTab === 0 && (
        <Box>
          {/* Document Type Selection */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Document Information
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Document Type</InputLabel>
                    <Select
                      value={documentData.type}
                      label="Document Type"
                      onChange={handleInputChange('type')}
                    >
                      {documentTypes.map((type) => (
                        <MenuItem key={type.value} value={type.value}>
                          {type.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Document Name (Optional)"
                    value={documentData.fileName}
                    onChange={handleInputChange('fileName')}
                    placeholder="e.g., Service Agreement v2.1"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Document Input Methods */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Document Input
              </Typography>

              {/* File Upload Option */}
              <Box sx={{ mb: 3 }}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<UploadIcon />}
                  sx={{ mb: 2 }}
                >
                  Upload Text File
                  <input
                    type="file"
                    hidden
                    accept=".txt"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                  />
                </Button>
                {documentData.uploadMethod === 'file' && documentData.fileName && (
                  <Typography variant="body2" color="text.secondary">
                    Uploaded: {documentData.fileName}
                  </Typography>
                )}
              </Box>

              <Divider sx={{ mb: 3 }}>
                <Typography variant="body2" color="text.secondary">OR</Typography>
              </Divider>

              {/* Text Paste Option */}
              <TextField
                fullWidth
                multiline
                rows={12}
                label="Paste Document Text"
                value={documentData.text}
                onChange={handleInputChange('text')}
                placeholder="Paste your legal document text here for AI-powered analysis..."
                helperText={`${documentData.text.length} characters | AI will analyze contracts, clauses, risks, and obligations`}
              />
            </CardContent>
          </Card>

          {/* Analysis Button */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleReview}
              disabled={!documentData.text.trim() || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <DocumentIcon />}
              sx={{ minWidth: 200 }}
            >
              {loading ? 'Analyzing...' : 'Analyze Document'}
            </Button>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
        </Box>
      )}

      {/* Analysis Results Tab */}
      {activeTab === 1 && review && (
        <Box>
          {/* Executive Summary */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Executive Summary
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Document Type
                    </Typography>
                    <Typography variant="h6">
                      {documentTypes.find(t => t.value === documentData.type)?.label || documentData.type}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Overall Risk Level
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 1 }}>
                      {review.overall_risk && getRiskLevel(review.overall_risk).icon}
                      <Typography variant="h6" sx={{ ml: 1 }}>
                        {review.overall_risk ? getRiskLevel(review.overall_risk).level : 'N/A'}
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Key Issues Found
                    </Typography>
                    <Typography variant="h6">
                      {review.key_issues ? review.key_issues.length : 'N/A'}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Key Issues & Risks */}
          {review.key_issues && review.key_issues.length > 0 && (
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">
                  <WarningIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'warning.main' }} />
                  Key Issues & Risks ({review.key_issues.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {review.key_issues.map((issue, index) => (
                    <ListItem key={index} divider>
                      <ListItemIcon>
                        {getRiskLevel(issue.risk_level || 5).icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={issue.issue || issue}
                        secondary={
                          issue.description && (
                            <Box sx={{ mt: 1 }}>
                              <Typography variant="body2">
                                {issue.description}
                              </Typography>
                              {issue.recommendation && (
                                <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                                  <strong>Recommendation:</strong> {issue.recommendation}
                                </Typography>
                              )}
                            </Box>
                          )
                        }
                      />
                      <Chip
                        size="small"
                        label={getRiskLevel(issue.risk_level || 5).level + ' Risk'}
                        color={getRiskLevel(issue.risk_level || 5).color}
                        variant="outlined"
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Legal Obligations */}
          {review.obligations && review.obligations.length > 0 && (
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">
                  <InfoIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'info.main' }} />
                  Legal Obligations ({review.obligations.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {review.obligations.map((obligation, index) => (
                    <ListItem key={index} divider>
                      <ListItemIcon>
                        <CheckIcon color="info" />
                      </ListItemIcon>
                      <ListItemText
                        primary={obligation.obligation || obligation}
                        secondary={obligation.party && `Responsible Party: ${obligation.party}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Clause Analysis */}
          {review.clause_analysis && (
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">
                  <DocumentIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'primary.main' }} />
                  Clause Analysis
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
                  <Typography
                    variant="body1"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.6
                    }}
                  >
                    {typeof review.clause_analysis === 'string'
                      ? review.clause_analysis
                      : JSON.stringify(review.clause_analysis, null, 2)
                    }
                  </Typography>
                </Paper>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Detailed Analysis */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detailed Legal Analysis
              </Typography>
              <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
                <Typography
                  variant="body1"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'Roboto, sans-serif',
                    lineHeight: 1.6
                  }}
                >
                  {review.detailed_analysis || review.summary || 'Analysis not available'}
                </Typography>
              </Paper>
            </CardContent>
          </Card>

          {/* Recommendations */}
          {review.recommendations && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recommendations
                </Typography>
                <Paper sx={{ p: 3, bgcolor: 'rgba(25, 118, 210, 0.1)' }}>
                  <Typography
                    variant="body1"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.6
                    }}
                  >
                    {typeof review.recommendations === 'string'
                      ? review.recommendations
                      : JSON.stringify(review.recommendations, null, 2)
                    }
                  </Typography>
                </Paper>
              </CardContent>
            </Card>
          )}

          {/* Action Items */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Next Steps
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <ViewIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Review identified risks with client"
                    secondary="Discuss potential modifications and risk tolerance"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <DocumentIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Draft amendments if needed"
                    secondary="Address high-risk clauses and missing provisions"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <CheckIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Obtain additional legal review"
                    secondary="For complex or high-value agreements"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Legal Disclaimer */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Document Review Disclaimer:</strong> This AI-powered analysis is for preliminary review only
          and does not replace professional legal judgment. All document reviews are confidential and protected
          under attorney-client privilege.
        </Typography>
      </Alert>
    </Box>
  );
}

export default DocumentReview;