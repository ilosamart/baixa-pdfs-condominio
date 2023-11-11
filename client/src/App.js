import React from 'react';
import { Button } from '@fluentui/react-components';
import { StackShim as Stack, StackItemShim as StackItem} from "@fluentui/react-migration-v8-v9";

const App = () => (<Stack grow verticalFill>
  
  <StackItem>
  <Button appearance="primary">Get started</Button>
  </StackItem>
  </Stack>
  );

export default App;