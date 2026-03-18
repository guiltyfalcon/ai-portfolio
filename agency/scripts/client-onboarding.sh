#!/bin/bash
# Client Onboarding Script for GuiltyFalcon Agency
# Usage: ./client-onboarding.sh "Client Name" "client@email.com" "package"

set -e

AGENCY_DIR="$HOME/git/guiltyfalcon/ai-portfolio/agency"
CLIENTS_DIR="$AGENCY_DIR/clients"

# Get arguments
CLIENT_NAME="${1:-}"
CLIENT_EMAIL="${2:-}"
PACKAGE="${3:-professional}"

if [ -z "$CLIENT_NAME" ] || [ -z "$CLIENT_EMAIL" ]; then
    echo "Usage: $0 \"Client Name\" \"client@email.com\" [package]"
    echo "Packages: starter, professional (default), enterprise"
    exit 1
fi

# Create safe directory name
SAFE_NAME=$(echo "$CLIENT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
CLIENT_DIR="$CLIENTS_DIR/$SAFE_NAME-$(date +%Y%m%d)"

mkdir -p "$CLIENT_DIR"

echo "=== GuiltyFalcon Agency - Client Onboarding ==="
echo "Client: $CLIENT_NAME"
echo "Email: $CLIENT_EMAIL"
echo "Package: $PACKAGE"
echo "Directory: $CLIENT_DIR"
echo ""

# Create client brief template
cat > "$CLIENT_DIR/brief.md" << EOF
# Client Brief: $CLIENT_NAME

**Date:** $(date +%Y-%m-%d)  
**Package:** $PACKAGE  
**Email:** $CLIENT_EMAIL  
**Status:** Discovery

## Business Information

**Business Name:** 
**Industry:** 
**Target Audience:** 
**Current Website (if any):** 

## Project Goals

- [ ] Increase signups
- [ ] Drive sales
- [ ] Build email list
- [ ] Showcase product
- [ ] Other: 

## Design Preferences

**Style:** [ ] Modern [ ] Minimal [ ] Bold [ ] Professional [ ] Playful  
**Color preferences:** 
**Reference sites:** 

## Must-Have Features

- [ ] Contact form
- [ ] Pricing table
- [ ] Testimonials
- [ ] FAQ section
- [ ] Newsletter signup
- [ ] Live chat
- [ ] Other: 

## Content

**Logo:** [ ] Provided [ ] Need to create  
**Images:** [ ] Provided [ ] Stock photos OK [ ] Need photography  
**Copy:** [ ] Client will provide [ ] Need copywriting help

## Timeline

**Start Date:** $(date +%Y-%m-%d)  
**Target Launch:** 

## Payment

**Total:** $(case $PACKAGE in
    starter) echo '$500' ;;
    professional) echo '$1,000' ;;
    enterprise) echo '$2,000' ;;
    *) echo 'TBD' ;;
esac)
**Deposit Paid:** [ ] Yes [ ] No  
**Final Payment:** [ ] Paid [ ] Pending

## Notes

EOF

echo "✅ Created client brief: $CLIENT_DIR/brief.md"

# Create project checklist
cat > "$CLIENT_DIR/checklist.md" << EOF
# Project Checklist: $CLIENT_NAME

## Pre-Project
- [ ] Receive deposit (50%)
- [ ] Client completes brief
- [ ] Gather brand assets (logo, colors, images)
- [ ] Confirm package and timeline

## Design Phase
- [ ] Create wireframe/mockup
- [ ] Client approves design direction
- [ ] Build landing page
- [ ] Internal review

## Revision Phase
- [ ] Deploy to staging
- [ ] Client review
- [ ] Revision round 1
- [ ] Revision round 2 (if needed)
- [ ] Final approval

## Launch Phase
- [ ] Receive final payment (50%)
- [ ] Deploy to production
- [ ] Set up analytics
- [ ] Hand over source files
- [ ] Client training (if needed)

## Post-Launch (Enterprise only)
- [ ] 30-day support period
- [ ] Performance check-in
- [ ] Request testimonial
- [ ] Ask for referrals

EOF

echo "✅ Created checklist: $CLIENT_DIR/checklist.md"

# Create assets directory
mkdir -p "$CLIENT_DIR/assets"
mkdir -p "$CLIENT_DIR/designs"
mkdir -p "$CLIENT_DIR/exports"

echo "✅ Created project directories"
echo ""
echo "Next steps:"
echo "1. Send client the brief questionnaire"
echo "2. Request 50% deposit to start"
echo "3. Begin design phase once brief is complete"
