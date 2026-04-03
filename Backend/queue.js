const { Queue, QueueEvents } = require('bullmq');
require('dotenv').config();

const connection = {
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
};

const videoQueue = new Queue('video-processing', { connection });
const queueEvents = new QueueEvents('video-processing', { connection });

module.exports = { videoQueue, queueEvents };
