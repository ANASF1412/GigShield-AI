"""
Base Repository - Memory-First CRUD operations for Streamlit Hackathon Demos
(Uses st.session_state as a reliable, zero-touch storage engine)
"""
import streamlit as st
import json
import os
import uuid
from datetime import datetime
from dateutil import parser
from typing import Optional, List, Dict, Any

class BaseRepository:
    """Base repository class with common CRUD operations using session_state."""

    def __init__(self, collection_name: str):
        """Initialize with session state storage, pre-populated from seed if available."""
        self.collection_name = collection_name
        
        # Absolute path to seed data
        self.seed_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed_data.json"))
        
        # 1. Initialize global storage if not exists
        if "db_storage" not in st.session_state:
            st.session_state.db_storage = {}
        
        # 2. Always ensure the collection is initialized
        if self.collection_name not in st.session_state.db_storage or not st.session_state.db_storage[self.collection_name]:
            self._load_seed_data()

    def _save_to_disk(self):
        """Persist the current session state back to seed_data.json for persistence across reboots."""
        try:
            # Prepare data (convert datetime objects back to ISO strings)
            export_data = {}
            for col_name, docs in st.session_state.db_storage.items():
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
                            if isinstance(v, str) and (k.endswith("_at") or k.endswith("_date") or k == "timestamp" or k == "completed_at"):
                                try:
                                    doc[k] = parser.parse(v)
                                except: pass
                        processed_docs.append(doc)
                    
                    st.session_state.db_storage[self.collection_name] = processed_docs
            except Exception as e:
                print(f"Error seeding {self.collection_name}: {e}")

    def create(self, document: Dict[str, Any]) -> str:
        """Create a new document in memory."""
        # Ensure it has an ID
        if "_id" not in document:
            document["_id"] = str(uuid.uuid4())
        if "created_at" not in document:
            document["created_at"] = datetime.now()
        
        st.session_state.db_storage[self.collection_name].append(document)
        self._save_to_disk()
        return str(document["_id"])

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict]:
        """Find one document by simple field match."""
        for doc in st.session_state.db_storage[self.collection_name]:
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
        results = []
        for doc in st.session_state.db_storage[self.collection_name]:
            match = True
            for key, val in query.items():
                # Handle basic list membership if needed
                if isinstance(val, dict) and "$in" in val:
                    if doc.get(key) not in val["$in"]:
                        match = False; break
                elif doc.get(key) != val:
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
        return st.session_state.db_storage[self.collection_name]

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
        initial_count = len(st.session_state.db_storage[self.collection_name])
        st.session_state.db_storage[self.collection_name] = [
            doc for doc in st.session_state.db_storage[self.collection_name] 
            if not all(doc.get(k) == v for k, v in query.items())
        ]
        return len(st.session_state.db_storage[self.collection_name]) < initial_count

    def delete_by_id(self, doc_id: str, id_field: str = "_id") -> bool:
        """Delete by ID."""
        return self.delete({id_field: doc_id})

    def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete many."""
        initial_count = len(st.session_state.db_storage[self.collection_name])
        st.session_state.db_storage[self.collection_name] = [
            doc for doc in st.session_state.db_storage[self.collection_name] 
            if not all(doc.get(k) == v for k, v in query.items())
        ]
        return initial_count - len(st.session_state.db_storage[self.collection_name])

    def count(self, query: Dict[str, Any] = None) -> int:
        """Count matching documents."""
        if not query:
            return len(st.session_state.db_storage[self.collection_name])
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
