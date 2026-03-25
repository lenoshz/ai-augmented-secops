import { AppMountParameters, CoreSetup, CoreStart, Plugin } from '@kbn/core/public';
import React from 'react';
import ReactDOM from 'react-dom';
import { GenesisSOCApp } from './components/GenesisSOCApp';

export class GenesisSOCPlugin implements Plugin {
  public setup(core: CoreSetup): void {
    core.application.register({
      id: 'genesissoc',
      title: 'GenesisSOC',
      async mount(params: AppMountParameters) {
        ReactDOM.render(React.createElement(GenesisSOCApp), params.element);
        return () => ReactDOM.unmountComponentAtNode(params.element);
      },
    });
  }

  public start(_core: CoreStart): void {}

  public stop(): void {}
}
