#!/usr/bin/env bash
# Deploy PDF-to-XLSX to QNAP NAS (192.168.0.213).
# Run from project root: ./deploy.sh
# Optional: NAS_USER=admin NAS_HOST=192.168.0.213 ./deploy.sh

set -e
NAS_HOST="${NAS_HOST:-192.168.0.213}"
NAS_USER="${NAS_USER:-admin}"
REMOTE_DIR="${REMOTE_DIR:-~/pdf2xlsx}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Deploying to ${NAS_USER}@${NAS_HOST}:${REMOTE_DIR}"

# Copy project (rsync if available, else scp)
if command -v rsync &>/dev/null; then
  rsync -avz --delete \
    --exclude='.git' --exclude='__pycache__' --exclude='venv' --exclude='.venv' \
    --exclude='media' --exclude='*.pyc' --exclude='*.sqlite3' \
    --exclude='.cursor' --exclude='mcps' --exclude='agent-transcripts' \
    "$PROJECT_ROOT/" "${NAS_USER}@${NAS_HOST}:${REMOTE_DIR}/"
else
  ssh -o StrictHostKeyChecking=accept-new "${NAS_USER}@${NAS_HOST}" "mkdir -p $REMOTE_DIR"
  (cd "$PROJECT_ROOT" && tar cf - --exclude=.git --exclude=__pycache__ --exclude=venv --exclude=.venv --exclude=media --exclude='*.sqlite3' .) \
    | ssh -o StrictHostKeyChecking=accept-new "${NAS_USER}@${NAS_HOST}" "cd $REMOTE_DIR && tar xf -"
fi

# Build and start on NAS
ssh -o StrictHostKeyChecking=accept-new "${NAS_USER}@${NAS_HOST}" \
  "cd $REMOTE_DIR && docker compose up -d --build"

echo "Done. App: http://${NAS_HOST}:8000/"
