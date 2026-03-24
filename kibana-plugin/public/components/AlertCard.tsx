import React, { useState } from 'react';
import {
  EuiBadge,
  EuiCallOut,
  EuiFlexGroup,
  EuiFlexItem,
  EuiPanel,
  EuiSpacer,
  EuiAccordion,
  EuiText,
  EuiListGroup,
  EuiListGroupItem,
} from '@elastic/eui';
import { AnalystChat } from './AnalystChat';
import { FeedbackWidget } from './FeedbackWidget';

interface ResponseStep {
  step: number;
  action: string;
  detail: string;
}

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
    steps: ResponseStep[];
    eql_query: string;
    escalate: boolean;
  };
}

interface AlertCardProps {
  alert: EnrichedAlert;
}

const criticalityColor = (criticality: string): 'danger' | 'warning' | 'success' | 'hollow' => {
  if (criticality === 'critical') return 'danger';
  if (criticality === 'high') return 'warning';
  if (criticality === 'medium' || criticality === 'low') return 'success';
  return 'hollow';
};

export const AlertCard: React.FC<AlertCardProps> = ({ alert }) => {
  const [isAccordionOpen, setAccordionOpen] = useState<boolean>(false);

  return (
    <EuiPanel hasBorder={true} paddingSize="m">
      <EuiFlexGroup gutterSize="s" alignItems="center" responsive={false}>
        <EuiFlexItem grow={false}>
          <EuiBadge color="primary">{alert.context.mitre.technique_id}</EuiBadge>
        </EuiFlexItem>
        <EuiFlexItem grow={false}>
          <EuiBadge color={criticalityColor(alert.context.asset_criticality)}>
            {alert.context.asset_criticality}
          </EuiBadge>
        </EuiFlexItem>
      </EuiFlexGroup>

      <EuiSpacer size="s" />
      <EuiCallOut title={`Alert ${alert.alert_id}`} color="primary" iconType="securitySignalDetected">
        <p>{alert.narrative}</p>
      </EuiCallOut>

      <EuiSpacer size="s" />
      <EuiText size="s">
        <p>
          MITRE: {alert.context.mitre.tactic} · {alert.context.mitre.technique_name}
        </p>
      </EuiText>

      <EuiSpacer size="s" />
      <EuiAccordion
        id={`response-steps-${alert.alert_id}`}
        buttonContent="Suggested response steps"
        forceState={isAccordionOpen ? 'open' : 'closed'}
        onToggle={() => setAccordionOpen(!isAccordionOpen)}
      >
        <EuiListGroup flush={true}>
          {alert.response.steps.map((step) => (
            <EuiListGroupItem key={`${alert.alert_id}-${step.step}`} label={`${step.step}. ${step.action}: ${step.detail}`} />
          ))}
        </EuiListGroup>
        <EuiSpacer size="s" />
        <EuiText size="s">
          <p>EQL Hunt Query: {alert.response.eql_query}</p>
        </EuiText>
      </EuiAccordion>

      <EuiSpacer size="m" />
      <AnalystChat alertContext={alert.context} />

      <EuiSpacer size="s" />
      <FeedbackWidget alertId={alert.alert_id} />
    </EuiPanel>
  );
};
