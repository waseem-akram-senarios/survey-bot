# 🚀 Deployment Guide - Survey Bot

## Step 1: Code Pushed to Git ✅
Your latest code has been successfully pushed to GitHub:
- Commit: `787cf5e` - "Fix API health endpoint and improve dashboard UI - all issues resolved"
- Repository: `https://github.com/waseem-akram-senarios/survey-bot.git`

## Step 2: Deploy to Live Server

### Option A: SSH Deployment (Recommended)
```bash
# Connect to your server
ssh root@54.86.65.150

# Navigate to project directory
cd /root

# Clone or pull latest code
if [ ! -d "survey-bot" ]; then
    git clone https://github.com/waseem-akram-senarios/survey-bot.git
else
    cd survey-bot
    git pull origin main
fi

# Run deployment script
cd survey-bot
chmod +x deploy_to_server.sh
./deploy_to_server.sh
```

### Option B: Manual Deployment
```bash
# On server (54.86.65.150)
cd /root/survey-bot
git pull origin main
cd survai-platform
docker compose -f docker-compose.microservices.yml down
docker compose -f docker-compose.microservices.yml up -d --build
```

## Step 3: Verify Deployment

After deployment, test these URLs:

### Health Endpoints
```bash
# Should return: {"status": "OK", "service": "api-gateway", "message": "All services healthy"}
curl http://54.86.65.150:8080/pg/api/health

# Should return: {"status": "OK", "service": "gateway"}
curl http://54.86.65.150:8080/health
```

### API Tests
```bash
# Translation test
curl -X POST -H "Content-Type: application/json" \
     -d '{"text":"Hello world","language":"es"}' \
     http://54.86.65.150:8080/pg/api/brain/translate

# Should return: {"translated":"Hola mundo"}

# Surveys test
curl http://54.86.65.150:8080/pg/api/surveys/list

# Should return array of surveys
```

### UI Tests
- Dashboard: http://54.86.65.150:8080
- Recipient: http://54.86.65.150:3000

## Step 4: Expected Results After Deployment

### ✅ What Should Work
- **Health Endpoint**: `/pg/api/health` should return 200 (was 404 before)
- **Dashboard UI**: Should load with "IT Curves" title
- **Translation API**: "Hello world" → "Hola mundo"
- **Survey System**: All 51 surveys accessible
- **Bilingual Support**: English↔Spanish translation
- **All APIs**: Should respond correctly

### 🔍 Verification Checklist
- [ ] Health endpoint returns 200
- [ ] Dashboard loads without errors
- [ ] Translation API works
- [ ] Survey URLs are accessible
- [ ] All containers are running
- [ ] No error logs in containers

## Troubleshooting

### If Health Endpoint Still Returns 404
```bash
# Check nginx config
docker exec gateway cat /etc/nginx/conf.d/default.conf | grep -A 3 "pg/api/health"

# Restart gateway
docker restart gateway
```

### If Services Don't Start
```bash
# Check logs
docker compose -f docker-compose.microservices.yml logs

# Rebuild specific service
docker compose -f docker-compose.microservices.yml up -d --build gateway
```

### If Dashboard Doesn't Load
```bash
# Check dashboard container
docker logs dashboard

# Restart dashboard
docker restart dashboard
```

## 🎯 Success Indicators

Your deployment is successful when:
1. ✅ `curl http://54.86.65.150:8080/pg/api/health` returns 200
2. ✅ Dashboard loads at http://54.86.65.150:8080
3. ✅ Translation API works: "Hello" → "Hola"
4. ✅ All 14 containers are running
5. ✅ No error logs in containers

## 🚀 Final Verification

Run this complete test after deployment:
```bash
# Test all critical endpoints
curl http://54.86.65.150:8080/pg/api/health
curl http://54.86.65.150:8080/pg/api/surveys/list
curl -X POST -H "Content-Type: application/json" -d '{"text":"test","language":"es"}' http://54.86.65.150:8080/pg/api/brain/translate

# Check container status
docker compose -f docker-compose.microservices.yml ps
```

When all tests pass, your latest code is successfully deployed! 🎉
