'use client';

import React, { useRef, useEffect, useState } from 'react';
import { Box, Paper, Typography, Chip, IconButton, Tooltip } from '@mui/material';
import { 
  Refresh as RefreshIcon, 
  Home as HomeIcon,
  Info as InfoIcon 
} from '@mui/icons-material';
import { StorylaneController, NavigationEvent } from '../../lib/storylaneController';
import { STORYLANE_BASE_URL } from '../../lib/storylaneConfig';

interface DemoViewerProps {
  onQueryReceived?: (query: string) => void;
  storylaneController?: StorylaneController;
}

const DemoViewer: React.FC<DemoViewerProps> = ({ 
  onQueryReceived, 
  storylaneController 
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [currentSection, setCurrentSection] = useState<string>('Main Dashboard');
  const [isLoading, setIsLoading] = useState(false);

  // Set up the iframe reference in the controller
  useEffect(() => {
    if (storylaneController) {
      console.log('[DemoViewer] Setting up StorylaneController with iframe ref');
      console.log('[DemoViewer] Iframe ref:', iframeRef.current);
      storylaneController.setIframeRef(iframeRef);
      
      // Listen for navigation events
      const handleNavigation = (event: NavigationEvent) => {
        console.log('[DemoViewer] Navigation event received:', event);
        if (event.section) {
          setCurrentSection(event.section.name);
        }
        setIsLoading(false);
      };

      storylaneController.addNavigationListener(handleNavigation);

      return () => {
        console.log('[DemoViewer] Cleaning up StorylaneController listeners');
        storylaneController.removeNavigationListener(handleNavigation);
      };
    } else {
      console.log('[DemoViewer] StorylaneController not ready yet, will retry when available');
    }
  }, [storylaneController]);

  // Additional effect to ensure iframe ref is set when iframe loads
  useEffect(() => {
    if (storylaneController && iframeRef.current) {
      console.log('[DemoViewer] Iframe loaded, ensuring ref is set in controller');
      storylaneController.setIframeRef(iframeRef);
    }
  }, [storylaneController, iframeRef.current]);

  const handleRefresh = () => {
    if (iframeRef.current) {
      setIsLoading(true);
      iframeRef.current.src = iframeRef.current.src;
    }
  };

  const handleHome = () => {
    if (storylaneController) {
      setIsLoading(true);
      storylaneController.resetDashboard('manual');
      setCurrentSection('Main Dashboard');
    }
  };

  const handleIframeLoad = () => {
    setIsLoading(false);
    // Ensure the iframe ref is set in the controller when iframe loads
    if (storylaneController && iframeRef.current) {
      console.log('[DemoViewer] Iframe loaded, setting ref in controller');
      storylaneController.setIframeRef(iframeRef);
    }
  };

  // Show iframe immediately; controller enables navigation once ready
  const canNavigate = !!storylaneController;

  return (
    <Box sx={{ height: '80vh', width: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Dashboard Header */}
      <Paper elevation={1} sx={{ p: 1, mb: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box display="flex" alignItems="center" gap={1}>
          <Chip 
            label={currentSection} 
            color="primary" 
            variant="outlined" 
            size="small" 
          />
        </Box>
        
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh Dashboard">
            <IconButton onClick={handleRefresh} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title={canNavigate ? 'Return to Main Dashboard' : 'Navigation initializing...'}>
            <span>
              <IconButton onClick={handleHome} size="small" disabled={!canNavigate}>
                <HomeIcon />
              </IconButton>
            </span>
          </Tooltip>
          
          <Tooltip title="Interactive Dashboard - Ask questions via chat or voice to navigate automatically">
            <IconButton size="small">
              <InfoIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>

      {/* Storylane iframe */}
      <Box sx={{ flex: 1, position: 'relative' }}>
        {isLoading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
              zIndex: 1000,
            }}
          >
            <Typography variant="h6">Loading dashboard...</Typography>
          </Box>
        )}
        
        <iframe
          ref={iframeRef}
          src={STORYLANE_BASE_URL}
          style={{ border: 'none', height: '100%', width: '100%' }}
          title="Interactive Dashboard"
          onLoad={handleIframeLoad}
          key="storylane-iframe"
        />
      </Box>
    </Box>
  );
};

export default DemoViewer; 