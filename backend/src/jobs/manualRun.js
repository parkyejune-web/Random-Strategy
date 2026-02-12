import { runCollectors } from '../collectors/runCollectors.js';

runCollectors()
  .then((result) => {
    console.log('Collector result:', result);
    process.exit(0);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
