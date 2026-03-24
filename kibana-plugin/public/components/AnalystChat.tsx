import React, { useState } from 'react';
import { EuiButton, EuiFieldText, EuiFlexGroup, EuiFlexItem, EuiText } from '@elastic/eui';

interface AnalystChatProps {
  alertContext: Record<string, unknown>;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export const AnalystChat: React.FC<AnalystChatProps> = ({ alertContext }) => {
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const updatedHistory: ChatMessage[] = [
      ...history,
      { id: `${Date.now()}-user`, role: 'user', content: input },
    ];
    setHistory(updatedHistory);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          history: updatedHistory.map(({ role, content }) => ({ role, content })),
          alert_context: alertContext,
        }),
      });
      const data = await response.json();
      setHistory([
        ...updatedHistory,
        { id: `${Date.now()}-assistant`, role: 'assistant', content: data.response || 'No response' },
      ]);
    } catch {
      setHistory([
        ...updatedHistory,
        { id: `${Date.now()}-assistant-error`, role: 'assistant', content: 'Chat request failed.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <EuiText size="s">
        {history.map((message) => (
          <p key={message.id}>
            <strong>{message.role}:</strong> {message.content}
          </p>
        ))}
      </EuiText>
      <EuiFlexGroup gutterSize="s">
        <EuiFlexItem>
          <EuiFieldText
            placeholder="Ask GenesisSOC analyst assistant"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                void sendMessage();
              }
            }}
          />
        </EuiFlexItem>
        <EuiFlexItem grow={false}>
          <EuiButton onClick={sendMessage} isLoading={loading}>
            Send
          </EuiButton>
        </EuiFlexItem>
      </EuiFlexGroup>
    </>
  );
};
