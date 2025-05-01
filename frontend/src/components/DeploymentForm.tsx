import React, { useState, useContext } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Card, 
  CardContent, 
  Typography, 
  CircularProgress,
  Alert
} from '@mui/material';
import { deployContainer } from '../services/api';
import DeploymentResult from './DeploymentResult';
import { DebugContext } from '../App';

const DeploymentForm: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorDetails, setErrorDetails] = useState<any | null>(null);
  const [deploymentResult, setDeploymentResult] = useState<any | null>(null);
  const { debugMode } = useContext(DebugContext);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError('Please enter a deployment prompt');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setErrorDetails(null);
      setDeploymentResult(null);
      
      const result = await deployContainer(prompt);
      setDeploymentResult(result);
    } catch (err: any) {
      setError('Failed to deploy container');
      setErrorDetails(err);
      console.error('Deployment error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Card variant="outlined">
        <CardContent>
          <Typography variant="h5" component="div" gutterBottom>
            Deploy a Container
          </Typography>
          
          <form onSubmit={handleSubmit}>
            <TextField
              label="What would you like to deploy?"
              variant="outlined"
              fullWidth
              multiline
              rows={3}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Example: Deploy a Redis server with password protection"
              sx={{ mb: 2 }}
              disabled={loading}
            />
            
            <Button 
              type="submit" 
              variant="contained" 
              color="primary" 
              disabled={loading || !prompt.trim()}
              sx={{ minWidth: '120px' }}
            >
              {loading ? <CircularProgress size={24} /> : 'Deploy'}
            </Button>
          </form>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {/* Debug error information */}
          {debugMode && error && errorDetails && (
            <Box sx={{ mt: 2 }}>
              <Card variant="outlined" sx={{ bgcolor: '#fff8f8' }}>
                <CardContent>
                  <Typography variant="h6" color="error">
                    Debug Information
                  </Typography>
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="subtitle2">Error Details:</Typography>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 1, whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(errorDetails, null, 2)}
                    </Typography>

                    {errorDetails?.stack && (
                      <>
                        <Typography variant="subtitle2">Stack Trace:</Typography>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            fontFamily: 'monospace', 
                            whiteSpace: 'pre-wrap',
                            fontSize: '0.75rem',
                            overflowX: 'auto'
                          }}
                        >
                          {errorDetails.stack}
                        </Typography>
                      </>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Box>
          )}
        </CardContent>
      </Card>

      {deploymentResult && (
        <Box sx={{ mt: 3 }}>
          <DeploymentResult result={deploymentResult} />
        </Box>
      )}
    </Box>
  );
};

export default DeploymentForm; 