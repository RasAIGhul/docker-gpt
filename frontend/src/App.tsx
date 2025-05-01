import React, { useState, createContext } from 'react';
import { 
  Container, 
  CssBaseline, 
  AppBar, 
  Toolbar, 
  Typography, 
  Box, 
  ThemeProvider, 
  createTheme, 
  Divider,
  useMediaQuery,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  FormControlLabel,
  Switch
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DeploymentForm from './components/DeploymentForm';
import DeploymentResult from './components/DeploymentResult';
import ContainerList from './components/ContainerList';
import SystemManagement from './components/SystemManagement';
import { DeploymentResponse } from './types/api';

// Create debug context
export const DebugContext = createContext({ debugMode: false, setDebugMode: (mode: boolean) => {} });

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [deploymentResult, setDeploymentResult] = useState<DeploymentResponse | null>(null);
  const [showManagement, setShowManagement] = useState(false);
  const [debugMode, setDebugMode] = useState(false);
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  
  // Theme with system preference detection
  const appTheme = React.useMemo(
    () =>
      createTheme({
        palette: {
          mode: prefersDarkMode ? 'dark' : 'light',
          primary: {
            main: '#2196f3',
          },
          secondary: {
            main: '#f50057',
          },
        },
      }),
    [prefersDarkMode],
  );

  const handleOpenManagement = () => {
    setShowManagement(true);
  };

  const handleCloseManagement = () => {
    setShowManagement(false);
  };

  // Debug context value
  const debugContextValue = { debugMode, setDebugMode };

  return (
    <DebugContext.Provider value={debugContextValue}>
      <ThemeProvider theme={appTheme}>
        <CssBaseline />
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              DockerGPT
            </Typography>
            <FormControlLabel
              control={<Switch 
                color="secondary" 
                checked={debugMode} 
                onChange={(e) => setDebugMode(e.target.checked)} 
              />}
              label="Debug Mode"
              sx={{ mr: 2, color: 'white' }}
            />
            <Button color="inherit" onClick={handleOpenManagement}>
              System Management
            </Button>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Box sx={{ my: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom align="center">
              Deploy Docker Containers with Natural Language
            </Typography>
            <Typography variant="subtitle1" align="center" color="text.secondary" sx={{ mb: 4 }}>
              Just describe the environment you need, and we'll find and deploy the right container
            </Typography>
            
            <DeploymentForm />
            
            <Divider sx={{ my: 4 }} />
            
            <ContainerList />
          </Box>
        </Container>

        {/* Management Dialog */}
        <Dialog 
          open={showManagement} 
          onClose={handleCloseManagement}
          fullWidth
          maxWidth="md"
        >
          <DialogTitle>
            System Management
            <IconButton
              aria-label="close"
              onClick={handleCloseManagement}
              sx={{
                position: 'absolute',
                right: 8,
                top: 8,
              }}
            >
              <CloseIcon />
            </IconButton>
          </DialogTitle>
          <DialogContent>
            <SystemManagement />
          </DialogContent>
        </Dialog>
      </ThemeProvider>
    </DebugContext.Provider>
  );
}

export default App; 