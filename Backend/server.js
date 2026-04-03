const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const { videoQueue } = require('./queue');
const redis = require('./redis');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Security and Logging
app.use(helmet());
app.use(morgan('dev'));
app.use(cors());
app.use(express.json());

// Rate Limiting (5 requests per min per IP)
const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 5,
  message: { error: 'Too many requests, please try again after a minute.' },
});
app.use('/api/generate', limiter);

// Helper to extract YouTube Video ID
const getYoutubeId = (url) => {
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  const match = url.match(regExp);
  return (match && match[2].length === 11) ? match[2] : null;
};

// POST /api/generate
app.post('/api/generate', async (req, res) => {
  const { url } = req.body;
  if (!url) return res.status(400).json({ error: 'URL is required' });

  const videoId = getYoutubeId(url);
  if (!videoId) return res.status(400).json({ error: 'Invalid YouTube URL' });

  try {
    const thumbnail = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
    
    // 1. Add to BullMQ
    const job = await videoQueue.add('process-video', { url, videoId });

    // 2. Store initial metadata in Redis hashes
    await redis.hset(`job:${job.id}:meta`, {
      videoId,
      thumbnail,
      status: 'waiting',
      createdAt: Date.now(),
    });

    // Handle tracking jobs set
    await redis.sadd('all-jobs', job.id);

    res.json({
      jobId: job.id,
      videoId,
      thumbnail,
      status: 'waiting',
    });
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ error: 'Failed to queue job' });
  }
});

// GET /api/status/:jobId
app.get('/api/status/:jobId', async (req, res) => {
  const { jobId } = req.params;
  const job = await videoQueue.getJob(jobId);
  const meta = await redis.hgetall(`job:${jobId}:meta`);

  if (!meta || Object.keys(meta).length === 0) {
    return res.status(404).json({ error: 'Job not found' });
  }

  // BullMQ status + our custom metadata
  const state = job ? await job.getState() : meta.status;

  res.json({
    jobId,
    status: state,
    progress: job ? job.progress : null,
    ...meta,
  });
});

// GET /api/result/:jobId
app.get('/api/result/:jobId', async (req, res) => {
  const { jobId } = req.params;
  const result = await redis.get(`job:${jobId}:result`);

  if (!result) {
    return res.status(404).json({ error: 'Result not found or job still processing' });
  }

  res.json(JSON.parse(result));
});

// GET /api/all-jobs
app.get('/api/all-jobs', async (req, res) => {
  try {
    const jobIds = await redis.smembers('all-jobs');
    const jobs = await Promise.all(
      jobIds.map(async (id) => {
        const meta = await redis.hgetall(`job:${id}:meta`);
        return { jobId: id, ...meta };
      })
    );
    jobs.sort((a, b) => b.createdAt - a.createdAt);
    res.json(jobs);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch jobs' });
  }
});

// DELETE /api/job/:jobId
app.delete('/api/job/:jobId', async (req, res) => {
  const { jobId } = req.params;
  console.log(`[Gateway] 🗑️ Deletion requested for job: ${jobId}`);

  try {
    // 1. Remove from all-jobs set
    await redis.srem('all-jobs', jobId);

    // 2. Delete metadata and results
    await redis.del(`job:${jobId}:meta`);
    await redis.del(`job:${jobId}:result`);

    // 3. Attempt to remove from BullMQ (optional)
    try {
      const job = await videoQueue.getJob(jobId);
      if (job) {
        await job.remove();
      }
    } catch (bullError) {
      console.warn(`[Gateway] ⚠️ Could not remove job ${jobId} from BullMQ queue:`, bullError.message);
    }

    res.json({ success: true, message: `Job ${jobId} purged from ledger` });
  } catch (error) {
    console.error('Delete Error:', error);
    res.status(500).json({ error: 'Failed to purge job: ' + error.message });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Gateway API running on http://localhost:${PORT}`);
});
