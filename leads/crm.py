#!/usr/bin/env python3
"""
Lead Tracker CRM - Simple CLI for managing inbound leads
"""

import json
import sys
from datetime import datetime
from pathlib import Path

CRM_FILE = Path(__file__).parent / 'leads_crm.json'

def load_crm():
    """Load CRM data."""
    if not CRM_FILE.exists():
        return {'leads': [], 'stats': {'total': 0, 'contacted': 0, 'converted': 0}}
    
    with open(CRM_FILE, 'r') as f:
        return json.load(f)

def save_crm(data):
    """Save CRM data."""
    with open(CRM_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_lead(name, source, contact, notes='', priority='warm'):
    """Add a new lead."""
    crm = load_crm()
    
    lead = {
        'id': len(crm['leads']) + 1,
        'name': name,
        'source': source,  # reddit, twitter, threads, referral, etc.
        'contact': contact,  # @username, email, etc.
        'notes': notes,
        'priority': priority,  # hot, warm, cold
        'status': 'new',  # new, contacted, qualified, converted, lost
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    crm['leads'].append(lead)
    crm['stats']['total'] += 1
    save_crm(crm)
    
    print(f"✅ Lead added: {name} ({source}) - ID: {lead['id']}")
    return lead

def list_leads(status=None, priority=None):
    """List leads with optional filters."""
    crm = load_crm()
    leads = crm['leads']
    
    if status:
        leads = [l for l in leads if l['status'] == status]
    if priority:
        leads = [l for l in leads if l['priority'] == priority]
    
    # Sort by priority (hot > warm > cold) then by date
    priority_order = {'hot': 0, 'warm': 1, 'cold': 2}
    leads.sort(key=lambda x: (priority_order.get(x['priority'], 3), x['created_at']), reverse=True)
    
    print(f"\n📊 Leads ({len(leads)} total)")
    print("=" * 60)
    
    for lead in leads[-10:]:  # Last 10
        emoji = {'hot': '🔥', 'warm': '🌡️', 'cold': '🧊'}.get(lead['priority'], '❓')
        status_icon = {'new': '🆕', 'contacted': '📧', 'qualified': '✅', 'converted': '💰', 'lost': '❌'}.get(lead['status'], '❓')
        
        print(f"{emoji} {status_icon} #{lead['id']}: {lead['name']}")
        print(f"   Source: {lead['source']} | Contact: {lead['contact']}")
        print(f"   Notes: {lead['notes'][:50]}..." if len(lead['notes']) > 50 else f"   Notes: {lead['notes']}")
        print(f"   Created: {lead['created_at'][:10]}")
        print()
    
    # Stats
    print("=" * 60)
    print(f"📈 Stats: {crm['stats']['total']} total | {crm['stats']['contacted']} contacted | {crm['stats']['converted']} converted")

def update_status(lead_id, status):
    """Update lead status."""
    crm = load_crm()
    
    for lead in crm['leads']:
        if lead['id'] == lead_id:
            lead['status'] = status
            lead['updated_at'] = datetime.now().isoformat()
            save_crm(crm)
            print(f"✅ Lead #{lead_id} status updated to: {status}")
            return
    
    print(f"❌ Lead #{lead_id} not found")

def search(query):
    """Search leads by name, notes, or source."""
    crm = load_crm()
    query = query.lower()
    
    matches = [
        l for l in crm['leads']
        if query in l['name'].lower() or query in l['notes'].lower() or query in l['source'].lower()
    ]
    
    print(f"\n🔍 Search results for '{query}' ({len(matches)} found)")
    for lead in matches:
        print(f"  #{lead['id']}: {lead['name']} ({lead['source']})")

def main():
    if len(sys.argv) < 2:
        print("Usage: python crm.py <command> [args]")
        print("Commands:")
        print("  add <name> <source> <contact> [notes] [priority]")
        print("  list [status] [priority]")
        print("  update <id> <status>")
        print("  search <query>")
        return
    
    command = sys.argv[1]
    
    if command == 'add' and len(sys.argv) >= 5:
        name = sys.argv[2]
        source = sys.argv[3]
        contact = sys.argv[4]
        notes = sys.argv[5] if len(sys.argv) > 5 else ''
        priority = sys.argv[6] if len(sys.argv) > 6 else 'warm'
        add_lead(name, source, contact, notes, priority)
    
    elif command == 'list':
        status = sys.argv[2] if len(sys.argv) > 2 else None
        priority = sys.argv[3] if len(sys.argv) > 3 else None
        list_leads(status, priority)
    
    elif command == 'update' and len(sys.argv) >= 4:
        lead_id = int(sys.argv[2])
        status = sys.argv[3]
        update_status(lead_id, status)
    
    elif command == 'search' and len(sys.argv) >= 3:
        query = ' '.join(sys.argv[2:])
        search(query)
    
    else:
        print(f"❌ Unknown command or missing args: {command}")

if __name__ == '__main__':
    main()
