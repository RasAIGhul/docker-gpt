import React, { useContext, useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Chip, 
  Card, 
  CardContent, 
  Alert, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails,
  Divider,
  Button,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import InfoIcon from '@mui/icons-material/Info';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import LanguageIcon from '@mui/icons-material/Language';
import StorageIcon from '@mui/icons-material/Storage';
import SettingsIcon from '@mui/icons-material/Settings';
import DashboardIcon from '@mui/icons-material/Dashboard';
import CodeIcon from '@mui/icons-material/Code';
import LinkIcon from '@mui/icons-material/Link';
import { Link } from '@mui/material';
import { DeploymentResponse } from '../types/api';
import { DebugContext } from '../App';

interface DeploymentResultProps {
  result: DeploymentResponse;
}

// Helper to format keys in a more readable way
const formatKey = (key: string): string => {
  return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
};

const DeploymentResult: React.FC<DeploymentResultProps> = ({ result }) => {
  const { debugMode } = useContext(DebugContext);
  const [showCommands, setShowCommands] = useState(false);
  const [showProcessLogs, setShowProcessLogs] = useState(false);

  if (!result) {
    return null;
  }

  const { 
    status, 
    message, 
    selected_image, 
    container_id, 
    config, 
    reasoning, 
    error, 
    docker_command,
    process_logs,
    docker_logs,
    access_links,
    has_web_frontend,
    web_url
  } = result;

  // Format ports for display
  const formatPorts = (ports: Record<string, number> = {}) => {
    return Object.entries(ports).map(([container, host]) => 
      <Chip 
        key={container} 
        label={`${host}:${container}`} 
        variant="outlined" 
        size="small" 
        sx={{ mr: 1, mb: 1 }} 
      />
    );
  };

  // Format environment variables for display
  const formatEnv = (env: Record<string, string> = {}) => {
    return Object.entries(env).map(([key, value]) => 
      <Box key={key} sx={{ mb: 1 }}>
        <Typography variant="body2" component="span" sx={{ fontWeight: 'bold' }}>
          {key}:
        </Typography>{' '}
        <Typography variant="body2" component="span" sx={{ wordBreak: 'break-all' }}>
          {value}
        </Typography>
      </Box>
    );
  };

  // Determine if this was a fallback deployment
  const isFallback = message?.toLowerCase().includes('fallback') || 
                    selected_image?.description?.toLowerCase().includes('fallback');

  // Generate docker command that would have been executed
  const generateDockerCommand = () => {
    if (docker_command) {
      return docker_command;
    }
    
    if (!selected_image?.name) return '';

    let command = `docker run -d`;
    
    // Add any port mappings
    if (config?.ports && Object.keys(config.ports).length > 0) {
      Object.entries(config.ports).forEach(([containerPort, hostPort]) => {
        command += ` -p ${hostPort}:${containerPort.replace('/tcp', '')}`;
      });
    }
    
    // Add any environment variables
    if (config?.environment && Object.keys(config.environment).length > 0) {
      Object.entries(config.environment).forEach(([key, value]) => {
        command += ` -e ${key}="${value}"`;
      });
    }
    
    // Add the image name
    command += ` ${selected_image.name}`;
    
    return command;
  };

  // Determine icon for log item based on content
  const getLogItemIcon = (logItem: string) => {
    if (logItem.includes("ERROR") || logItem.includes("Error") || logItem.includes("failed")) {
      return <ErrorIcon color="error" />;
    } else if (logItem.includes("WARNING") || logItem.includes("fallback")) {
      return <WarningIcon color="warning" />;
    } else {
      return <InfoIcon color="info" />;
    }
  };
  
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Deployment Result
      </Typography>

      {/* Status Message */}
      <Alert 
        severity={status ? (isFallback ? "warning" : "success") : "error"} 
        sx={{ mb: 3 }}
      >
        {message || (status ? 'Deployment completed successfully' : 'Deployment failed')}
        
        {isFallback && (
          <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
            A fallback image was used because the original request could not be processed.
          </Typography>
        )}
        
        {/* Web Access Button */}
        {has_web_frontend && web_url && (
          <Box sx={{ mt: 2 }}>
            <Button 
              variant="contained"
              color="primary"
              href={web_url}
              target="_blank"
              startIcon={<OpenInNewIcon />}
              sx={{ mr: 1 }}
            >
              Open Web Interface
            </Button>
            <Typography variant="caption" sx={{ display: 'block', mt: 0.5, color: 'text.secondary' }}>
              {web_url}
            </Typography>
          </Box>
        )}
      </Alert>

      {/* Debug Information */}
      {debugMode && error && (
        <Card variant="outlined" sx={{ mb: 3, bgcolor: '#333333', border: '2px solid #d32f2f', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>
          <CardContent>
            <Typography variant="h6" sx={{ color: '#ff5252', fontWeight: 'bold' }}>
              Debug Information
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Typography variant="subtitle2" sx={{ color: '#ffffff', fontWeight: 'bold' }}>Error Type:</Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 1, color: '#ffffff' }}>
                {error.type}
              </Typography>
              
              <Typography variant="subtitle2" sx={{ color: '#ffffff', fontWeight: 'bold' }}>Error Details:</Typography>
              <Typography variant="body2" sx={{ 
                fontFamily: 'monospace', 
                mb: 1, 
                whiteSpace: 'pre-wrap', 
                color: '#ffffff',
                backgroundColor: '#444444',
                padding: '8px',
                border: '1px solid #666666',
                borderRadius: '4px'
              }}>
                {JSON.stringify(error.details, null, 2)}
              </Typography>

              {error.stack && (
                <>
                  <Typography variant="subtitle2" sx={{ color: '#ffffff', fontWeight: 'bold' }}>Stack Trace:</Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontFamily: 'monospace', 
                      whiteSpace: 'pre-wrap',
                      fontSize: '0.75rem',
                      overflowX: 'auto',
                      color: '#ffffff',
                      backgroundColor: '#444444',
                      padding: '8px',
                      border: '1px solid #666666',
                      borderRadius: '4px'
                    }}
                  >
                    {error.stack}
                  </Typography>
                </>
              )}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Show deployment commands button */}
      <Box sx={{ mb: 3 }}>
        <Button 
          variant="outlined" 
          size="small"
          onClick={() => setShowCommands(!showCommands)}
          startIcon={<ExpandMoreIcon style={{ transform: showCommands ? 'rotate(180deg)' : 'rotate(0deg)' }}/>}
          sx={{ mr: 1 }}
        >
          {showCommands ? 'Hide Docker Commands' : 'Show Docker Commands'}
        </Button>

        <Button 
          variant="outlined" 
          size="small"
          color="info"
          onClick={() => setShowProcessLogs(!showProcessLogs)}
          startIcon={<ExpandMoreIcon style={{ transform: showProcessLogs ? 'rotate(180deg)' : 'rotate(0deg)' }}/>}
        >
          {showProcessLogs ? 'Hide Deployment Logs' : 'Show Deployment Logs'}
        </Button>
        
        <Collapse in={showCommands} timeout="auto" unmountOnExit>
          <Paper variant="outlined" sx={{ p: 2, mt: 1, bgcolor: '#222222', border: '1px solid #444', color: '#ffffff' }}>
            <Typography variant="subtitle2" gutterBottom sx={{ color: '#ffffff', fontWeight: 'bold' }}>
              Equivalent Docker Command:
            </Typography>
            <Typography 
              variant="body2" 
              component="pre"
              sx={{ 
                fontFamily: 'monospace', 
                overflowX: 'auto',
                p: 2,
                backgroundColor: '#1e1e1e',
                color: '#ffffff',
                borderRadius: 1,
                whiteSpace: 'pre-wrap',
                border: '1px solid #555',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
              }}
            >
              {generateDockerCommand() || 'Command information not available'}
            </Typography>
          </Paper>
        </Collapse>

        {/* Detailed Process Logs */}
        <Collapse in={showProcessLogs} timeout="auto" unmountOnExit>
          <Paper variant="outlined" sx={{ 
            p: 2, 
            mt: 1, 
            bgcolor: '#222222', 
            maxHeight: '400px', 
            overflow: 'auto', 
            border: '2px solid #444',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            color: '#ffffff'
          }}>
            <Typography variant="subtitle2" gutterBottom fontWeight="bold" sx={{ color: '#ffffff' }}>
              Deployment Process Logs:
            </Typography>
            
            {process_logs?.steps && Array.isArray(process_logs.steps) && process_logs.steps.length > 0 ? (
              <List dense sx={{ bgcolor: '#333333', border: '1px solid #555', borderRadius: '4px' }}>
                {process_logs.steps.map((log, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      {getLogItemIcon(log)}
                    </ListItemIcon>
                    <ListItemText 
                      primary={log}
                      sx={{ 
                        '& .MuiTypography-root': { 
                          color: log.includes("ERROR") || log.includes("Error") || log.includes("failed") 
                            ? '#ff6b6b' 
                            : log.includes("WARNING") || log.includes("fallback")
                              ? '#ffc107'
                              : '#8bc8ff',
                          fontWeight: 500
                        }
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            ) : process_logs && Array.isArray(process_logs) && process_logs.length > 0 ? (
              <List dense sx={{ bgcolor: '#333333', border: '1px solid #555', borderRadius: '4px' }}>
                {process_logs.map((log, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      {getLogItemIcon(log)}
                    </ListItemIcon>
                    <ListItemText 
                      primary={log}
                      sx={{ 
                        '& .MuiTypography-root': { 
                          color: log.includes("ERROR") || log.includes("Error") || log.includes("failed") 
                            ? '#ff6b6b' 
                            : log.includes("WARNING") || log.includes("fallback")
                              ? '#ffc107'
                              : '#8bc8ff',
                          fontWeight: 500
                        }
                      }}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Alert severity="info" sx={{ mt: 1, color: '#ffffff', bgcolor: 'rgba(32, 44, 55, 0.9)', border: '1px solid #444' }}>
                No deployment logs available.
              </Alert>
            )}

            {/* Display any error messages */}
            {process_logs?.error && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" color="error" gutterBottom fontWeight="bold" sx={{ color: '#ff6b6b' }}>
                  Error Details:
                </Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    bgcolor: 'rgba(53, 37, 37, 0.9)', 
                    borderColor: '#ff6b6b',
                    color: '#ff9595',
                    borderWidth: 2,
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                  }}
                >
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap', fontWeight: 500 }}>
                    {process_logs.error}
                  </Typography>
                </Paper>
              </Box>
            )}

            {/* Display docker logs if available */}
            {docker_logs && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom sx={{ color: '#ffffff' }}>
                  Docker Execution Details:
                </Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    bgcolor: '#1e1e1e',
                    borderColor: '#555',
                    color: '#f8f8f2'
                  }}
                >
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(docker_logs, null, 2)}
                  </Typography>
                </Paper>
              </Box>
            )}
          </Paper>
        </Collapse>
      </Box>

      {/* Container Details */}
      {container_id && (
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Container Details
          </Typography>
          <Paper variant="outlined" sx={{ p: 2, mb: 3, backgroundColor: '#f5f5f5' }}>
            <Box>
              <Typography variant="subtitle2">Container ID</Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', overflowWrap: 'break-word' }}>
                {container_id}
              </Typography>
            </Box>
          </Paper>
        </Box>
      )}

      {/* Selected Docker Image Information */}
      {selected_image && (
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Selected Docker Image
            {isFallback && (
              <Chip 
                label="Fallback Image" 
                color="warning" 
                size="small" 
                sx={{ ml: 1 }} 
              />
            )}
          </Typography>
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2">Image</Typography>
              <Typography variant="body1">{selected_image.name}</Typography>
            </Box>
            
            {selected_image.description && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Description</Typography>
                <Typography variant="body2">{selected_image.description}</Typography>
              </Box>
            )}
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              {selected_image.stars !== undefined && (
                <Box>
                  <Typography variant="subtitle2">Stars</Typography>
                  <Typography variant="body2">{selected_image.stars.toLocaleString()}</Typography>
                </Box>
              )}
              
              {selected_image.official !== undefined && (
                <Box>
                  <Typography variant="subtitle2">Official</Typography>
                  <Typography variant="body2">{selected_image.official ? 'Yes' : 'No'}</Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Box>
      )}
      
      {/* Configuration Details */}
      {config && (
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Configuration
          </Typography>
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            {/* Port Mappings */}
            {config.ports && Object.keys(config.ports).length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Port Mappings
                </Typography>
                <Box>{formatPorts(config.ports)}</Box>
              </Box>
            )}
            
            {/* Environment Variables */}
            {config.environment && Object.keys(config.environment).length > 0 && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Environment Variables
                </Typography>
                {formatEnv(config.environment)}
              </Box>
            )}
            
            {/* If no ports or env vars */}
            {(!config.ports || Object.keys(config.ports).length === 0) && 
             (!config.environment || Object.keys(config.environment).length === 0) && (
              <Typography variant="body2" color="text.secondary">
                No specific configuration provided. Using default settings.
              </Typography>
            )}
          </Paper>
        </Box>
      )}
      
      {/* Reasoning */}
      {reasoning && (
        <Box mt={3}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Reasoning</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {reasoning}
              </Typography>
            </AccordionDetails>
          </Accordion>
        </Box>
      )}

      {/* Access Links */}
      {access_links && Object.keys(access_links).length > 0 && (
        <Paper variant="outlined" sx={{ p: 2, mb: 3, bgcolor: '#222222', color: '#ffffff', border: '1px solid #444' }}>
          <Typography variant="h6" gutterBottom>
            Access Links
          </Typography>
          <List dense>
            {Object.entries(access_links).map(([type, url]) => (
              <ListItem key={type}>
                <ListItemIcon sx={{ minWidth: 36, color: '#ffffff' }}>
                  {type === 'web' && <LanguageIcon color="info" />}
                  {type === 'database' && <StorageIcon color="warning" />}
                  {type === 'admin' && <SettingsIcon color="error" />}
                  {type === 'dashboard' && <DashboardIcon color="success" />}
                  {type === 'jupyter' && <CodeIcon color="info" />}
                  {(type !== 'web' && type !== 'database' && type !== 'admin' && 
                    type !== 'dashboard' && type !== 'jupyter') && <LinkIcon />}
                </ListItemIcon>
                <ListItemText 
                  primary={`${type.charAt(0).toUpperCase() + type.slice(1)} Interface`}
                  secondary={
                    <Link 
                      href={url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      sx={{ color: '#8bc8ff' }}
                    >
                      {url}
                    </Link>
                  }
                />
                <Button
                  size="small"
                  variant="outlined"
                  color="info"
                  href={url}
                  target="_blank"
                  startIcon={<OpenInNewIcon />}
                  sx={{ ml: 2 }}
                >
                  Open
                </Button>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default DeploymentResult; 