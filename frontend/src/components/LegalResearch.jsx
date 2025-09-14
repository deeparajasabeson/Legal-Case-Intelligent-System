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
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Paper
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  Gavel as GavelIcon,
  Description as DescriptionIcon,
  FindInPage as FindInPageIcon
} from '@mui/icons-material';

function LegalResearch({ currentUser }) {
  const [query, setQuery] = useState('');
  const [jurisdiction, setJurisdiction] = useState('Federal');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const jurisdictions = [
    'Federal',
    'California',
    'New York',
    'Texas',
    'Florida',
    'Illinois',
    'Pennsylvania',
    'Ohio',
    'Georgia',
    'North Carolina'
  ];

  const handleSearch = useCallback(async () => {
    if (!query.trim()) {
      setError('Please enter a legal research query');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/legal-research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          jurisdiction: jurisdiction,
          attorney_id: currentUser.id
        })
      });

      const data = await response.json();

      if (data.success) {
        setResults(data.results);
      } else {
        setError(data.error || 'Research failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
      console.error('Research error:', err);
    } finally {
      setLoading(false);
    }
  }, [query, jurisdiction, currentUser.id]);

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        <SearchIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
        Legal Research
      </Typography>

      {/* Search Interface */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Legal Research Query"
                placeholder="e.g., breach of contract remedies, employment discrimination, patent infringement..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                multiline
                rows={2}
                helperText="Enter your legal question in natural language"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Jurisdiction</InputLabel>
                <Select
                  value={jurisdiction}
                  label="Jurisdiction"
                  onChange={(e) => setJurisdiction(e.target.value)}
                >
                  {jurisdictions.map((j) => (
                    <MenuItem key={j} value={j}>
                      {j}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button
                fullWidth
                variant="contained"
                onClick={handleSearch}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                sx={{ height: '56px' }}
              >
                {loading ? 'Researching...' : 'Research'}
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

      {/* Research Results */}
      {results && (
        <Box>
          {/* Summary Statistics */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Research Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item>
                  <Chip
                    icon={<GavelIcon />}
                    label={`${results.case_count} Cases`}
                    color="primary"
                    variant="outlined"
                  />
                </Grid>
                <Grid item>
                  <Chip
                    icon={<DescriptionIcon />}
                    label={`${results.statute_count} Statutes`}
                    color="secondary"
                    variant="outlined"
                  />
                </Grid>
                <Grid item>
                  <Chip
                    icon={<FindInPageIcon />}
                    label={`${results.precedent_count} Precedents`}
                    color="success"
                    variant="outlined"
                  />
                </Grid>
              </Grid>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Query: "{results.query}" | Jurisdiction: {results.jurisdiction}
              </Typography>
            </CardContent>
          </Card>

          {/* AI Analysis */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Legal Analysis
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
                  {results.ai_analysis}
                </Typography>
              </Paper>
            </CardContent>
          </Card>

          {/* Case Law Results */}
          {results.raw_data.case_law && results.raw_data.case_law.length > 0 && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">
                  <GavelIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Case Law ({results.raw_data.case_law.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {results.raw_data.case_law.map((case_item, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={
                          <Box>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {case_item.case_name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {case_item.citation} | {case_item.court} | {case_item.decision_date}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              <strong>Legal Issues:</strong> {case_item.legal_issues}
                            </Typography>
                            <Typography variant="body2">
                              <strong>Holding:</strong> {case_item.holding}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Statutes Results */}
          {results.raw_data.statutes && results.raw_data.statutes.length > 0 && (
            <Accordion sx={{ mt: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">
                  <DescriptionIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Statutes ({results.raw_data.statutes.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {results.raw_data.statutes.map((statute, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={
                          <Box>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {statute.statute_title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {statute.code_section} | {statute.jurisdiction}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="body2">
                              {statute.statute_text?.substring(0, 300)}...
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Precedents Results */}
          {results.raw_data.precedents && results.raw_data.precedents.length > 0 && (
            <Accordion sx={{ mt: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">
                  <FindInPageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Legal Precedents ({results.raw_data.precedents.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {results.raw_data.precedents.map((precedent, index) => (
                    <ListItem key={index} divider>
                      <ListItemText
                        primary={
                          <Box>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {precedent.case_name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {precedent.citation} | Weight: {precedent.precedent_weight}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              <strong>Legal Principle:</strong> {precedent.legal_principle}
                            </Typography>
                            <Typography variant="body2">
                              <strong>Binding Authority:</strong> {precedent.binding_authority}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          )}
        </Box>
      )}

      {/* Legal Disclaimer */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Legal Disclaimer:</strong> This AI-powered research is for informational purposes only and does not constitute legal advice.
          Always consult with a qualified attorney for specific legal matters. Attorney-client privilege applies to communications
          within this platform.
        </Typography>
      </Alert>
    </Box>
  );
}

export default LegalResearch;