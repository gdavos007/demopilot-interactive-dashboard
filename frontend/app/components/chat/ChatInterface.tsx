'use client';

import React, { useState } from 'react';
import { Box, TextField, Button, List, ListItem, ListItemText, Paper, Typography } from '@mui/material';

interface Message {
  sender: 'user' | 'bot';
  text: string;
}

interface ChatInterfaceProps {
  onQueryReceived?: (query: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onQueryReceived }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (input.trim() === '' || isLoading) return;

    const query = input.trim();
    const userMessage: Message = { sender: 'user', text: query };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    onQueryReceived?.(query);

    const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000'}/api/v1/knowledge/query`;

    try {
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const botMessage: Message = { sender: 'bot', text: data.response };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        sender: 'bot',
        text: 'I apologize, but I encountered an error processing your request. Please try again or check your connection.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        minHeight: 0,
        boxSizing: 'border-box',
      }}
    >
      <Paper
        sx={{
          flex: 1,
          minHeight: 0,
          overflow: 'auto',
          p: 2,
          mb: 2,
          backgroundColor: 'background.default',
        }}
      >
        {messages.length === 0 ? (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
            <Typography variant="body1" color="text.secondary" align="center">
              Ask a question about Carbon Black — for example:
              <br />
              &quot;What platforms are supported?&quot; or &quot;Show me the alerts&quot;
            </Typography>
          </Box>
        ) : (
          <List>
            {messages.map((msg, index) => (
              <ListItem key={index} sx={{ flexDirection: 'column', alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
                <ListItemText
                  primary={msg.text}
                  primaryTypographyProps={{ align: msg.sender === 'user' ? 'right' : 'left' }}
                />
              </ListItem>
            ))}
          </List>
        )}
        {isLoading && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Thinking...
          </Typography>
        )}
      </Paper>
      <Box sx={{ display: 'flex', flexShrink: 0 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
          disabled={isLoading}
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={isLoading || input.trim() === ''}
          sx={{ ml: 1, minWidth: 88 }}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default ChatInterface;
