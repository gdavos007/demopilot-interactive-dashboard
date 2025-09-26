'use client';

import React, { useState, useEffect } from 'react';
import Vapi from '@vapi-ai/web';
import { Fab, CircularProgress } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';

const vapi = new Vapi(process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY as string);

// Debug VAPI initialization
console.log('[VoiceWidget] VAPI public key:', process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY ? 'Set' : 'Not set');
console.log('[VoiceWidget] VAPI client initialized:', !!vapi);

interface VoiceWidgetProps {
  onQueryReceived?: (query: string) => void;
}

const VoiceWidget: React.FC<VoiceWidgetProps> = ({ onQueryReceived }) => {
  console.log('[VoiceWidget] Component initialized with onQueryReceived:', !!onQueryReceived);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    vapi.on('call-start', () => {
      setIsSessionActive(true);
      setIsProcessing(false);
    });

    vapi.on('call-end', () => {
      setIsSessionActive(false);
      setIsProcessing(false);
    });

    vapi.on('speech-start', () => {
      setIsProcessing(true);
    });
    
    vapi.on('speech-end', () => {
      setIsProcessing(false);
    });

    vapi.on('message', async (message) => {
      if (message.type === 'transcript' && message.transcriptType === 'final' && message.role === 'user') {
        const query = message.transcript;
        console.log(`[VoiceWidget] Received voice query: "${query}"`);
        
        // Notify parent component about the query for dashboard integration
        console.log('[VoiceWidget] Calling onQueryReceived with query:', query);
        if (onQueryReceived) {
          onQueryReceived(query);
          console.log('[VoiceWidget] onQueryReceived called successfully');
        } else {
          console.error('[VoiceWidget] onQueryReceived is not defined!');
        }
        
        // Temporarily skip backend call to focus on dashboard navigation
        console.log('[VoiceWidget] Skipping backend call for now - focusing on dashboard navigation');
        
        // Send a simple response to the user
        vapi.send({
          type: 'add-message',
          message: {
            role: 'system',
            content: `I heard your question: "${query}". Let me navigate to the relevant section of the dashboard.`,
          },
        });
      }
    });

    return () => {
      vapi.removeAllListeners();
    };
  }, []);

  const handleToggleCall = async () => {
    if (isSessionActive) {
      vapi.stop();
    } else {
      try {
        console.log('[VoiceWidget] Starting VAPI call...');
        await vapi.start({
          model: {
            provider: 'openai',
            model: 'gpt-4o-mini',
            messages: [
              {
                role: 'system',
                content: 'You are a helpful assistant for Carbon Black product questions. Keep responses concise and helpful.',
              },
            ],
          },
          voice: {
            provider: '11labs',
            voiceId: 'burt',
          },
        });
        console.log('[VoiceWidget] VAPI call started successfully');
      } catch (error) {
        console.error('[VoiceWidget] Error starting VAPI call:', error);
        // Show user-friendly error message
        alert('Failed to start voice call. Please check your VAPI configuration.');
      }
    }
  };

  return (
    <Fab
      color={isSessionActive ? 'secondary' : 'primary'}
      aria-label="toggle voice"
      onClick={handleToggleCall}
      sx={{ position: 'fixed', bottom: 16, right: 16 }}
    >
      {isProcessing ? <CircularProgress color="inherit" /> : (isSessionActive ? <MicOffIcon /> : <MicIcon />)}
    </Fab>
  );
};

export default VoiceWidget; 