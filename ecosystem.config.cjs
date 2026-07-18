module.exports = {
  apps: [
    {
      name: 'astro-engine',
      cwd: '/opt/astro',
      script: '/usr/bin/bash',
      args: '-c /opt/astro/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000',
      interpreter: 'none',
      autorestart: true,
      max_restarts: 50,
      env: {
        PYTHONUNBUFFERED: '1',
        ATRO_ROOT: '/opt/astro',
        // Set real keys: ATRO_API_KEYS=secret:professional,other:premium
        // Dev keys only when explicitly enabled:
        ATRO_ALLOW_DEV_KEYS: '1',
        ATRO_CORS_ORIGINS: 'http://127.0.0.1:8000,http://localhost:8000',
      },
    },
  ],
};
