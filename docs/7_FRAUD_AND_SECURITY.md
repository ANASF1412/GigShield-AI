# Fraud & Security Stack

The platform operates on a "Zero-Trust Data, High-Trust Execution" philosophy.

## 🔒 Defense Layers

### 1. Velocity Checks
A driver cannot extract >3 claims within a 7-day rolling window, regardless of weather severity.

### 2. Daily Caps
Maximum payout is globally restricted locally. A worker attempting to extract continuous fractions of premium beyond ₹2,000/day receives an instant `FLAGGED` tag.

### 3. IsolationForest Routing (Ring Detection)
ML does not govern the amount of payout, but it evaluates spatial behaviors. If 40 delivery workers in the exact same GPS block trigger with identical metadata simultaneously, the transaction shifts from automated AI to `Manual Review (Cluster Proxy Detected)`.

### 4. Semantic Circuit Breakers
Fake payloads cannot crash the system. If an attacker injects an impossible API value (`AQI = 5000`), the `trigger_claims_for_event()` breaks the script naturally and halts execution without exposing liquidity.
