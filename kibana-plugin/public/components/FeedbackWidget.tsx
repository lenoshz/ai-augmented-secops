import React, { useState } from 'react';
import { EuiButtonIcon, EuiFlexGroup, EuiFlexItem, EuiText } from '@elastic/eui';

interface FeedbackWidgetProps {
  alertId: string;
}

export const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({ alertId }) => {
  const [submitted, setSubmitted] = useState<boolean>(false);

  const submitFeedback = async (rating: 'up' | 'down') => {
    try {
      await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_id: alertId, rating, analyst_id: 'kibana-user' }),
      });
      setSubmitted(true);
    } catch {
      setSubmitted(false);
    }
  };

  return (
    <EuiFlexGroup gutterSize="s" alignItems="center" responsive={false}>
      <EuiFlexItem grow={false}>
        <EuiText size="s">Feedback:</EuiText>
      </EuiFlexItem>
      <EuiFlexItem grow={false}>
        <EuiButtonIcon iconType="thumbUp" aria-label="Thumbs up" onClick={() => submitFeedback('up')} />
      </EuiFlexItem>
      <EuiFlexItem grow={false}>
        <EuiButtonIcon iconType="thumbDown" aria-label="Thumbs down" onClick={() => submitFeedback('down')} />
      </EuiFlexItem>
      <EuiFlexItem>
        <EuiText size="s">{submitted ? 'Thanks for your feedback.' : ''}</EuiText>
      </EuiFlexItem>
    </EuiFlexGroup>
  );
};
