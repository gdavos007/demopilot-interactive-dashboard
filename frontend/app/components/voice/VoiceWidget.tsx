'use client';

import React, { useState, useEffect, useRef } from 'react';
import Vapi from '@vapi-ai/web';
import { Fab, CircularProgress } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';

interface VoiceWidgetProps {
  onQueryReceived?: (query: string) => void;
}

const VoiceWidget: React.FC<VoiceWidgetProps> = ({ onQueryReceived }) => {
  const vapiRef = useRef<Vapi | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const publicKey = process.env.NEXT_PUBLIC_VAPI_PUBLIC_KEY;
    if (!publicKey) {
      console.error('[VoiceWidget] NEXT_PUBLIC_VAPI_PUBLIC_KEY is not set');
      return;
    }

    const vapi = new Vapi(publicKey);
    vapiRef.current = vapi;
    setIsReady(true);
    console.log('[VoiceWidget] VAPI client initialized');

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

    vapi.on('error', (error) => {
      console.error('[VoiceWidget] VAPI error:', error);
      setIsProcessing(false);
    });

    vapi.on('message', async (message) => {
      if (message.type === 'transcript' && message.transcriptType === 'final' && message.role === 'user') {
        const query = message.transcript;
        console.log(`[VoiceWidget] Received voice query: "${query}"`);

        onQueryReceived?.(query);

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
      vapi.stop();
      vapi.removeAllListeners();
      vapiRef.current = null;
    };
  }, [onQueryReceived]);

  const handleToggleCall = async () => {
    const vapi = vapiRef.current;
    if (!vapi) {
      alert('Voice is not configured. Add NEXT_PUBLIC_VAPI_PUBLIC_KEY to frontend/.env.local');
      return;
    }

    if (isSessionActive) {
      vapi.stop();
      return;
    }

    const assistantId = process.env.NEXT_PUBLIC_VAPI_ASSISTANT_ID;
    if (!assistantId) {
      alert('Voice assistant is not configured. Add NEXT_PUBLIC_VAPI_ASSISTANT_ID to frontend/.env.local');
      return;
    }

    try {
      console.log('[VoiceWidget] Starting VAPI call with assistant:', assistantId);
      await vapi.start(assistantId);
      console.log('[VoiceWidget] VAPI call started successfully');
    } catch (error) {
      console.error('[VoiceWidget] Error starting VAPI call:', error);
      alert('Failed to start voice call. Check your VAPI public key and assistant ID.');
    }
  };

  return (
    <Fab
      color={isSessionActive ? 'secondary' : 'primary'}
      aria-label="toggle voice"
      onClick={handleToggleCall}
      disabled={!isReady}
      sx={{ position: 'fixed', bottom: 16, right: 16 }}
    >
      {isProcessing ? <CircularProgress color="inherit" /> : (isSessionActive ? <MicOffIcon /> : <MicIcon />)}
    </Fab>
  );
};

export default VoiceWidget;
