#!/bin/bash
# Quick deploy script for Sports Betting AI

echo "🏆 Sports Betting AI - Deployment Helper"
echo ""
echo "Step 1: Make sure code is pushed to GitHub"
cd /Users/djryan/git/guiltyfalcon/ai-portfolio
git status
echo ""

echo "Step 2: Open browser to Streamlit Cloud"
echo "Go to: https://share.streamlit.io"
echo ""

echo "Step 3: Connect GitHub and select repo"
echo "- Repo: guiltyfalcon/ai-portfolio"
echo "- Branch: main"
echo "- Main file: sports-betting-ai/Home.py"
echo ""

echo "Step 4: Add secrets (Settings → Secrets)"
echo "THEODDS_API_KEY = 8fcaab13355be4098fc79f7dbce9821b"
echo ""

echo "Step 5: Deploy!"
echo "Your site will be: https://sports-betting-ai-demo.streamlit.app"
echo ""

open https://share.streamlit.io 2>/dev/null || echo "Open browser manually"
