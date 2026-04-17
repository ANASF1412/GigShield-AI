"""
MODULE: SCHEDULER SERVICE
Autonomous Monitoring Heartbeat for Zero-Touch Claims.
"""
from apscheduler.schedulers.background import BackgroundScheduler
import threading
from datetime import datetime
from services.automation_engine import AutomationEngine

class MonitoringScheduler:
    """Orchestrates background monitoring of environmental disruptions."""
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MonitoringScheduler, cls).__new__(cls)
                cls._instance.scheduler = BackgroundScheduler()
                cls._instance.engine = AutomationEngine()
                cls._instance.is_running = False
                cls._instance.total_cycles = 0
                cls._instance.last_run_ts = None
        return cls._instance

    def get_scheduler_status(self):
        """Proof of Autonomy metrics for the UI."""
        return {
            "status": "ACTIVE" if self.is_running else "IDLE",
            "cycles": self.total_cycles,
            "last_run": self.last_run_ts.strftime("%H:%M:%S") if self.last_run_ts else "NEVER",
            "pipeline": "Heartbeat \u2192 API Sync \u2192 Automation \u2192 Payout",
            "logs": getattr(self, 'recent_logs', [])
        }

    def _add_log(self, msg: str):
        if not hasattr(self, 'recent_logs'):
            self.recent_logs = []
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.recent_logs.insert(0, f"[{timestamp}] {msg}")
        self.recent_logs = self.recent_logs[:20]

    def start(self):
        """Start the background scheduler globally."""
        if not self.is_running:
            self.scheduler.add_job(
                func=self._heartbeat_job,
                trigger="interval",
                seconds=60,
                id="environmental_monitor_job"
            )
            self.scheduler.start()
            self.is_running = True

    def _heartbeat_job(self):
        """Internal job runner for zero-touch execution."""
        try:
            self._add_log("Scheduler waking up... preparing to fetch environmental state.")
            self.total_cycles += 1
            self.last_run_ts = datetime.now()
            
            # Fetch explicitly to log
            from services.environmental_api import EnvironmentalAPI
            c_data = EnvironmentalAPI.fetch_current_conditions()
            if c_data.get("is_real_data"):
                self._add_log(f"Fetched LIVE data from {c_data.get('source')} (Rain: {c_data.get('rainfall_mm')}mm, AQI: {c_data.get('aqi')})")
            else:
                self._add_log("Using FALLBACK environmental cache due to API unavailability.")
                
            if c_data.get('rainfall_mm', 0) > 40:
                self._add_log("Rainfall threshold crossed! Triggering automation engine...")
                
            res = self.engine.trigger_claims_for_event(rainfall_mm=c_data.get('rainfall_mm',0), temperature=c_data.get('temperature',0), aqi=c_data.get('aqi',0))
            if res.get("success"):
                stats = res.get("payout_stats", {})
                if stats.get("safe", 0) > 0 or stats.get("blocked", 0) > 0:
                    self._add_log(f"Automation executed: {stats.get('safe', 0)} Approved, {stats.get('blocked', 0)} Handled.")
            else:
                self._add_log(f"Pipeline evaluation completed: {res.get('message', 'No action needed')}")

        except Exception as e:
            self._add_log(f"Scheduler encountered error during cycle: {str(e)}")
