'use client';

import React, { useState } from 'react';
import { Box, TextField, Button, List, ListItem, ListItemText, Paper, Typography } from '@mui/material';
import { queryKnowledge, KNOWLEDGE_ERROR_MESSAGE } from '../../lib/knowledgeClient';

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

    try {
      const data = await queryKnowledge(query);
      const botMessage: Message = { sender: 'bot', text: data.response };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorText =
        error instanceof Error && error.message ? error.message : KNOWLEDGE_ERROR_MESSAGE;
      const errorMessage: Message = {
        sender: 'bot',
        text: errorText,
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
