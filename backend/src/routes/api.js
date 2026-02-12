import { Router } from 'express';
import { supabase } from '../services/supabaseClient.js';
import { runCollectors } from '../collectors/runCollectors.js';

export const apiRouter = Router();

apiRouter.get('/health', (_req, res) => res.json({ ok: true }));

apiRouter.post('/collect/run', async (_req, res) => {
  try {
    const result = await runCollectors();
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

apiRouter.get('/videos', async (_req, res) => {
  const { data, error } = await supabase.from('videos').select('*').order('collected_at', { ascending: false }).limit(100);
  if (error) return res.status(500).json({ error: error.message });
  return res.json(data);
});

apiRouter.get('/news', async (_req, res) => {
  const { data, error } = await supabase.from('news').select('*').order('collected_at', { ascending: false }).limit(100);
  if (error) return res.status(500).json({ error: error.message });
  return res.json(data);
});

apiRouter.get('/drafts', async (_req, res) => {
  const { data, error } = await supabase.from('drafts').select('*').order('created_at', { ascending: false }).limit(100);
  if (error) return res.status(500).json({ error: error.message });
  return res.json(data);
});

apiRouter.patch('/drafts/:id', async (req, res) => {
  const { id } = req.params;
  const { draft_text, published } = req.body;
  const { data, error } = await supabase
    .from('drafts')
    .update({ draft_text, published })
    .eq('id', id)
    .select('*')
    .single();
  if (error) return res.status(500).json({ error: error.message });
  return res.json(data);
});

apiRouter.delete('/drafts/:id', async (req, res) => {
  const { id } = req.params;
  const { error } = await supabase.from('drafts').delete().eq('id', id);
  if (error) return res.status(500).json({ error: error.message });
  return res.status(204).send();
});
