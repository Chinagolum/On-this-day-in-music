#!/bin/bash
# Run a database health audit
# Usage: ./scripts/audit_db.sh
set -e

echo "🔍 Running database audit..."
python3 -c "
from lib.pitchfork_scraper import PitchforkScraper
scraper = PitchforkScraper()
try:
    scraper.audit_database()
finally:
    scraper.close()
"
