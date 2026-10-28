"""Tulsipur portal sections. Sheet IDs and coordinator identities will be added later."""

NAV_SECTIONS = [
    ("⌂", "Home"),
    ("▦", "Reports"),
    ("▤", "Daily Summary"),
    ("♙", "Team"),
]

# Six core ground-operations reporting categories.
# Tulsipur does not include the Manjhanpur-only Solar Light Verification section.
REPORT_SECTIONS = [
    ("daily", "📋", "Daily Field Reports", "Daily observations and activity updates"),
    ("registration", "👥", "Worker Registration", "New worker and volunteer registrations"),
    ("whatsapp", "💬", "WhatsApp Outreach", "New member and group-building reports"),
    ("actions", "📝", "Issues & Action Taken", "Local issues, requests and follow-up actions"),
    ("booth", "🗳️", "Booth Visits", "Booth-level visits and coverage tracking"),
    ("social", "📱", "Social Media Reporting", "Digital activities and field amplification"),
]

# No connectors configured in Version 1 (deliberate).
SHEET_CONNECTIONS = {}
COORDINATORS = []
