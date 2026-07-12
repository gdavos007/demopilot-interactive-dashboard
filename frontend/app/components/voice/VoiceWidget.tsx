'use client';

import React, { useState, useEffect, useRef } from 'react';
import Vapi from '@vapi-ai/web';
import { Fab, CircularProgress } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import { queryKnowledge, KNOWLEDGE_ERROR_MESSAGE } from '../../lib/knowledgeClient';

interface VoiceWidgetProps {
  onQueryReceived?: (query: string) => void;
}

const VOICE_ASSISTANT_OVERRIDES = {
  firstMessageMode: 'assistant-waits-for-user' as const,
};

function formatVapiError(error: unknown): string {
  if (!error) return 'Unknown VAPI error';
  if (typeof error === 'string') return error;
  if (error instanceof Error) return error.message;
  try {
    return JSON.stringify(error);
  } catch {
    return String(error);
  }
}

// VAPI runs calls over Daily.co WebRTC. When the room closes, Daily "ejects"
// the client and the SDK forwards it through the 'error' channel even though
// it's just the call ending (a 'call-end' event also fires). Treat these as a
// normal end-of-call rather than a real error so the demo console stays clean.
function isCallEndedError(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;
  const e = error as Record<string, any>;
  if (
    e?.error?.error?.type === 'ejected' ||
    e?.error?.message?.type === 'ejected' ||
    e?.error?.errorMsg === 'Meeting has ended'
  ) {
    return true;
  }
  try {
    return /ejected|meeting has ended/i.test(JSON.stringify(error));
  } catch {
    return false;
  }
}

const VoiceWidget: React.FC<VoiceWidgetProps> = ({ onQueryReceived }) => {
  const vapiRef = useRef<Vapi | null>(null);
  const onQueryReceivedRef = useRef(onQueryReceived);
  const isHandlingTranscriptRef = useRef(false);
  const [isReady, setIsReady] = useState(false);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    onQueryReceivedRef.current = onQueryReceived;
  }, [onQueryReceived]);

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
      isHandlingTranscriptRef.current = false;
    });

    vapi.on('speech-start', () => {
      if (!isHandlingTranscriptRef.current) {
        setIsProcessing(true);
      }
    });

    vapi.on('speech-end', () => {
      if (!isHandlingTranscriptRef.current) {
        setIsProcessing(false);
      }
    });

    vapi.on('error', (error) => {
      // End-of-call ejection from Daily isn't a real error — reset state quietly.
      if (isCallEndedError(error)) {
        console.info('[VoiceWidget] Voice call ended (VAPI/Daily): meeting has ended');
        setIsProcessing(false);
        setIsSessionActive(false);
        isHandlingTranscriptRef.current = false;
        return;
      }
      console.error('[VoiceWidget] VAPI error:', formatVapiError(error));
      setIsProcessing(false);
      isHandlingTranscriptRef.current = false;
    });

    vapi.on('message', async (message) => {
      if (message.type !== 'transcript' || message.transcriptType !== 'final' || message.role !== 'user') {
        return;
      }

      const query = message.transcript?.trim();
      if (!query || isHandlingTranscriptRef.current) {
        return;
      }

      isHandlingTranscriptRef.current = true;
      setIsProcessing(true);
      console.log(`[VoiceWidget] Received voice query: "${query}"`);

      onQueryReceivedRef.current?.(query);

      try {
        console.log('[VoiceWidget] Querying Product Knowledge Agent...');
        const data = await queryKnowledge(query);
        console.log('[VoiceWidget] Knowledge agent response received');

        vapi.say(data.response);
      } catch (error) {
        console.error('[VoiceWidget] Knowledge query error:', error);
        vapi.say(KNOWLEDGE_ERROR_MESSAGE);
      } finally {
        isHandlingTranscriptRef.current = false;
        setIsProcessing(false);
      }
    });

    return () => {
      vapi.stop();
      vapi.removeAllListeners();
      vapiRef.current = null;
    };
  }, []);

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
      await vapi.start(assistantId, VOICE_ASSISTANT_OVERRIDES);
      console.log('[VoiceWidget] VAPI call started successfully');
    } catch (error) {
      console.error('[VoiceWidget] Error starting VAPI call:', formatVapiError(error));
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
