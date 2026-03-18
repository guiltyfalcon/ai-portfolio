#!/bin/bash
# Lead Monitor Script for GuiltyFalcon Agency
# Runs daily to find new landing page leads

set -e

AGENCY_DIR="$HOME/git/guiltyfalcon/ai-portfolio/agency"
LEADS_FILE="$AGENCY_DIR/leads.json"
LOG_FILE="$AGENCY_DIR/logs/lead-monitor-$(date +%Y-%m-%d).log"

# Create logs directory if needed
mkdir -p "$AGENCY_DIR/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting lead monitoring..."

# Check if lead-hunter skill is available
if [ -d "$HOME/.openclaw/skills/lead-hunter" ]; then
    log "Lead Hunter skill found"
    
    # TODO: Implement actual lead-hunter CLI calls when available
    # For now, log that we would search these platforms
    
    log "Searching Twitter/X for: 'need a landing page', 'landing page designer', 'website help'"
    log "Searching Reddit r/forhire and r/needahire for hiring posts"
    log "Searching IndieHackers for feedback requests"
    
    # Placeholder: In production, this would call lead-hunter discover
    # lead-hunter discover --config "$AGENCY_DIR/discovery/landing-page-leads.yaml"
    
else
    log "WARNING: Lead Hunter skill not found at ~/.openclaw/skills/lead-hunter"
fi

# Manual search reminders
log "=== Daily Lead Search Tasks ==="
log "1. Twitter/X Search: 'need a landing page' (last 24h)"
log "2. Reddit r/forhire: [Hiring] posts"
log "3. Reddit r/needahire: New posts"
log "4. IndieHackers: 'landing page feedback'"
log "5. Product Hunt: New launches without landing pages"

log "Lead monitoring complete. Check $LEADS_FILE for results."
