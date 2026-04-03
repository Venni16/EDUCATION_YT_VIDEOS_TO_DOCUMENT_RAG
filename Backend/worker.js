const { Worker } = require('bullmq');
const axios = require('axios');
const redis = require('./redis');
require('dotenv').config();

const connection = {
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
};

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

const worker = new Worker('video-processing', async (job) => {
  const { url, videoId } = job.data;
  console.log(`[Worker] 🎬 Processing job ${job.id} for Video ID: ${videoId}`);

  try {
    // 1. Update status in job metadata
    await redis.hset(`job:${job.id}:meta`, 'status', 'active');

    // 2. Call FastAPI AI Service
    // Note: The generate-doc endpoint returns the full document and other metadata
    const response = await axios.post(`${FASTAPI_URL}/generate-doc`, { url }); // 10 min timeout

    const result = response.data;

    // 3. Store result in Redis
    await redis.set(`job:${job.id}:result`, JSON.stringify(result));
    
    // 4. Update metadata status
    await redis.hset(`job:${job.id}:meta`, {
      status: 'completed',
      title: result.title,
      finishedAt: Date.now(),
    });

    console.log(`[Worker] ✅ Completed job ${job.id}`);
    return result;

  } catch (error) {
    console.error(`[Worker] ❌ Failed job ${job.id}:`, error.message);
    
    // Update metadata on failure
    await redis.hset(`job:${job.id}:meta`, {
      status: 'failed',
      error: error.message,
      finishedAt: Date.now(),
    });

    throw error; // Let BullMQ handle retries
  }
}, { connection });

worker.on('failed', (job, err) => {
  console.error(`[Worker] Job ${job?.id} failed with ${err.message}`);
});

console.log('👷 Video processing worker is running...');

module.exports = worker;
