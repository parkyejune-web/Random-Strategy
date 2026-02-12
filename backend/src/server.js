import express from 'express';
import cors from 'cors';
import { config } from './config.js';
import { apiRouter } from './routes/api.js';
import { runCollectors } from './collectors/runCollectors.js';

const app = express();
app.use(cors());
app.use(express.json());
app.use('/api', apiRouter);

app.listen(config.port, () => {
  console.log(`Backend started on http://localhost:${config.port}`);
});

setInterval(() => {
  runCollectors().catch((error) => {
    console.error('Auto collector failed:', error.message);
  });
}, config.autoCollectMinutes * 60 * 1000);
