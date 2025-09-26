'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Box, Grid, Paper, Typography, Tabs, Tab, Button } from '@mui/material';
import VoiceWidget from './components/voice/VoiceWidget';
import DemoViewer from './components/demo/DemoViewer';
import ChatInterface from './components/chat/ChatInterface';
import { StorylaneController } from './lib/storylaneController';

export default function Home() {
  const [activeTab, setActiveTab] = useState(0);
  const storylaneControllerRef = useRef<StorylaneController | null>(null);

  useEffect(() => {
    // Initialize Storylane controller immediately
    console.log('[Home] Initializing StorylaneController');
    const controller = new StorylaneController();
    storylaneControllerRef.current = controller;
    console.log('[Home] StorylaneController initialized:', !!controller);

    return () => {
      // Cleanup if needed
      console.log('[Home] Cleaning up StorylaneController');
    };
  }, []);

  // Ensure controller is ready before handling queries
  const isControllerReady = storylaneControllerRef.current !== null;

  const handleQueryReceived = (query: string) => {
    // Handle queries from voice or chat - navigate Storylane dashboard
    console.log('[Home] Chat query received:', query);
    if (storylaneControllerRef.current) {
      storylaneControllerRef.current.handleQuery(query, 'chat');
    } else {
      console.error('[Home] StorylaneController is null when handling chat query');
    }
  };

  const handleVoiceQueryReceived = (query: string) => {
    // Handle queries from voice - navigate Storylane dashboard
    console.log('[Home] Voice query received:', query);
    console.log('[Home] StorylaneController status:', !!storylaneControllerRef.current);
    console.log('[Home] Controller ready:', isControllerReady);
    
    if (storylaneControllerRef.current) {
      console.log('[Home] Calling storylaneController.handleQuery...');
      storylaneControllerRef.current.handleQuery(query, 'voice');
    } else {
      console.log('[Home] StorylaneController not ready yet, will retry...');
      // Retry after a short delay
      setTimeout(() => {
        console.log('[Home] Retry - StorylaneController status:', !!storylaneControllerRef.current);
        if (storylaneControllerRef.current) {
          console.log('[Home] Retry - Calling storylaneController.handleQuery...');
          storylaneControllerRef.current.handleQuery(query, 'voice');
        } else {
          console.error('[Home] StorylaneController still not ready after retry');
        }
      }, 1000);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Debug function to test navigation manually
  const debugTestNavigation = () => {
    console.log('[Home] DEBUG: Testing manual navigation');
    console.log('[Home] DEBUG: Controller exists:', !!storylaneControllerRef.current);
    
    if (storylaneControllerRef.current) {
      console.log('[Home] DEBUG: Testing navigation to alerts');
      storylaneControllerRef.current.handleQuery('show me the alerts', 'manual');
    } else {
      console.error('[Home] DEBUG: Controller is null');
    }
  };

  // Add debug function to global scope
  useEffect(() => {
    (window as any).debugTestNavigation = debugTestNavigation;
    console.log('[Home] DEBUG: Added debugTestNavigation to window');
    
    return () => {
      (window as any).debugTestNavigation = undefined;
    };
  }, []);

  return (
    <Box sx={{ flexGrow: 1, p: 2 }}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h4" component="h1" gutterBottom>
            DemoPilot - Interactive Carbon Black Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Ask questions via chat or voice to automatically navigate the Carbon Black dashboard to relevant sections.
          </Typography>
          
          {/* Debug buttons for testing */}
          <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
            <Button 
              variant="contained" 
              color="primary" 
              onClick={() => {
                console.log('[Home] Manual test - calling handleVoiceQueryReceived');
                handleVoiceQueryReceived('api access for custom integrations');
              }}
            >
              Test: API Access
            </Button>
            <Button 
              variant="contained" 
              color="secondary" 
              onClick={debugTestNavigation}
            >
              Debug: Alerts
            </Button>
            <Button 
              variant="outlined" 
              color="primary" 
              onClick={() => {
                console.log('[Home] DEBUG: Controller status:', !!storylaneControllerRef.current);
                console.log('[Home] DEBUG: Controller ref:', storylaneControllerRef.current);
              }}
            >
              Debug: Controller Status
            </Button>
            <Button 
              variant="outlined" 
              color="secondary" 
              onClick={() => {
                if (storylaneControllerRef.current) {
                  console.log('[Home] DEBUG: Resetting dashboard to main view');
                  storylaneControllerRef.current.resetDashboard('manual');
                } else {
                  console.error('[Home] DEBUG: Controller is null');
                }
              }}
            >
              Debug: Reset Dashboard
            </Button>
            <Button 
              variant="outlined" 
              color="error" 
              onClick={() => {
                if (storylaneControllerRef.current) {
                  console.log('[Home] DEBUG: Testing force reload to Policies');
                  storylaneControllerRef.current.handleQuery('show me the policies', 'manual');
                } else {
                  console.error('[Home] DEBUG: Controller is null');
                }
              }}
            >
              Debug: Force Reload Policies
            </Button>
            <Button 
              variant="outlined" 
              color="warning" 
              onClick={() => {
                if (storylaneControllerRef.current) {
                  console.log('[Home] DEBUG: Testing direct URL change');
                  // Test with a completely different URL to see if Storylane responds
                  const testUrl = 'https://app.storylane.io/share/filcrnbzfr0i?pageid=18c0582b-9aa5-4723-b272-23b2cedb24c7';
                  console.log('[Home] DEBUG: Testing URL:', testUrl);
                  
                  // Direct iframe manipulation
                  const iframe = document.querySelector('iframe[title="Interactive Carbon Black Dashboard"]');
                  if (iframe) {
                    console.log('[Home] DEBUG: Found iframe, changing src to:', testUrl);
                    iframe.src = testUrl;
                    console.log('[Home] DEBUG: Direct URL change completed');
                  } else {
                    console.error('[Home] DEBUG: Iframe not found');
                  }
                } else {
                  console.error('[Home] DEBUG: Controller is null');
                }
              }}
            >
              Debug: Direct URL Test
            </Button>
          </Box>
        </Grid>
        
        <Grid item xs={12}>
          <Paper elevation={3}>
            <Tabs value={activeTab} onChange={handleTabChange} aria-label="demo tabs">
              <Tab label="Interactive Dashboard" />
              <Tab label="Chat Interface" />
            </Tabs>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper elevation={3} sx={{ height: '80vh', overflow: 'hidden' }}>
            {activeTab === 0 && (
              <DemoViewer 
                onQueryReceived={handleQueryReceived}
                storylaneController={storylaneControllerRef.current || undefined}
              />
            )}
            {activeTab === 1 && (
              <ChatInterface onQueryReceived={handleQueryReceived} />
            )}
          </Paper>
        </Grid>
      </Grid>
      <VoiceWidget onQueryReceived={handleVoiceQueryReceived} />
    </Box>
  );
} 