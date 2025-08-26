const config = {
  api: {
    baseURL: '/api',
    timeout: 5000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    withCredentials: true
  },
  cors: {
    allowedOrigins: ['http://localhost:8000', 'http://127.0.0.1:8000', 'http://localhost:8081', 'http://127.0.0.1:8081'],
    allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'Accept']
  }
}

module.exports = config 