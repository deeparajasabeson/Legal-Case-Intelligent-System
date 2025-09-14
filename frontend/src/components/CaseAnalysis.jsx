import React, { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Rating,
  Chip,
  Divider,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Gavel as GavelIcon,
  TrendingUp as StrengthIcon,
  Warning as RiskIcon,
  Lightbulb as StrategyIcon,
  Security as PrivilegeIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material';

function CaseAnalysis({ currentUser }) {
  const [caseData, setCaseData] = useState({
    caseName: '',
    clientId: '',
    caseFacts: '',
    legalIssues: '',
    desiredOutcome: ''
  });
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [privilegeWarning, setPrivilegeWarning] = useState(false);
  const [activeStep, setActiveStep] = useState(0);

  const analysisSteps = [
    'Case Information',
    'Legal Issues',
    'Analysis Results'
  ];

  const handleInputChange = (field) => (event) => {
    setCaseData({
      ...caseData,
      [field]: event.target.value
    });
  };

  const handleAnalyze = useCallback(async () => {
    if (!caseData.caseFacts.trim() || !caseData.legalIssues.trim()) {
      setError('Please provide case facts and legal issues');
      return;
    }

    if (!caseData.clientId.trim()) {
      setPrivilegeWarning(true);
      return;
    }

    setLoading(true);
    setError('');
    setActiveStep(2);

    try {
      const response = await fetch('/api/case-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_facts: caseData.caseFacts,
          legal_issues: caseData.legalIssues,
          case_name: caseData.caseName,
          desired_outcome: caseData.desiredOutcome,
          attorney_id: currentUser.id,
          client_id: caseData.clientId
        })
      });

      const data = await response.json();

      if (data.success) {
        setAnalysis(data.analysis);
      } else {
        setError(data.error || 'Case analysis failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  }, [caseData, currentUser.id]);

  const getStrengthColor = (score) => {
    if (score >= 8) return 'success';
    if (score >= 6) return 'warning';
    return 'error';
  };

  const getStrengthIcon = (score) => {
    if (score >= 7) return <CheckCircleIcon color="success" />;
    if (score >= 4) return <InfoIcon color="warning" />;
    return <ErrorIcon color="error" />;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        <AssessmentIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
        Case Analysis
      </Typography>

      <Stepper activeStep={activeStep} orientation="vertical">
        {/* Step 1: Case Information */}
        <Step>
          <StepLabel>Case Information</StepLabel>
          <StepContent>
            <Card>
              <CardContent>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Case Name"
                      value={caseData.caseName}
                      onChange={handleInputChange('caseName')}
                      placeholder="e.g., Smith v. ABC Corp"
                      helperText="Internal case identifier"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      required
                      label="Client ID"
                      value={caseData.clientId}
                      onChange={handleInputChange('clientId')}
                      placeholder="e.g., CLIENT_001"
                      helperText="Required for attorney-client privilege"
                      InputProps={{
                        startAdornment: <PrivilegeIcon sx={{ mr: 1, color: 'primary.main' }} />
                      }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      required
                      label="Case Facts"
                      value={caseData.caseFacts}
                      onChange={handleInputChange('caseFacts')}
                      placeholder="Describe the key facts of the case, including dates, parties, and relevant circumstances..."
                      helperText="Provide detailed factual background"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button
                      variant="contained"
                      onClick={() => setActiveStep(1)}
                      disabled={!caseData.caseFacts.trim()}
                    >
                      Next: Legal Issues
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </StepContent>
        </Step>

        {/* Step 2: Legal Issues */}
        <Step>
          <StepLabel>Legal Issues</StepLabel>
          <StepContent>
            <Card>
              <CardContent>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      required
                      label="Legal Issues"
                      value={caseData.legalIssues}
                      onChange={handleInputChange('legalIssues')}
                      placeholder="Identify the key legal issues, claims, or causes of action..."
                      helperText="Specify the legal questions to be analyzed"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={2}
                      label="Desired Outcome"
                      value={caseData.desiredOutcome}
                      onChange={handleInputChange('desiredOutcome')}
                      placeholder="What outcome does the client seek? (damages, injunction, etc.)"
                      helperText="Client's objectives and desired relief"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Button
                        variant="outlined"
                        onClick={() => setActiveStep(0)}
                      >
                        Back
                      </Button>
                      <Button
                        variant="contained"
                        onClick={handleAnalyze}
                        disabled={!caseData.legalIssues.trim() || loading}
                        startIcon={loading ? <CircularProgress size={20} /> : <AssessmentIcon />}
                      >
                        {loading ? 'Analyzing...' : 'Analyze Case'}
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </StepContent>
        </Step>

        {/* Step 3: Analysis Results */}
        <Step>
          <StepLabel>Analysis Results</StepLabel>
          <StepContent>
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {analysis && (
              <Box>
                {/* Case Strength Overview */}
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <StrengthIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Case Strength Assessment
                    </Typography>

                    {analysis.strength_score && (
                      <Box sx={{ mb: 3 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          {getStrengthIcon(analysis.strength_score)}
                          <Typography variant="h4" sx={{ ml: 1, mr: 2 }}>
                            {analysis.strength_score}/10
                          </Typography>
                          <Chip
                            label={
                              analysis.strength_score >= 8 ? 'Strong Case' :
                              analysis.strength_score >= 6 ? 'Moderate Case' : 'Weak Case'
                            }
                            color={getStrengthColor(analysis.strength_score)}
                            variant="outlined"
                          />
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={analysis.strength_score * 10}
                          color={getStrengthColor(analysis.strength_score)}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>
                    )}

                    {analysis.strength_factors && (
                      <Grid container spacing={2}>
                        {Object.entries(analysis.strength_factors).map(([factor, score]) => (
                          <Grid item xs={12} sm={6} md={4} key={factor}>
                            <Paper sx={{ p: 2, textAlign: 'center' }}>
                              <Typography variant="body2" color="text.secondary">
                                {factor.replace('_', ' ').toUpperCase()}
                              </Typography>
                              <Typography variant="h6">
                                {typeof score === 'number' ? `${score}/10` : score}
                              </Typography>
                            </Paper>
                          </Grid>
                        ))}
                      </Grid>
                    )}
                  </CardContent>
                </Card>

                {/* Strategic Recommendations */}
                {analysis.recommendations && (
                  <Card sx={{ mb: 3 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        <StrategyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Strategic Recommendations
                      </Typography>
                      <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
                        <Typography
                          variant="body1"
                          sx={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: 1.6
                          }}
                        >
                          {typeof analysis.recommendations === 'string'
                            ? analysis.recommendations
                            : JSON.stringify(analysis.recommendations, null, 2)
                          }
                        </Typography>
                      </Paper>
                    </CardContent>
                  </Card>
                )}

                {/* Risk Assessment */}
                {analysis.risk_assessment && (
                  <Card sx={{ mb: 3 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        <RiskIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Risk Assessment
                      </Typography>
                      <Paper sx={{ p: 3, bgcolor: 'rgba(255, 193, 7, 0.1)' }}>
                        <Typography
                          variant="body1"
                          sx={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: 1.6
                          }}
                        >
                          {typeof analysis.risk_assessment === 'string'
                            ? analysis.risk_assessment
                            : JSON.stringify(analysis.risk_assessment, null, 2)
                          }
                        </Typography>
                      </Paper>
                    </CardContent>
                  </Card>
                )}

                {/* Full Analysis */}
                {analysis.detailed_analysis && (
                  <Card sx={{ mb: 3 }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        <GavelIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
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
                          {analysis.detailed_analysis}
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
                          <CheckCircleIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Review analysis with client"
                          secondary="Discuss findings and strategic options"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <InfoIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Conduct additional legal research"
                          secondary="Focus on identified weak areas"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon>
                          <StrategyIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Develop litigation strategy"
                          secondary="Based on strength assessment and recommendations"
                        />
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Box>
            )}
          </StepContent>
        </Step>
      </Stepper>

      {/* Privilege Warning Dialog */}
      <Dialog open={privilegeWarning} onClose={() => setPrivilegeWarning(false)}>
        <DialogTitle>
          <PrivilegeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Attorney-Client Privilege Required
        </DialogTitle>
        <DialogContent>
          <Typography>
            A Client ID is required to ensure attorney-client privilege protection.
            All case analysis communications will be encrypted and protected under
            applicable privilege rules.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPrivilegeWarning(false)}>
            Understood
          </Button>
        </DialogActions>
      </Dialog>

      {/* Legal Ethics Disclaimer */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Confidential Attorney Work Product:</strong> This analysis is protected by attorney-client privilege
          and work product doctrine. The AI assessment is for strategic planning only and should be verified through
          independent legal research and professional judgment.
        </Typography>
      </Alert>
    </Box>
  );
}

export default CaseAnalysis;