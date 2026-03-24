import React, { useEffect, useState } from 'react';
import { EuiPageTemplate, EuiSpacer, EuiTitle } from '@elastic/eui';
import { AlertCard } from './AlertCard';

interface EnrichedAlert {
  alert_id: string;
  narrative: string;
  context: {
    mitre: { tactic: string; technique_id: string; technique_name: string };
    asset_criticality: string;
    ioc_matches: string[];
    similar_hits_7d: number;
  };
  response: {
    steps: Array<{ step: number; action: string; detail: string }>;
    eql_query: string;
    escalate: boolean;
  };
}

export const GenesisSOCApp: React.FC = () => {
  const [alerts, setAlerts] = useState<EnrichedAlert[]>([]);

  const pollAlerts = async () => {
    try {
      const response = await fetch('/api/v1/alerts/enriched');
      if (!response.ok) {
        return;
      }
      const data = await response.json();
      setAlerts(Array.isArray(data) ? data : []);
    } catch {
      setAlerts([]);
    }
  };

  useEffect(() => {
    void pollAlerts();
    const timer = window.setInterval(() => {
      void pollAlerts();
    }, 15000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <EuiPageTemplate panelled={false} grow={true}>
      <EuiPageTemplate.Header pageTitle="GenesisSOC" />
      <EuiPageTemplate.Section>
        <EuiTitle size="l">
          <h2>AI-Augmented SecOps Alerts</h2>
        </EuiTitle>
        <EuiSpacer size="m" />
        {alerts.map((alert) => (
          <React.Fragment key={alert.alert_id}>
            <AlertCard alert={alert} />
            <EuiSpacer size="m" />
          </React.Fragment>
        ))}
      </EuiPageTemplate.Section>
    </EuiPageTemplate>
  );
};
