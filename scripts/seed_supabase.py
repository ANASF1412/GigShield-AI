import os
import sys
from datetime import datetime, timedelta
import random

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.repositories.worker_repository import WorkerRepository
from services.repositories.policy_repository import PolicyRepository
from services.repositories.claim_repository import ClaimRepository
from services.repositories.payout_repository import PayoutRepository
from services.repositories.zone_repository import ZoneRepository
from services.repositories.audit_log_repository import AuditLogRepository

def get_db():
    return {
        'workers': WorkerRepository(),
        'policies': PolicyRepository(),
        'claims': ClaimRepository(),
        'payouts': PayoutRepository(),
        'zones': ZoneRepository(),
        'audit': AuditLogRepository()
    }

def seed_zones(db):
    print("\n--- Seeding Zones ---")
    zones_data = [
        {"city": "Chennai", "zone_id": "Chennai South", "rainfall": 0, "temperature": 32, "humidity": 70, "aqi": 85, "risk_score": 0.2, "status": "SAFE", "source": "Seed"},
        {"city": "Chennai", "zone_id": "Chennai North", "rainfall": 12, "temperature": 30, "humidity": 80, "aqi": 90, "risk_score": 0.4, "status": "WATCH", "source": "Seed"},
        {"city": "Bengaluru", "zone_id": "Koramangala", "rainfall": 0, "temperature": 28, "humidity": 65, "aqi": 110, "risk_score": 0.1, "status": "SAFE", "source": "Seed"},
        {"city": "Delhi", "zone_id": "Connaught Place", "rainfall": 0, "temperature": 40, "humidity": 45, "aqi": 350, "risk_score": 0.8, "status": "CRITICAL", "source": "Seed"},
        {"city": "Mumbai", "zone_id": "Andheri East", "rainfall": 85, "temperature": 29, "humidity": 90, "aqi": 50, "risk_score": 0.75, "status": "CRITICAL", "source": "Seed"}
    ]
    
    count = 0
    for z in zones_data:
        existing = db['zones'].find_one({"zone_id": z["zone_id"]})
        if existing:
            z["updated_at"] = datetime.now().isoformat()
            db['zones'].update(existing["_id"], z)
        else:
            z["created_at"] = datetime.now().isoformat()
            db['zones'].create(z)
            count += 1
    print(f"Upserted 5 Zones. (New: {count})")

def seed_workers(db):
    print("\n--- Seeding Workers ---")
    workers_data = [
        {"worker_id": "W001", "name": "Ramesh Kumar", "city": "Chennai", "delivery_zone": "Chennai South", "avg_hourly_income": 45.0, "kyc_status": "Verified", "rating": 4.8, "ncb_streak": 3, "ncb_discount_rate": 0.05,"total_payouts": 0.0},
        {"worker_id": "W002", "name": "Suresh Raina", "city": "Chennai", "delivery_zone": "Chennai North", "avg_hourly_income": 40.0, "kyc_status": "Verified", "rating": 4.2, "ncb_streak": 0, "ncb_discount_rate": 0.0,"total_payouts": 0.0},
        {"worker_id": "W003", "name": "Amit Sharma", "city": "Delhi", "delivery_zone": "Connaught Place", "avg_hourly_income": 50.0, "kyc_status": "Verified", "rating": 4.9, "ncb_streak": 10, "ncb_discount_rate": 0.20,"total_payouts": 0.0},
        {"worker_id": "W010", "name": "Priya Patel", "city": "Mumbai", "delivery_zone": "Andheri East", "avg_hourly_income": 55.0, "kyc_status": "Verified", "rating": 4.5, "ncb_streak": 1, "ncb_discount_rate": 0.0,"total_payouts": 0.0},
    ]
    
    # Add generic workers
    cities = ["Bengaluru", "Pune", "Hyderabad"]
    zones = ["Koramangala", "Shivaji Nagar", "Hi-Tech City"]
    for i in range(11, 25):
        wid = f"W{i:03d}"
        c_idx = i % 3
        workers_data.append({
            "worker_id": wid, 
            "name": f"Gig Worker {i}", 
            "city": cities[c_idx], 
            "delivery_zone": zones[c_idx], 
            "avg_hourly_income": round(random.uniform(35.0, 60.0), 1), 
            "kyc_status": "Verified", 
            "rating": round(random.uniform(3.5, 4.9), 1), 
            "ncb_streak": random.randint(0, 5),
            "ncb_discount_rate": 0.0,
            "total_payouts": 0.0
        })

    count = 0
    for w in workers_data:
        existing = db['workers'].find_one({"worker_id": w["worker_id"]})
        if existing:
            w["updated_at"] = datetime.now().isoformat()
            db['workers'].update(existing["_id"], w)
        else:
            w["created_at"] = datetime.now().isoformat()
            w["updated_at"] = datetime.now().isoformat()
            db['workers'].create(w)
            count += 1
    print(f"Upserted {len(workers_data)} Workers. (New: {count})")
    return workers_data

def seed_policies(db, workers):
    print("\n--- Seeding Policies ---")
    now = datetime.now()
    count = 0
    
    for w in workers:
        wid = w["worker_id"]
        existing = db['policies'].find_one({"worker_id": wid, "active_status": True})
        if existing:
            continue
            
        # Distribute states
        state_roll = random.random()
        active_status = True
        days_offset = 7
        
        if wid == "W002": # Expiring soon
            days_offset = 1
        elif wid == "W003": # Expired
            days_offset = -1
            active_status = False

        start_date = now - timedelta(days=7 - max(days_offset, 1)) if days_offset > 0 else now - timedelta(days=14)
        end_date = now + timedelta(days=days_offset)
        
        pol_id = db['policies'].generate_policy_id()
        policy = {
            "policy_id": pol_id,
            "worker_id": wid,
            "weekly_premium": 45.0 * (1.0 - w["ncb_discount_rate"]),
            "coverage_limit": 5000.0,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "active_status": active_status,
            "payment_ref": f"rzp_sub_{pol_id}",
            "payment_status": "SUCCESS",
            "premium_paid": 45.0 * (1.0 - w["ncb_discount_rate"]),
            "renewal_count": w["ncb_streak"],
            "created_at": start_date.isoformat(),
            "updated_at": start_date.isoformat()
        }
        db['policies'].create(policy)
        count += 1
    print(f"Inserted {count} new Policies.")

def seed_claims_and_payouts(db):
    print("\n--- Seeding Claims & Payouts ---")
    
    worker = db['workers'].find_one({"worker_id": "W001"})
    if not worker: return
    
    existing_claims = db['claims'].find_one({"worker_id": "W001"})
    if existing_claims:
        print("Demo claims already exist. Skipping payload seeding to avoid spam.")
        return

    # Claim 1: SUCCESS (W001)
    c1_id = db['claims'].generate_claim_id()
    c1 = {
        "claim_id": c1_id,
        "worker_id": "W001",
        "policy_id": "P_MOCK_001",
        "event_type": "HEAVY_RAIN",
        "trigger_conditions": "Rainfall exceeded 85mm",
        "estimated_loss": 480.0,
        "fraud_score": 12.0,
        "status": "PAID",
        "payout_amount": 480.0,
        "governance_status": "CLEARED",
        "governance_tags": ["AUTO_VERIFIED"],
        "is_real_data": False,
        "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
        "audit_trail": [
            {"ts": (datetime.now() - timedelta(days=2)).isoformat(), "action": "TRIGGER", "narration": "Weather payload received"}
        ]
    }
    db['claims'].create(c1)
    
    # Payout 1 (W001)
    db['payouts'].create({
        "payout_id": f"pay_{c1_id}",
        "claim_id": c1_id,
        "worker_id": "W001",
        "amount": 480.0,
        "status": "SUCCESS",
        "method": "UPI",
        "compliance_confidence": "HIGH",
        "created_at": (datetime.now() - timedelta(days=2)).isoformat()
    })

    # Update total_payouts for W001
    worker["total_payouts"] = 480.0
    db['workers'].update(worker["_id"], worker)

    # Claim 2: BLOCKED / REVIEW (W002) - Fraud
    c2_id = db['claims'].generate_claim_id()
    db['claims'].create({
        "claim_id": c2_id,
        "worker_id": "W002",
        "policy_id": "P_MOCK_002",
        "event_type": "AQI_SPIKE",
        "trigger_conditions": "AQI exceeded 400",
        "estimated_loss": 500.0,
        "fraud_score": 85.0,
        "status": "BLOCKED",
        "governance_status": "FRAUD_LOCK",
        "governance_tags": ["GPS_SPOOF", "VELOCITY_ABUSE"],
        "created_at": (datetime.now() - timedelta(hours=5)).isoformat(),
        "audit_trail": [
            {"ts": (datetime.now() - timedelta(hours=5)).isoformat(), "action": "FRAUD_SCAN", "narration": "GPS anomaly detected via IsolationForest."}
        ]
    })
    
    # Claim 3: POOL PROTECTION (W010)
    c3_id = db['claims'].generate_claim_id()
    db['claims'].create({
        "claim_id": c3_id,
        "worker_id": "W010",
        "policy_id": "P_MOCK_010",
        "event_type": "HEATWAVE",
        "estimated_loss": 600.0,
        "fraud_score": 15.0,
        "status": "REVIEW",
        "governance_status": "POOL_PROTECTION",
        "governance_tags": ["EXPOSURE_CAP_BREACH"],
        "created_at": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "audit_trail": [
            {"ts": (datetime.now() - timedelta(minutes=15)).isoformat(), "action": "LIQUIDITY_CHECK", "narration": "Mass exposure >40%. Routed to manual."}
        ]
    })
    
    print("Inserted 3 complex Claims & 1 Payout.")

def seed_activity(db):
    print("\n--- Seeding Activity & Fraud Logs ---")
    
    existing = db['audit'].find_many(limit=1)
    if existing:
        print("Audit logs exist. Skipping standalone logs.")
        return
        
    logs = [
        {"timestamp": datetime.now().isoformat(), "level": "INFO", "source": "Scheduler", "message": "Heartbeat sweep complete. No anomalies."},
        {"timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(), "level": "WARNING", "source": "FraudEngine", "message": "Ring activity suspected in Zone: Andheri East"},
        {"timestamp": (datetime.now() - timedelta(hours=1)).isoformat(), "level": "INFO", "source": "SupabaseSync", "message": "Cache successfully merged with cloud layer."},
    ]
    for log in logs:
        db['audit'].create(log)
    print("Inserted 3 Activity Logs.")

def run_seed():
    print("====================================")
    print("JARVIS EnviroSense — Database Seeder")
    print("====================================\n")
    
    db = get_db()
    seed_zones(db)
    workers = seed_workers(db)
    seed_policies(db, workers)
    seed_claims_and_payouts(db)
    seed_activity(db)
    
    print("\n✅ Seeding Complete. The system is populated and Judge-Ready.")

if __name__ == "__main__":
    run_seed()
