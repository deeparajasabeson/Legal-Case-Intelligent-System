import React, { useState, useCallback } from 'react';
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
  Chip,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Rating,
  Tooltip,
  ButtonGroup,
  IconButton
} from '@mui/material';
import {
  FindInPage as PrecedentIcon,
  Gavel as GavelIcon,
  TrendingUp as StrengthIcon,
  TrendingDown as WeaknessIcon,
  Balance as BalanceIcon,
  School as AuthorityIcon,
  LocationOn as JurisdictionIcon,
  CalendarToday as DateIcon,
  ExpandMore as ExpandMoreIcon,
  BookmarkBorder as BookmarkIcon,
  Share as ShareIcon,
  FileCopy as CopyIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon
} from '@mui/icons-material';

function PrecedentFinder({ currentUser }) {
  const [searchData, setSearchData] = useState({
    legalIssue: '',
    jurisdiction: 'Federal',
    caseFacts: '',
    clientPosition: ''
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [savedPrecedents, setSavedPrecedents] = useState([]);

  const jurisdictions = [
    'Federal',
    'Supreme Court',
    'Circuit Courts',
    'California',
    'New York',
    'Texas',
    'Florida',
    'Illinois',
    'Pennsylvania',
    'All Jurisdictions'
  ];

  const handleInputChange = (field) => (event) => {
    setSearchData({
      ...searchData,
      [field]: event.target.value
    });
  };

  const handleSearch = useCallback(async () => {
    if (!searchData.legalIssue.trim()) {
      setError('Please provide a legal issue to search');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/precedent-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          legal_issue: searchData.legalIssue,
          jurisdiction: searchData.jurisdiction,
          case_facts: searchData.caseFacts,
          client_position: searchData.clientPosition,
          attorney_id: currentUser.id
        })
      });

      const data = await response.json();

      if (data.success) {
        setResults(data.precedents);
      } else {
        setError(data.error || 'Precedent search failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  }, [searchData, currentUser.id]);

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const savePrecedent = (precedent) => {
    if (!savedPrecedents.find(p => p.precedent_id === precedent.precedent_id)) {
      setSavedPrecedents([...savedPrecedents, { ...precedent, saved_at: new Date().toISOString() }]);
    }
  };

  const getAuthorityColor = (authority) => {
    if (authority?.toLowerCase().includes('supreme court')) return 'error';
    if (authority?.toLowerCase().includes('circuit') || authority?.toLowerCase().includes('federal')) return 'warning';
    if (authority?.toLowerCase().includes('binding')) return 'success';
    return 'default';
  };

  const getAuthorityWeight = (weight) => {
    return Math.min(Math.max(weight || 5, 1), 10);
  };

  const getPrecedentStrength = (precedent) => {
    const weight = getAuthorityWeight(precedent.precedent_weight);
    if (weight >= 8) return { label: 'Strong', color: 'success', icon: <StrengthIcon /> };
    if (weight >= 5) return { label: 'Moderate', color: 'warning', icon: <BalanceIcon /> };
    return { label: 'Weak', color: 'error', icon: <WeaknessIcon /> };
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        <PrecedentIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
        Legal Precedent Finder
      </Typography>

      {/* Search Interface */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Precedent Search Criteria
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Legal Issue"
                placeholder="e.g., breach of contract damages, employment discrimination, constitutional rights..."
                value={searchData.legalIssue}
                onChange={handleInputChange('legalIssue')}
                onKeyPress={handleKeyPress}
                multiline
                rows={2}
                helperText="Describe the specific legal issue or question you need precedents for"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Jurisdiction</InputLabel>
                <Select
                  value={searchData.jurisdiction}
                  label="Jurisdiction"
                  onChange={handleInputChange('jurisdiction')}
                >
                  {jurisdictions.map((j) => (
                    <MenuItem key={j} value={j}>
                      {j}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Client Position"
                placeholder="e.g., plaintiff seeking damages, defendant asserting..."
                value={searchData.clientPosition}
                onChange={handleInputChange('clientPosition')}
                helperText="Your client's position in the matter"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Relevant Case Facts (Optional)"
                placeholder="Key facts that may help find more relevant precedents..."
                value={searchData.caseFacts}
                onChange={handleInputChange('caseFacts')}
                multiline
                rows={2}
                helperText="Provide context to find more analogous cases"
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={handleSearch}
                disabled={loading || !searchData.legalIssue.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <PrecedentIcon />}
                size="large"
              >
                {loading ? 'Searching Precedents...' : 'Find Precedents'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Search Results */}
      {results && (
        <Box>
          {/* Results Summary */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Search Results Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item>
                  <Chip
                    icon={<GavelIcon />}
                    label={`${results.binding_authority?.length || 0} Binding`}
                    color="error"
                    variant="outlined"
                  />
                </Grid>
                <Grid item>
                  <Chip
                    icon={<AuthorityIcon />}
                    label={`${results.persuasive_authority?.length || 0} Persuasive`}
                    color="warning"
                    variant="outlined"
                  />
                </Grid>
                <Grid item>
                  <Chip
                    icon={<BalanceIcon />}
                    label={`${results.analogous_cases?.length || 0} Analogous`}
                    color="info"
                    variant="outlined"
                  />
                </Grid>
                <Grid item>
                  <Chip
                    icon={<WeaknessIcon />}
                    label={`${results.adverse_precedents?.length || 0} Adverse`}
                    color="default"
                    variant="outlined"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Strategic Analysis */}
          {results.strategic_recommendations && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <StrengthIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Strategic Analysis
                </Typography>
                <Paper sx={{ p: 3, bgcolor: 'grey.50' }}>
                  <Typography
                    variant="body1"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      lineHeight: 1.6
                    }}
                  >
                    {typeof results.strategic_recommendations === 'string'
                      ? results.strategic_recommendations
                      : JSON.stringify(results.strategic_recommendations, null, 2)
                    }
                  </Typography>
                </Paper>
              </CardContent>
            </Card>
          )}

          {/* Binding Authority */}
          {results.binding_authority && results.binding_authority.length > 0 && (
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">
                  <GavelIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'error.main' }} />
                  Binding Authority ({results.binding_authority.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {results.binding_authority.map((precedent, index) => (
                  <Card key={index} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'start', mb: 2 }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="h6" gutterBottom>
                            {precedent.case_name || `Case ${index + 1}`}
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                            <Chip
                              icon={<JurisdictionIcon />}
                              label={precedent.jurisdiction || 'Unknown'}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                            <Chip
                              icon={<AuthorityIcon />}
                              label={precedent.binding_authority || 'Binding'}
                              size="small"
                              color="error"
                            />
                            <Chip
                              icon={<StarIcon />}
                              label={`Weight: ${getAuthorityWeight(precedent.precedent_weight)}/10`}
                              size="small"
                              color={getPrecedentStrength(precedent).color}
                            />
                          </Box>
                        </Box>
                        <ButtonGroup variant="outlined" size="small">
                          <Tooltip title="Save precedent">
                            <IconButton onClick={() => savePrecedent(precedent)}>
                              <BookmarkIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Copy citation">
                            <IconButton>
                              <CopyIcon />
                            </IconButton>
                          </Tooltip>
                        </ButtonGroup>
                      </Box>

                      <Typography variant="body1" paragraph>
                        <strong>Legal Principle:</strong> {precedent.legal_principle}
                      </Typography>

                      {precedent.citation && (
                        <Typography variant="body2" color="text.secondary" paragraph>
                          <strong>Citation:</strong> {precedent.citation}
                        </Typography>
                      )}

                      {precedent.related_statutes && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Related Statutes:</strong> {precedent.related_statutes}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </AccordionDetails>
            </Accordion>
          )}

          {/* Persuasive Authority */}
          {results.persuasive_authority && results.persuasive_authority.length > 0 && (
            <Accordion sx={{ mt: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">
                  <AuthorityIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'warning.main' }} />
                  Persuasive Authority ({results.persuasive_authority.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {results.persuasive_authority.map((precedent, index) => (
                  <Card key={index} sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'start', mb: 2 }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="h6" gutterBottom>
                            {precedent.case_name || `Case ${index + 1}`}
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                            <Chip
                              icon={<JurisdictionIcon />}
                              label={precedent.jurisdiction || 'Unknown'}
                              size="small"
                              color="secondary"
                              variant="outlined"
                            />
                            <Chip
                              icon={<AuthorityIcon />}
                              label="Persuasive"
                              size="small"
                              color="warning"
                            />
                            <Chip
                              icon={<StarIcon />}
                              label={`Weight: ${getAuthorityWeight(precedent.precedent_weight)}/10`}
                              size="small"
                              color={getPrecedentStrength(precedent).color}
                            />
                          </Box>
                        </Box>
                        <ButtonGroup variant="outlined" size="small">
                          <IconButton onClick={() => savePrecedent(precedent)}>
                            <BookmarkIcon />
                          </IconButton>
                          <IconButton>
                            <CopyIcon />
                          </IconButton>
                        </ButtonGroup>
                      </Box>

                      <Typography variant="body1" paragraph>
                        <strong>Legal Principle:</strong> {precedent.legal_principle}
                      </Typography>

                      {precedent.citation && (
                        <Typography variant="body2" color="text.secondary">
                          <strong>Citation:</strong> {precedent.citation}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </AccordionDetails>
            </Accordion>
          )}

          {/* Adverse Precedents */}
          {results.adverse_precedents && results.adverse_precedents.length > 0 && (
            <Accordion sx={{ mt: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">
                  <WeaknessIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'error.main' }} />
                  Adverse Precedents ({results.adverse_precedents.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Alert severity="warning" sx={{ mb: 2 }}>
                  These precedents may be unfavorable to your client's position. Consider distinguishing factors.
                </Alert>
                {results.adverse_precedents.map((precedent, index) => (
                  <Card key={index} sx={{ mb: 2, border: '1px solid', borderColor: 'warning.light' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {precedent.case_name || `Adverse Case ${index + 1}`}
                      </Typography>
                      <Typography variant="body1" paragraph>
                        <strong>Legal Principle:</strong> {precedent.legal_principle}
                      </Typography>
                      {precedent.distinguishing_factors && (
                        <Typography variant="body2" color="primary">
                          <strong>Distinguishing Factors:</strong> {precedent.distinguishing_factors}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </AccordionDetails>
            </Accordion>
          )}

          {/* Legal Analysis */}
          {results.legal_analysis && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Comprehensive Precedent Analysis
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
                    {typeof results.legal_analysis === 'string'
                      ? results.legal_analysis
                      : JSON.stringify(results.legal_analysis, null, 2)
                    }
                  </Typography>
                </Paper>
              </CardContent>
            </Card>
          )}
        </Box>
      )}

      {/* Saved Precedents */}
      {savedPrecedents.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <BookmarkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Saved Precedents ({savedPrecedents.length})
            </Typography>
            <List>
              {savedPrecedents.map((precedent, index) => (
                <ListItem key={index} divider>
                  <ListItemIcon>
                    <StarIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={precedent.case_name}
                    secondary={precedent.legal_principle}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Legal Disclaimer */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Precedent Research Disclaimer:</strong> AI-identified precedents should be independently verified
          and analyzed. Citation accuracy and current validity must be confirmed through official legal databases.
          This research is protected by attorney-client privilege.
        </Typography>
      </Alert>
    </Box>
  );
}

export default PrecedentFinder;