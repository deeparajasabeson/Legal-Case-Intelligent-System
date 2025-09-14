import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Badge,
  Alert
} from '@mui/material';
import {
  Menu as MenuIcon,
  Gavel as GavelIcon,
  Search as SearchIcon,
  Assessment as AssessmentIcon,
  Description as DocumentIcon,
  FindInPage as PrecedentIcon,
  Security as PrivilegeIcon,
  Notifications as NotificationsIcon
} from '@mui/icons-material';

import LegalResearch from './components/LegalResearch';
import CaseAnalysis from './components/CaseAnalysis';
import DocumentReview from './components/DocumentReview';
import PrecedentFinder from './components/PrecedentFinder';
import PrivilegeMonitor from './components/PrivilegeMonitor';
import EthicsCompliance from './components/EthicsCompliance';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      dark: '#115293',
      light: '#4791db'
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff'
    }
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    }
  },
});

const drawerWidth = 280;

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [currentUser] = useState({
    id: 'att_001',
    name: 'Attorney Smith',
    role: 'attorney',
    barNumber: 'CA12345'
  });
  const [ethicsAlerts, setEthicsAlerts] = useState([]);

  const menuItems = [
    { text: 'Legal Research', icon: <SearchIcon />, path: '/research' },
    { text: 'Case Analysis', icon: <AssessmentIcon />, path: '/case-analysis' },
    { text: 'Document Review', icon: <DocumentIcon />, path: '/document-review' },
    { text: 'Precedent Finder', icon: <PrecedentIcon />, path: '/precedent-finder' },
    { text: 'Privilege Monitor', icon: <PrivilegeIcon />, path: '/privilege-monitor' },
    { text: 'Ethics Compliance', icon: <GavelIcon />, path: '/ethics' },
  ];

  useEffect(() => {
    // Load ethics alerts on startup
    fetchEthicsAlerts();
  }, []);

  const fetchEthicsAlerts = async () => {
    try {
      const response = await fetch('/api/ethics-compliance?attorney_id=' + currentUser.id);
      const data = await response.json();
      if (data.success) {
        setEthicsAlerts(data.ethics_alerts || []);
      }
    } catch (error) {
      console.error('Failed to fetch ethics alerts:', error);
    }
  };

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const drawer = (
    <div>
      <Toolbar>
        <GavelIcon sx={{ mr: 2 }} />
        <Typography variant="h6" noWrap component="div">
          Legal AI Platform
        </Typography>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem button key={item.text} component="a" href={item.path}>
            <ListItemIcon>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          <AppBar
            position="fixed"
            sx={{
              width: { sm: `calc(100% - ${drawerWidth}px)` },
              ml: { sm: `${drawerWidth}px` },
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 2, display: { sm: 'none' } }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                Legal AI Research Platform
              </Typography>
              <Typography variant="body2" sx={{ mr: 2 }}>
                {currentUser.name} - {currentUser.barNumber}
              </Typography>
              <IconButton color="inherit">
                <Badge badgeContent={ethicsAlerts.length} color="secondary">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Toolbar>
          </AppBar>

          <Box
            component="nav"
            sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
          >
            <Drawer
              variant="temporary"
              open={drawerOpen}
              onClose={handleDrawerToggle}
              ModalProps={{
                keepMounted: true, // Better open performance on mobile.
              }}
              sx={{
                display: { xs: 'block', sm: 'none' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
            >
              {drawer}
            </Drawer>
            <Drawer
              variant="permanent"
              sx={{
                display: { xs: 'none', sm: 'block' },
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
              open
            >
              {drawer}
            </Drawer>
          </Box>

          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: { sm: `calc(100% - ${drawerWidth}px)` },
            }}
          >
            <Toolbar />

            {/* Ethics Alerts */}
            {ethicsAlerts.length > 0 && (
              <Box sx={{ mb: 2 }}>
                {ethicsAlerts.slice(0, 3).map((alert, index) => (
                  <Alert
                    key={index}
                    severity={alert.includes('CRITICAL') ? 'error' : alert.includes('WARNING') ? 'warning' : 'info'}
                    sx={{ mb: 1 }}
                  >
                    {alert}
                  </Alert>
                ))}
              </Box>
            )}

            <Container maxWidth="xl">
              <Routes>
                <Route path="/" element={<Navigate to="/research" replace />} />
                <Route path="/research" element={<LegalResearch currentUser={currentUser} />} />
                <Route path="/case-analysis" element={<CaseAnalysis currentUser={currentUser} />} />
                <Route path="/document-review" element={<DocumentReview currentUser={currentUser} />} />
                <Route path="/precedent-finder" element={<PrecedentFinder currentUser={currentUser} />} />
                <Route path="/privilege-monitor" element={<PrivilegeMonitor currentUser={currentUser} />} />
                <Route path="/ethics" element={<EthicsCompliance currentUser={currentUser} onAlertsUpdate={setEthicsAlerts} />} />
              </Routes>
            </Container>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;