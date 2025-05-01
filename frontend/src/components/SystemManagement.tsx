import React, { useState, useEffect, useContext } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Tabs,
  Tab,
  Alert,
  Snackbar,
  CircularProgress,
  Card,
  CardContent
} from '@mui/material';
import { listContainers, listImages, removeContainer, removeImage, stopContainer } from '../services/api';
import { ContainerListItem } from '../types/api';
import { DockerImageListResponse } from '../services/api';
import { DebugContext } from '../App';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`system-tabpanel-${index}`}
      aria-labelledby={`system-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const SystemManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [containers, setContainers] = useState<ContainerListItem[]>([]);
  const [images, setImages] = useState<DockerImageListResponse['images']>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [errorDetails, setErrorDetails] = useState<any | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { debugMode } = useContext(DebugContext);

  const fetchContainers = async () => {
    try {
      setLoading(true);
      const response = await listContainers();
      setContainers(response.containers);
      setError(null);
      setErrorDetails(null);
    } catch (err: any) {
      setError('Failed to fetch containers');
      setErrorDetails(err);
      console.error('Error fetching containers:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchImages = async () => {
    try {
      setLoading(true);
      const response = await listImages();
      setImages(response.images);
      setError(null);
      setErrorDetails(null);
    } catch (err: any) {
      setError('Failed to fetch images');
      setErrorDetails(err);
      console.error('Error fetching images:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (tabValue === 0) {
      fetchContainers();
    } else {
      fetchImages();
    }
  }, [tabValue]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleRefresh = () => {
    if (tabValue === 0) {
      fetchContainers();
    } else {
      fetchImages();
    }
  };

  const handleRemoveContainer = async (containerId: string) => {
    try {
      setLoading(true);
      const result = await removeContainer(containerId);
      if (result.status) {
        setSuccess('Container removed successfully');
        fetchContainers(); // Refresh the list
      } else {
        setError(`Failed to remove container: ${result.message}`);
        setErrorDetails(result.error_details || null);
      }
    } catch (err: any) {
      setError('Failed to remove container');
      setErrorDetails(err);
      console.error('Error removing container:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveImage = async (imageId: string) => {
    try {
      setLoading(true);
      const result = await removeImage(imageId);
      if (result.status) {
        setSuccess('Image removed successfully');
        fetchImages(); // Refresh the list
      } else {
        setError(`Failed to remove image: ${result.message}`);
        setErrorDetails(result.error_details || null);
      }
    } catch (err: any) {
      setError('Failed to remove image');
      setErrorDetails(err);
      console.error('Error removing image:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStopContainer = async (containerId: string) => {
    try {
      setLoading(true);
      const result = await stopContainer(containerId);
      if (result.status) {
        setSuccess(`Container ${containerId.slice(0, 8)} stopped successfully`);
        await fetchContainers(); // Refresh the list
      } else {
        setError(`Failed to stop container: ${result.message}`);
        setErrorDetails(result.error_details || null);
      }
    } catch (err: any) {
      setError('Failed to stop container');
      setErrorDetails(err);
      console.error('Error stopping container:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setError(null);
    setSuccess(null);
    setErrorDetails(null);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="system management tabs" variant="fullWidth">
          <Tab label="Containers" />
          <Tab label="Images" />
        </Tabs>
      </Box>

      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Button 
          variant="contained" 
          onClick={handleRefresh}
          disabled={loading}
          sx={{ minWidth: '120px' }}
        >
          {loading ? <CircularProgress size={24} /> : 'Refresh'}
        </Button>
      </Box>

      {/* Debug error information */}
      {debugMode && error && errorDetails && (
        <Card variant="outlined" sx={{ mb: 3, bgcolor: '#fff8f8' }}>
          <CardContent>
            <Typography variant="h6" color="error">
              Debug Information
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Typography variant="subtitle2">Error Message:</Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 1 }}>
                {error}
              </Typography>
              
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
      )}

      <TabPanel value={tabValue} index={0}>
        <Typography variant="h6" gutterBottom>
          Running Containers
        </Typography>
        <TableContainer component={Paper} sx={{ maxHeight: '400px', overflow: 'auto' }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>ID</TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Name</TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Image</TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Ports</TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {containers.length > 0 ? (
                containers.map((container) => (
                  <TableRow key={container.id} hover>
                    <TableCell sx={{ fontFamily: 'monospace' }}>{container.id.slice(0, 12)}</TableCell>
                    <TableCell>{container.name}</TableCell>
                    <TableCell>{container.image}</TableCell>
                    <TableCell>{container.status}</TableCell>
                    <TableCell>
                      {container.ports && Object.entries(container.ports).map(([port, target]) => (
                        <div key={port}>{`${target}:${port.split('/')[0]}`}</div>
                      ))}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button 
                          variant="outlined" 
                          size="small" 
                          color="warning" 
                          onClick={() => handleStopContainer(container.id)}
                          disabled={loading || container.status.toLowerCase().includes('exited')}
                        >
                          Stop
                        </Button>
                        <Button 
                          variant="outlined" 
                          size="small" 
                          color="error" 
                          onClick={() => handleRemoveContainer(container.id)}
                          disabled={loading}
                        >
                          Remove
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    {loading ? 'Loading...' : 'No containers found'}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Typography variant="h6" gutterBottom>
          Docker Images
        </Typography>
        <TableContainer component={Paper} sx={{ maxHeight: '400px', overflow: 'auto' }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>ID</TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Repository</TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Tag</TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Size</TableCell>
                <TableCell sx={{ fontWeight: 'bold', backgroundColor: '#f5f5f5' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {images.length > 0 ? (
                images.map((image) => (
                  <TableRow key={image.id} hover>
                    <TableCell sx={{ fontFamily: 'monospace' }}>{image.id.slice(0, 12)}</TableCell>
                    <TableCell>{image.repository}</TableCell>
                    <TableCell>{image.tag}</TableCell>
                    <TableCell>{image.size}</TableCell>
                    <TableCell>
                      <Button 
                        variant="outlined" 
                        size="small" 
                        color="error" 
                        onClick={() => handleRemoveImage(image.id)}
                        disabled={loading}
                      >
                        Remove
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    {loading ? 'Loading...' : 'No images found'}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <Snackbar 
        open={!!error || !!success} 
        autoHideDuration={5000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        {error ? (
          <Alert onClose={handleCloseSnackbar} severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        ) : (
          <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
            {success}
          </Alert>
        )}
      </Snackbar>
    </Box>
  );
};

export default SystemManagement; 