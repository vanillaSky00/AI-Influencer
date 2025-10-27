#!/usr/bin/env bash
set -euo pipefail

# Trap any exit (normal or Ctrl+C) and clean up
cleanup() {
  echo ""
  echo "🧹 Cleaning up..."
  pkill -f 'socat.*TCP-LISTEN:6000' || true
  docker compose down || true
  echo "✅ All cleaned up. Bye!"
}
trap cleanup EXIT

echo "👉 Ensuring Docker Desktop is running..."
if ! docker info >/dev/null 2>&1; then
  echo "🐳 Launching Docker Desktop..."
  open -a Docker || true
  for i in {1..60}; do
    if docker info >/dev/null 2>&1; then break; fi
    printf "."
    sleep 1
  done
  echo
  docker info >/dev/null 2>&1 || { echo "❌ Docker Engine not running."; exit 1; }
fi

echo "🖥 Starting XQuartz..."
open -a XQuartz || true
defaults write org.xquartz.X11 nolisten_tcp -int 0 || true
sleep 2

echo "🔐 Allowing X connections..."
DISPLAY=:0 /opt/X11/bin/xhost +localhost || true
DISPLAY=:0 /opt/X11/bin/xhost +127.0.0.1 || true

echo "🔗 Starting socat bridge (TCP 6000 -> UNIX socket)..."
brew list socat >/dev/null 2>&1 || brew install socat
pkill -f 'socat.*TCP-LISTEN:6000' || true
socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\" >/tmp/socat-x11.log 2>&1 &
SOCAT_PID=$!

export DISPLAY=host.docker.internal:0
echo "🪟 DISPLAY=$DISPLAY"

echo "🚢 Starting Docker Compose (mac profile)..."
docker compose --profile mac up --build

# When Docker Compose stops (GUI closed or Ctrl+C), cleanup() triggers

# couldn't connect to display "host.docker.internal:0" check:
# https://github.com/orgs/orbstack/discussions/1388


# rebuild and restart only gui 
#docker compose --profile mac up --build chat-mac