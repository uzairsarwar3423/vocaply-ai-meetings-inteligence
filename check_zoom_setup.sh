#!/bin/bash

# Zoom OAuth Integration Health Check
# Run this script to verify your Zoom OAuth setup is complete

echo "================================"
echo "Zoom OAuth Integration Check"
echo "================================"
echo ""

# Check backend environment variables
echo "1. Checking Backend Configuration..."
echo "   ZOOM_CLIENT_ID: ${ZOOM_CLIENT_ID:-(not set)}"
echo "   ZOOM_CLIENT_SECRET: ${ZOOM_CLIENT_SECRET:+(set)-(not set)}"
echo "   ZOOM_REDIRECT_URI: ${ZOOM_REDIRECT_URI:-(not set)}"
echo ""

# Check frontend environment variables
echo "2. Checking Frontend Configuration (.env.local)..."
if [ -f "frontend/.env.local" ]; then
    echo "   ✓ .env.local exists"
    grep "NEXT_PUBLIC_ZOOM" frontend/.env.local | sed 's/=.*/=...[redacted]/' || echo "   ✗ No ZOOM variables found"
else
    echo "   ✗ .env.local not found"
fi
echo ""

# Check if required backend files exist
echo "3. Checking Backend Files..."
if [ -f "backend/app/services/zoom_oauth.py" ]; then
    echo "   ✓ zoom_oauth.py exists"
else
    echo "   ✗ zoom_oauth.py missing"
fi

if grep -q "ZOOM_CLIENT_ID" backend/app/core/config.py; then
    echo "   ✓ Config has Zoom settings"
else
    echo "   ✗ Config missing Zoom settings"
fi

if grep -q "zoom/callback" backend/app/api/v1/auth.py; then
    echo "   ✓ Auth endpoint configured"
else
    echo "   ✗ Auth endpoint not found"
fi
echo ""

# Check if required frontend files exist
echo "4. Checking Frontend Files..."
if [ -f "frontend/hooks/useZoomAuth.ts" ]; then
    echo "   ✓ useZoomAuth.ts exists"
else
    echo "   ✗ useZoomAuth.ts missing"
fi

if [ -f "frontend/app/(auth)/zoom-callback/page.tsx" ]; then
    echo "   ✓ Callback page exists"
else
    echo "   ✗ Callback page missing"
fi

if grep -q "ZoomOAuthTokens" frontend/types/auth.ts; then
    echo "   ✓ Auth types updated"
else
    echo "   ✗ Auth types not updated"
fi
echo ""

# Test backend API
echo "5. Testing Backend API..."
if command -v curl &> /dev/null; then
    # Check if backend is running
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        echo "   ✓ Backend is running"
        
        # Test the zoom callback endpoint exists
        response=$(curl -s -X POST http://localhost:8000/api/v1/auth/zoom/callback \
            -H "Content-Type: application/json" \
            -d '{"code":"test"}' \
            -w "\n%{http_code}")
        
        http_code=$(echo "$response" | tail -n 1)
        if [ "$http_code" -eq 400 ] || [ "$http_code" -eq 200 ]; then
            echo "   ✓ OAuth endpoint is responding"
        else
            echo "   ✗ OAuth endpoint returned HTTP $http_code"
        fi
    else
        echo "   ✗ Backend is not running on http://localhost:8000"
        echo "      Start backend with: make run-backend"
    fi
else
    echo "   ⚠ curl not found, skipping API test"
fi
echo ""

# Summary
echo "================================"
echo "Setup Checklist"
echo "================================"
echo ""
echo "Required Steps:"
echo "  [ ] Get Zoom OAuth credentials from https://marketplace.zoom.us"
echo "  [ ] Set ZOOM_CLIENT_ID in backend/.env"
echo "  [ ] Set ZOOM_CLIENT_SECRET in backend/.env"
echo "  [ ] Set ZOOM_REDIRECT_URI in backend/.env"
echo "  [ ] Set NEXT_PUBLIC_ZOOM_CLIENT_ID in frontend/.env.local"
echo "  [ ] Set NEXT_PUBLIC_ZOOM_REDIRECT_URI in frontend/.env.local"
echo "  [ ] Add redirect URI to Zoom app: https://marketplace.zoom.us"
echo ""
echo "Optional:"
echo "  [ ] Test with: curl -X POST http://localhost:8000/api/v1/auth/zoom/callback -H 'Content-Type: application/json' -d '{\"code\": \"your-code\"}'"
echo "  [ ] Check backend logs for errors"
echo "  [ ] Verify frontend can access environment variables"
echo ""
echo "Quick Start:"
echo "  1. npm run dev (frontend)"
echo "  2. python -m uvicorn app.main:app --reload (backend)"
echo "  3. Navigate to http://localhost:3000/login"
echo "  4. Click 'Sign in with Zoom'"
echo ""
