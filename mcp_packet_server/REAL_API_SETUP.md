# 🚀 Real API Integration Setup Guide

## 🎯 **Overview**

Your MCP Packet Server is now ready for real API integrations! This guide will walk you through setting up real credentials for all services.

## ✅ **What's Already Working**

- ✅ **All service handlers** are implemented and tested
- ✅ **Mock fallback mode** works for development
- ✅ **Environment variable configuration** is set up
- ✅ **Google API libraries** are installed
- ✅ **Todoist API library** is installed
- ✅ **DeepPCB API** is already configured and working

## 🔑 **Required Credentials**

### **1. Todoist API Token**
- **Get it from**: https://app.todoist.com/app/settings/integrations/developer
- **Add to `.env`**: `TODOIST_API_TOKEN=your_actual_token_here`

### **2. Google Services (Calendar & Gmail)**
- **Get credentials from**: https://console.developers.google.com/
- **Required files**:
  - `client_secret_*.json` (OAuth2 client credentials)
  - `token.json` (will be auto-generated on first auth)

### **3. DeepPCB API**
- **Already configured** in your `.env` file
- **Status**: ✅ Working with real API

## 🚀 **Quick Setup Steps**

### **Step 1: Get Todoist API Token**
1. Go to https://app.todoist.com/app/settings/integrations/developer
2. Copy your API token
3. Update `.env` file:
   ```bash
   TODOIST_API_TOKEN=your_actual_token_here
   ```

### **Step 2: Get Google API Credentials**
1. Go to https://console.developers.google.com/
2. Create a new project or select existing one
3. Enable Google Calendar API and Gmail API
4. Create OAuth2 credentials (Desktop application)
5. Download `client_secret_*.json` file
6. Place it in the appropriate service directory

### **Step 3: Update Environment Variables**
Your `.env` file should look like this:
```bash
# DeepPCB (already working)
DEEPPCB_API_KEY=ykNTkhwhPUzVJ3EpPRS281Nis/34g8yXd8I3Yh66/yM=
DEEPPCB_API_URL=https://api.deeppcb.com/v1

# Todoist (add your real token)
TODOIST_API_TOKEN=your_actual_todoist_token_here

# Google Services (update paths to match your setup)
GOOGLE_CALENDAR_TOKEN_PATH=../google_calendar/token.json
GOOGLE_CALENDAR_CREDENTIALS_PATH=../google_calendar/client_secret_*.json
GMAIL_TOKEN_PATH=../gmail/token.json
GMAIL_CREDENTIALS_PATH=../gmail/client_secret.json
```

## 🔧 **Service-Specific Setup**

### **Todoist Service**
- **Easiest to set up** - just needs API token
- **No OAuth flow** - simple token-based auth
- **Test with**: Create a simple task

### **Google Calendar Service**
- **Requires OAuth2 setup**
- **First run**: Will open browser for authentication
- **Scopes**: Calendar read/write access
- **Test with**: List your calendars

### **Gmail Service**
- **Requires OAuth2 setup**
- **First run**: Will open browser for authentication
- **Scopes**: Gmail read/write access
- **Test with**: List your email labels

### **DeepPCB Service**
- **Already working** with real API
- **No additional setup needed**
- **Test with**: Any PCB design operation

## 🧪 **Testing Real API Integration**

### **Test 1: Verify Service Status**
```bash
cd mcp_packet_server
python3 -c "
from enhanced_server import EnhancedMCPServer
import asyncio

server = EnhancedMCPServer()
result = asyncio.run(server._list_services({}))
print(f'✅ Services: {result[\"total_services\"]}')
print(f'✅ Available: {list(result[\"services\"].keys())}')
"
```

### **Test 2: Test Todoist (if token is set)**
```bash
python3 -c "
from services.todoist_handler import TodoistServiceHandler
import asyncio

handler = TodoistServiceHandler()
if handler.api_token:
    print('✅ Todoist API token configured')
    # Test will happen automatically
else:
    print('⚠️  Todoist API token not set - using mock mode')
"
```

### **Test 3: Test Google Services**
```bash
python3 -c "
from services.google_calendar_handler import GoogleCalendarServiceHandler
from services.gmail_handler import GmailServiceHandler

gcal = GoogleCalendarServiceHandler()
gmail = GmailServiceHandler()

print(f'✅ Google Calendar: {\"Real API\" if gcal.service else \"Mock mode\"}')
print(f'✅ Gmail: {\"Real API\" if gmail.service else \"Mock mode\"}')
"
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. "Google API libraries not available"**
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### **2. "Credentials file not found"**
- Check file paths in `.env`
- Ensure credential files exist in specified locations
- Verify file permissions

#### **3. "API token not set"**
- Add `TODOIST_API_TOKEN=your_token` to `.env`
- Restart the server after updating `.env`

#### **4. OAuth2 Authentication Fails**
- Check internet connection
- Verify OAuth2 credentials are correct
- Ensure required APIs are enabled in Google Console

### **Debug Mode**
Enable verbose logging by setting environment variable:
```bash
export MCP_DEBUG=1
python3 -m mcp_packet_server.mcp_server
```

## 🎉 **Success Indicators**

### **When Everything is Working:**
- ✅ **No warning messages** about missing credentials
- ✅ **Real API calls** instead of mock responses
- ✅ **Authentication flows** work smoothly
- ✅ **All 137 operations** work with real data

### **Example Success Output:**
```
🚀 Enhanced MCP Server initialized with LFU policy
📊 Tool limit: 80
🔧 Available services: 4
🚨 Tripwire validation system: ACTIVE
✅ All services using real APIs
```

## 🔮 **Next Steps After Setup**

1. **Test all services** with real API calls
2. **Monitor API usage** and rate limits
3. **Set up monitoring** for production use
4. **Configure backup credentials** if needed
5. **Document your setup** for team members

## 📞 **Need Help?**

- **Check logs**: Look for specific error messages
- **Verify credentials**: Ensure all tokens and files are correct
- **Test individually**: Test each service separately
- **Check permissions**: Ensure credential files are readable

---

**🎯 Your MCP Packet Server is now ready for production use with real APIs!**

*Last updated: January 15, 2024*
