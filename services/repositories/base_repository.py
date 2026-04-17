"""
Base Repository - Memory-First CRUD operations for Streamlit Hackathon Demos
(Uses a globally shared @st.cache_resource dict as a reliable database simulator)
"""
import streamlit as st
import json
import os
import uuid
from datetime import datetime
from dateutil import parser
from typing import Optional, List, Dict, Any

@st.cache_resource
def get_global_db_storage():
    """Returns a globally shared dictionary to simulate a database across all user sessions."""
    return {}

class BaseRepository:
    """Base repository class with common CRUD operations using global shared storage."""

    def __init__(self, collection_name: str):
        """Initialize with global shared storage, pre-populated from seed if available."""
        self.collection_name = collection_name
        self.db_storage = get_global_db_storage()
        
        # --- Supabase Initialization ---
        self.supabase = None
        try:
            from services.supabase_service import get_supabase_client
            self.supabase = get_supabase_client()
        except:
            self.supabase = None
        
        # Absolute path to seed data
        self.seed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed_data.json"))
        
        # Always ensure the collection is initialized
        if self.collection_name not in self.db_storage or not self.db_storage[self.collection_name]:
            self.db_storage[self.collection_name] = []
            self._load_seed_data()

    def _save_to_disk(self):
        """Persist the current global state back to seed_data.json for persistence across reboots."""
        try:
            # Prepare data (convert datetime objects back to ISO strings)
            export_data = {}
            for col_name, docs in self.db_storage.items():
                processed_docs = []
                for doc in docs:
                    new_doc = doc.copy()
                    for k, v in new_doc.items():
                        if isinstance(v, datetime):
                            new_doc[k] = v.isoformat()
                    processed_docs.append(new_doc)
                export_data[col_name] = processed_docs
                
            with open(self.seed_path, "w") as f:
                json.dump(export_data, f, indent=4)
        except Exception as e:
            print(f"FAILED TO PERSIST: {e}")

    def _load_seed_data(self):
        """Pre-populate the collection from data/seed_data.json."""
        if os.path.exists(self.seed_path):
            try:
                with open(self.seed_path, "r") as f:
                    all_seed_data = json.load(f)
                
                if self.collection_name in all_seed_data:
                    raw_docs = all_seed_data[self.collection_name]
                    processed_docs = []
                    for doc in raw_docs:
                        for k, v in doc.items():
                            if isinstance(v, str) and (k.endswith("_at") or k.endswith("_date") or k == "timestamp" or k == "completed_at" or k == "start_date" or k == "end_date"):
                                try:
                                    doc[k] = parser.parse(v)
                                except: pass
                        processed_docs.append(doc)
                    
                    self.db_storage[self.collection_name] = processed_docs
            except Exception as e:
                print(f"Error seeding {self.collection_name}: {e}")

    def create(self, document: Dict[str, Any]) -> str:
        """Create a new document in memory."""
        # Ensure it has an ID
        if "_id" not in document:
            document["_id"] = str(uuid.uuid4())
        if "created_at" not in document:
            document["created_at"] = datetime.now()
        
        self.db_storage[self.collection_name].append(document)
        self._save_to_disk()
        
        # Supabase Push Sync (Fallback Mode Supported)
        if self.supabase:
            try:
                # Prepare supabase compatible payload (convert datetimes)
                sb_doc = {}
                for k, v in document.items():
                    sb_doc[k] = v.isoformat() if isinstance(v, datetime) else v
                self.supabase.table(self.collection_name).insert(sb_doc).execute()
            except Exception as e:
                import logging
                logging.warning(f"Supabase sync failed for {self.collection_name}: {e}")

        return str(document["_id"])

    def _process_supabase_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ISO strings back to datetime objects to maintain strict type parity with local DB."""
        new_doc = {}
        for k, v in doc.items():
            if isinstance(v, str) and (k.endswith("_at") or k.endswith("_date") or k == "timestamp" or k == "completed_at" or k == "start_date" or k == "end_date"):
                try:
                    parsed = parser.parse(v)
                    # Keep tzinfo consistent with local DB (usually naive in this project)
                    new_doc[k] = parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
                except:
                    new_doc[k] = v
            else:
                new_doc[k] = v
        return new_doc

    def _sync_to_local_cache(self, fetched_docs_or_doc):
        """Safely upsert fetched remote documents into the local in-memory dict."""
        if not fetched_docs_or_doc: return
        
        # Ensure list processing
        docs = fetched_docs_or_doc if isinstance(fetched_docs_or_doc, list) else [fetched_docs_or_doc]
        
        current_cache = self.db_storage[self.collection_name]
        
        for doc in docs:
            # Figure out primary key natively without rewriting legacy logic
            id_val = doc.get("worker_id") or doc.get("policy_id") or doc.get("claim_id") or doc.get("_id")
            id_key = "worker_id" if "worker_id" in doc else ("policy_id" if "policy_id" in doc else ("claim_id" if "claim_id" in doc else "_id"))
            
            if not id_val:
                continue
                
            # Upsert into cache
            idx_to_replace = None
            for i, c_doc in enumerate(current_cache):
                if c_doc.get(id_key) == id_val:
                    idx_to_replace = i
                    break
                    
            if idx_to_replace is not None:
                current_cache[idx_to_replace] = doc
            else:
                current_cache.append(doc)
                
        self.db_storage[self.collection_name] = current_cache

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict]:
        """Find one document by simple field match."""
        if self.supabase:
            try:
                q = self.supabase.table(self.collection_name).select("*")
                for key, val in query.items():
                    if not isinstance(val, dict):
                        q = q.eq(key, val)
                res = q.limit(1).execute()
                if res.data:
                    doc = self._process_supabase_doc(res.data[0])
                    self._sync_to_local_cache(doc)
                    return doc
            except Exception as e:
                import logging
                logging.warning(f"Supabase find_one failed, falling back to local: {e}")
                
        # --- LOCAL FALLBACK ---
        for doc in self.db_storage[self.collection_name]:
            match = True
            for key, val in query.items():
                if doc.get(key) != val:
                    match = False
                    break
            if match:
                return doc
        return None

    def find_by_id(self, doc_id: str, id_field: str = "_id") -> Optional[Dict]:
        """Find document by ID."""
        return self.find_one({id_field: doc_id})

    def find_many(self, query: Dict[str, Any], limit: int = 0, skip: int = 0,
                  sort_field: str = None, sort_order: int = -1) -> List[Dict]:
        """Find multiple documents with basic filtering and sorting."""
        if self.supabase:
            try:
                q = self.supabase.table(self.collection_name).select("*")
                for key, val in query.items():
                    if isinstance(val, dict):
                        if "$in" in val:
                            q = q.in_(key, val["$in"])
                        if "$gte" in val:
                            val_gte = val["$gte"].isoformat() if isinstance(val["$gte"], datetime) else val["$gte"]
                            q = q.gte(key, val_gte)
                        if "$lte" in val:
                            val_lte = val["$lte"].isoformat() if isinstance(val["$lte"], datetime) else val["$lte"]
                            q = q.lte(key, val_lte)
                    else:
                        q = q.eq(key, val)
                
                if sort_field:
                    q = q.order(sort_field, desc=(sort_order == -1))
                if limit > 0:
                    # Fetching limit + skip to slice safely in memory
                    q = q.limit(limit + skip)
                    
                res = q.execute()
                processed = [self._process_supabase_doc(d) for d in res.data]
                
                # Cloud-Sync Local Cache
                self._sync_to_local_cache(processed)
                
                if skip > 0:
                    processed = processed[skip:]
                
                # Apply limits purely incase db wrapper didnt
                if limit > 0 and len(processed) > limit:
                    processed = processed[:limit]
                    
                return processed
            except Exception as e:
                import logging
                logging.warning(f"Supabase find_many failed, falling back to local: {e}")
                
        # --- LOCAL FALLBACK ---
        results = []
        for doc in self.db_storage[self.collection_name]:
            match = True
            for key, val in query.items():
                doc_val = doc.get(key)
                # Handle MongoDB-style operators
                if isinstance(val, dict):
                    if "$in" in val and doc_val not in val["$in"]:
                        match = False; break
                    if "$gte" in val and not (doc_val and doc_val >= val["$gte"]):
                        match = False; break
                    if "$lte" in val and not (doc_val and doc_val <= val["$lte"]):
                        match = False; break
                elif doc_val != val:
                    match = False; break
            if match:
                results.append(doc)

        # Sort
        if sort_field:
            reverse = True if sort_order == -1 else False
            results.sort(key=lambda x: x.get(sort_field, ""), reverse=reverse)

        # Skip and Limit
        if skip > 0:
            results = results[skip:]
        if limit > 0:
            results = results[:limit]
            
        return results

    def find_all(self) -> List[Dict]:
        """Find all documents in collection."""
        if self.supabase:
            try:
                res = self.supabase.table(self.collection_name).select("*").execute()
                processed = [self._process_supabase_doc(d) for d in res.data]
                self._sync_to_local_cache(processed)
                return processed
            except Exception as e:
                import logging
                logging.warning(f"Supabase find_all failed, falling back: {e}")
                
        # --- LOCAL FALLBACK ---
        return self.db_storage[self.collection_name]

    def update(self, query: Dict[str, Any], update_data: Dict[str, Any], upsert: bool = False) -> bool:
        """Update multiple documents (In MEMORY)."""
        modified = False
        target_docs = self.find_many(query)
        
        # Simple $set logic simulation
        data_to_set = update_data.get("$set", update_data)
        
        for doc in target_docs:
            doc.update(data_to_set)
            modified = True
            
        if modified:
            self._save_to_disk()
            # Push changes to Supabase
            if self.supabase:
                try:
                    for doc in target_docs:
                        sb_doc = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in doc.items()}
                        id_val = doc.get("worker_id") or doc.get("policy_id") or doc.get("claim_id") or doc.get("_id")
                        id_key = "worker_id" if "worker_id" in doc else ("policy_id" if "policy_id" in doc else ("claim_id" if "claim_id" in doc else "_id"))
                        self.supabase.table(self.collection_name).update(sb_doc).eq(id_key, id_val).execute()
                except Exception as e:
                    pass
            
        if not modified and upsert:
            self.create(query | data_to_set)
            return True
            
        return modified

    def update_by_id(self, doc_id: str, update_data: Dict[str, Any], id_field: str = "_id") -> bool:
        """Update by ID."""
        update_data["updated_at"] = datetime.now()
        return self.update({id_field: doc_id}, {"$set": update_data})

    def update_many(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update many (basic count)."""
        target_docs = self.find_many(query)
        data_to_set = update.get("$set", update)
        for doc in target_docs:
            doc.update(data_to_set)
        return len(target_docs)

    def delete(self, query: Dict[str, Any]) -> bool:
        """Delete from memory."""
        initial_count = len(self.db_storage[self.collection_name])
        self.db_storage[self.collection_name] = [
            doc for doc in self.db_storage[self.collection_name] 
            if not all(doc.get(k) == v for k, v in query.items())
        ]
        return len(self.db_storage[self.collection_name]) < initial_count

    def delete_by_id(self, doc_id: str, id_field: str = "_id") -> bool:
        """Delete by ID."""
        return self.delete({id_field: doc_id})

    def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete many."""
        initial_count = len(self.db_storage[self.collection_name])
        self.db_storage[self.collection_name] = [
            doc for doc in self.db_storage[self.collection_name] 
            if not all(doc.get(k) == v for k, v in query.items())
        ]
        return initial_count - len(self.db_storage[self.collection_name])

    def count(self, query: Dict[str, Any] = None) -> int:
        """Count matching documents."""
        if not query:
            return len(self.db_storage[self.collection_name])
        return len(self.find_many(query))

    def exists(self, query: Dict[str, Any]) -> bool:
        """Check exists."""
        return self.find_one(query) is not None

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict]:
        """Simple aggregation layer for counts (Simulated for Hackathon UI)."""
        # We only need to support basic counts for the dashboard charts
        return self.find_all()

    def bulk_insert(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Bulk insert."""
        ids = []
        for doc in documents:
            ids.append(self.create(doc))
        return ids

    def create_index(self, field_name: str, unique: bool = False): pass
    def delete_index(self, field_name: str): pass
