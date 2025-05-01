import React, { useState, useEffect } from 'react';
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
  Chip,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import { Stop as StopIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import { listContainers, stopContainer } from '../services/api';
import { ContainerListItem } from '../types/api';

const ContainerList: React.FC = () => {
  const [containers, setContainers] = useState<ContainerListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);
  const [error, setError] = useState('');

  const fetchContainers = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await listContainers();
      setContainers(response.containers);
    } catch (err) {
      setError('Failed to load containers');
      console.error('Error fetching containers:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopContainer = async (containerId: string) => {
    setActionInProgress(containerId);
    try {
      const response = await stopContainer(containerId);
      if (response.status) {
        // Refresh container list after successful stop
        fetchContainers();
      } else {
        setError(`Failed to stop container: ${response.message}`);
      }
    } catch (err) {
      setError('Failed to stop container');
      console.error('Error stopping container:', err);
    } finally {
      setActionInProgress(null);
    }
  };

  useEffect(() => {
    fetchContainers();
    // Set up polling interval to refresh containers periodically
    const interval = setInterval(fetchContainers, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Format port mappings for display
  const formatPorts = (ports: Record<string, any> | undefined) => {
    if (!ports || Object.keys(ports).length === 0) {
      return 'None';
    }
    
    return Object.entries(ports)
      .map(([key, value]) => {
        // Handle different formats of port mappings
        if (Array.isArray(value)) {
          return value.map(v => `${v.HostIp || '0.0.0.0'}:${v.HostPort}->${key}`).join(', ');
        }
        return `${key}->${value}`;
      })
      .join(', ');
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h2">
          Running Containers
        </Typography>
        <Tooltip title="Refresh containers">
          <IconButton onClick={fetchContainers} disabled={isLoading}>
            {isLoading ? <CircularProgress size={24} /> : <RefreshIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {containers.length === 0 ? (
        <Typography variant="body1" sx={{ textAlign: 'center', py: 3 }}>
          No containers are currently running
        </Typography>
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Container ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Image</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Ports</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {containers.map((container) => (
                <TableRow key={container.id}>
                  <TableCell>{container.id}</TableCell>
                  <TableCell>{container.name}</TableCell>
                  <TableCell>{container.image}</TableCell>
                  <TableCell>
                    <Chip 
                      label={container.status} 
                      color={container.status.includes('running') ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{formatPorts(container.ports)}</TableCell>
                  <TableCell>
                    <Button
                      startIcon={actionInProgress === container.id ? <CircularProgress size={20} /> : <StopIcon />}
                      variant="outlined"
                      color="error"
                      size="small"
                      onClick={() => handleStopContainer(container.id)}
                      disabled={actionInProgress === container.id}
                    >
                      Stop
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  );
};

export default ContainerList; 