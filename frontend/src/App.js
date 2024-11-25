import { PlasmicRootProvider, PlasmicComponent } from '@plasmicapp/loader-react';
import { PLASMIC } from './plasmic-init';

function App() {
  return (
    <PlasmicRootProvider loader={PLASMIC}>
      <PlasmicComponent component="/" />
    </PlasmicRootProvider>
  );
}

export default App;
