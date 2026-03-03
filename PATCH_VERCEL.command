#!/bin/bash
set -euo pipefail

cd "/Users/simonemosca/Documents/Develop/worldmonitor"

python3 "./patch_vercel_json.py"

echo ""
echo "Done. Premi INVIO per chiudere."
read