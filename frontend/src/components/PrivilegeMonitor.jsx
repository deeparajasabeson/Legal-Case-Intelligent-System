import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Paper,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField
} from '@mui/material';
import {
  Security as PrivilegeIcon,
  Visibility as ViewIcon,
  VisibilityOff as HideIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Shield as ShieldIcon,
  Lock as LockIcon,
  History as HistoryIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  Gavel as GavelIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

function PrivilegeMonitor({ currentUser }) {
  const [loading, setLoading] = useState(false);
  const [privilegeData, setPrivilegeData] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [selectedCommunication, setSelectedCommunication] = useState(null);
  const [auditFilter, setAuditFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data for demonstration
  const mockPrivilegeData = {
    active_relationships: [
      {
        client_id: 'CLIENT_001',
        client_name: 'Smith Corporation',
        relationship_start: '2024-01-15',
        last_activity: '2024-09-14',
        communication_count: 23,
        privilege_status: 'active',
        confidentiality_level: 'high'
      },
      {
        client_id: 'CLIENT_002',
        client_name: 'Johnson LLC',
        relationship_start: '2024-03-10',
        last_activity: '2024-09-12',
        communication_count: 15,
        privilege_status: 'active',
        confidentiality_level: 'medium'
      }
    ],
    recent_communications: [
      {
        communication_id: 'COMM_001',
        client_id: 'CLIENT_001',
        client_name: 'Smith Corporation',
        type: 'case_analysis',
        timestamp: '2024-09-14T10:30:00Z',
        privilege_applied: true,
        access_level: 'attorney_only',
        encryption_status: 'encrypted'
      },
      {
        communication_id: 'COMM_002',
        client_id: 'CLIENT_002',
        client_name: 'Johnson LLC',
        type: 'legal_research',
        timestamp: '2024-09-14T09:15:00Z',
        privilege_applied: true,
        access_level: 'attorney_client',
        encryption_status: 'encrypted'
      }
    ],
    audit_logs: [
      {
        log_id: 'AUDIT_001',
        timestamp: '2024-09-14T10:30:00Z',
        attorney_id: 'att_001',
        action: 'communication_access',
        client_id: 'CLIENT_001',
        status: 'approved',
        details: 'Accessed case analysis for Smith Corporation'
      },
      {
        log_id: 'AUDIT_002',
        timestamp: '2024-09-14T09:15:00Z',
        attorney_id: 'att_001',
        action: 'privilege_verification',
        client_id: 'CLIENT_002',
        status: 'approved',
        details: 'Verified privilege relationship with Johnson LLC'
      }
    ],
    compliance_status: {
      overall_score: 95,
      privilege_protection: 98,
      encryption_compliance: 100,
      access_control: 92,
      audit_completeness: 90
    }
  };

  useEffect(() => {
    loadPrivilegeData();
  }, []);

  const loadPrivilegeData = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      // In a real implementation, this would fetch from the API
      // For now, using mock data
      setTimeout(() => {
        setPrivilegeData(mockPrivilegeData);
        setLoading(false);
      }, 1000);

    } catch (err) {
      setError('Failed to load privilege data');
      setLoading(false);
    }
  }, []);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getPrivilegeStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'suspended': return 'warning';
      case 'terminated': return 'error';
      default: return 'default';
    }
  };

  const getConfidentialityColor = (level) => {
    switch (level) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getComplianceColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const filteredAuditLogs = privilegeData?.audit_logs?.filter(log => {
    const matchesFilter = auditFilter === 'all' || log.action === auditFilter;
    const matchesSearch = searchTerm === '' ||
      log.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.client_id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  }) || [];

  if (loading && !privilegeData) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        <PrivilegeIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
        Attorney-Client Privilege Monitor
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {privilegeData && (
        <Box>
          {/* Compliance Dashboard */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  <ShieldIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Privilege Compliance Dashboard
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={loadPrivilegeData}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Box>

              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h3" color={getComplianceColor(privilegeData.compliance_status.overall_score)}>
                      {privilegeData.compliance_status.overall_score}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Overall Compliance
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={privilegeData.compliance_status.overall_score}
                      color={getComplianceColor(privilegeData.compliance_status.overall_score)}
                      sx={{ mt: 1 }}
                    />
                  </Paper>
                </Grid>

                <Grid item xs={12} md={9}>
                  <Grid container spacing={2}>
                    {Object.entries(privilegeData.compliance_status)
                      .filter(([key]) => key !== 'overall_score')
                      .map(([key, value]) => (
                        <Grid item xs={12} sm={6} md={3} key={key}>
                          <Paper sx={{ p: 2, textAlign: 'center' }}>
                            <Typography variant="h5" color={getComplianceColor(value)}>
                              {value}%
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {key.replace('_', ' ').toUpperCase()}
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={value}
                              color={getComplianceColor(value)}
                              sx={{ mt: 1 }}
                              size="small"
                            />
                          </Paper>
                        </Grid>
                      ))}
                  </Grid>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Tabs for Different Views */}
          <Card>
            <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tab label="Active Relationships" />
              <Tab label="Recent Communications" />
              <Tab label="Audit Logs" />
            </Tabs>

            {/* Active Relationships Tab */}
            {activeTab === 0 && (
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <PersonIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Active Attorney-Client Relationships
                </Typography>

                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Client</TableCell>
                        <TableCell>Relationship Start</TableCell>
                        <TableCell>Last Activity</TableCell>
                        <TableCell>Communications</TableCell>
                        <TableCell>Privilege Status</TableCell>
                        <TableCell>Confidentiality</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {privilegeData.active_relationships.map((relationship) => (
                        <TableRow key={relationship.client_id}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <BusinessIcon sx={{ mr: 1 }} />
                              <Box>
                                <Typography variant="body2" fontWeight="bold">
                                  {relationship.client_name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {relationship.client_id}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>{formatDate(relationship.relationship_start)}</TableCell>
                          <TableCell>{formatDate(relationship.last_activity)}</TableCell>
                          <TableCell>
                            <Chip
                              label={relationship.communication_count}
                              color="primary"
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={relationship.privilege_status.toUpperCase()}
                              color={getPrivilegeStatusColor(relationship.privilege_status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={relationship.confidentiality_level.toUpperCase()}
                              color={getConfidentialityColor(relationship.confidentiality_level)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <IconButton size="small" color="primary">
                              <ViewIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            )}

            {/* Recent Communications Tab */}
            {activeTab === 1 && (
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <LockIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Recent Privileged Communications
                </Typography>

                <List>
                  {privilegeData.recent_communications.map((comm) => (
                    <ListItem
                      key={comm.communication_id}
                      divider
                      secondaryAction={
                        <Box>
                          <Chip
                            icon={comm.privilege_applied ? <CheckIcon /> : <ErrorIcon />}
                            label={comm.privilege_applied ? 'Privileged' : 'Not Privileged'}
                            color={comm.privilege_applied ? 'success' : 'error'}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                          <Chip
                            icon={<LockIcon />}
                            label={comm.encryption_status.toUpperCase()}
                            color={comm.encryption_status === 'encrypted' ? 'success' : 'error'}
                            size="small"
                          />
                        </Box>
                      }
                    >
                      <ListItemIcon>
                        <GavelIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box>
                            <Typography variant="body1" fontWeight="bold">
                              {comm.client_name} - {comm.type.replace('_', ' ').toUpperCase()}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {formatDate(comm.timestamp)} | Access Level: {comm.access_level.replace('_', ' ')}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Typography variant="caption" color="primary">
                            Communication ID: {comm.communication_id}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            )}

            {/* Audit Logs Tab */}
            {activeTab === 2 && (
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Privilege Access Audit Trail
                </Typography>

                {/* Filters */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Filter by Action</InputLabel>
                      <Select
                        value={auditFilter}
                        label="Filter by Action"
                        onChange={(e) => setAuditFilter(e.target.value)}
                      >
                        <MenuItem value="all">All Actions</MenuItem>
                        <MenuItem value="communication_access">Communication Access</MenuItem>
                        <MenuItem value="privilege_verification">Privilege Verification</MenuItem>
                        <MenuItem value="data_access">Data Access</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Search"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Search audit logs..."
                    />
                  </Grid>
                </Grid>

                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Attorney</TableCell>
                        <TableCell>Action</TableCell>
                        <TableCell>Client</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Details</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {filteredAuditLogs.map((log) => (
                        <TableRow key={log.log_id}>
                          <TableCell>
                            <Typography variant="body2">
                              {formatDate(log.timestamp)}
                            </Typography>
                          </TableCell>
                          <TableCell>{log.attorney_id}</TableCell>
                          <TableCell>
                            <Chip
                              label={log.action.replace('_', ' ').toUpperCase()}
                              color="primary"
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>{log.client_id}</TableCell>
                          <TableCell>
                            <Chip
                              icon={log.status === 'approved' ? <CheckIcon /> : <ErrorIcon />}
                              label={log.status.toUpperCase()}
                              color={log.status === 'approved' ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {log.details}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            )}
          </Card>
        </Box>
      )}

      {/* Privilege Alerts */}
      <Alert severity="warning" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Privilege Protection Notice:</strong> All communications and data access are continuously monitored
          for attorney-client privilege compliance. Any privilege violations will be immediately flagged and reported
          to the Bar Association as required by professional responsibility rules.
        </Typography>
      </Alert>

      {/* Legal Ethics Compliance */}
      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          <strong>Ethics Compliance:</strong> This system maintains comprehensive audit trails in accordance with
          ABA Model Rules of Professional Conduct, particularly Rules 1.6 (Confidentiality) and 5.5 (Technology Competence).
          All data is encrypted and access-controlled per legal industry standards.
        </Typography>
      </Alert>
    </Box>
  );
}

export default PrivilegeMonitor;