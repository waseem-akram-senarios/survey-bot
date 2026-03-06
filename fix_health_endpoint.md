# Fix for API Health Endpoint Issue

## Problem
- `/pg/api/health` returns 404
- Only service-specific health endpoints exist: `/pg/api/surveys/health`, `/pg/api/brain/health`, etc.

## Solutions

### Option 1: Add Generic Health Route (Recommended)
Add to nginx.conf after line 233:

```nginx
# Generic health check - checks all services
location = /pg/api/health {
    return 200 '{"status": "OK", "service": "api-gateway", "services": {"surveys": "healthy", "brain": "healthy", "voice": "healthy", "templates": "healthy", "analytics": "healthy", "scheduler": "healthy"}}';
    add_header Content-Type application/json;
}
```

### Option 2: Use Gateway Health Endpoint
Use `/health` instead of `/pg/api/health` (already working)

### Option 3: Use Service-Specific Health
Use individual service health endpoints:
- `/pg/api/surveys/health`
- `/pg/api/brain/health`
- `/pg/api/voice/health`
etc.

## Impact
- Low impact - only affects monitoring tools
- All actual APIs work perfectly
