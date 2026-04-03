const Redis = require('ioredis');
require('dotenv').config();

const redisConfig = {
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  maxRetriesPerRequest: null, // Critical for BullMQ
};

const redis = new Redis(redisConfig);

redis.on('connect', () => console.log('✅ Connected to Redis'));
redis.on('error', (err) => console.error('❌ Redis Connection Error:', err));

module.exports = redis;
