#!/usr/bin/env bash

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

backend_url="${BACKEND_URL:-http://localhost:8002/api/v1/health}"
frontend_url="${FRONTEND_URL:-http://localhost:3002}"

check_url() {
  local label="$1"
  local url="$2"
  local code

  echo -n "$label: "
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || true)
  if [ "$code" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC}"
  else
    echo -e "${RED}✗ FAILED (HTTP $code)${NC}"
  fi
}

check_url "Backend API" "$backend_url"
check_url "Frontend" "$frontend_url"
