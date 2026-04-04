import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.repositories.worker_repository import WorkerRepository
from services.repositories.policy_repository import PolicyRepository
from services.repositories.claim_repository import ClaimRepository
from services.repositories.payout_repository import PayoutRepository
from services.repositories.zone_repository import ZoneRepository

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def export_seed_data():
    print("🚀 Starting Seed Data Export from Local MongoDB...")
    
    data = {
        "workers": WorkerRepository().find_all(),
        "policies": PolicyRepository().find_all(),
        "claims": ClaimRepository().find_all(),
        "payouts": PayoutRepository().find_all(),
        "zones": ZoneRepository().find_all()
    }
    
    # Remove MongoDB _id fields
    for collection in data:
        for doc in data[collection]:
            if "_id" in doc:
                del doc["_id"]
                
    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "seed_data.json")
    
    with open(output_path, "w") as f:
        json.dump(data, f, default=json_serial, indent=4)
        
    print(f"✅ Export completed! File saved at: {output_path}")
    print(f"📊 Stats: {len(data['workers'])} workers, {len(data['claims'])} claims exported.")

if __name__ == "__main__":
    export_seed_data()
