import os
import json
from datetime import datetime, timedelta
from pathlib import Path

class KeyManager:
    """
    Simplified key management: tracks key metadata (creation date,
    version) so you know when manual rotation is due. Does NOT auto-rotate
    (that needs an HSM/vault in real production) — this is the MVP-appropriate
    version: visibility + a manual rotation procedure.
    """
    METADATA_FILE = Path("data/key_metadata.json")
    ROTATION_INTERVAL_DAYS = 180

    def __init__(self):
        self.METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not self.METADATA_FILE.exists():
            self._save_metadata({
                "current_version": 1,
                "created_at": datetime.utcnow().isoformat(),
                "history": []
            })

    def _load_metadata(self) -> dict:
        with open(self.METADATA_FILE) as f:
            return json.load(f)

    def _save_metadata(self, data: dict):
        with open(self.METADATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def is_rotation_due(self) -> bool:
        meta = self._load_metadata()
        created = datetime.fromisoformat(meta["created_at"])
        return datetime.utcnow() - created > timedelta(days=self.ROTATION_INTERVAL_DAYS)

    def record_rotation(self, new_version: int):
        meta = self._load_metadata()
        meta["history"].append({
            "version": meta["current_version"],
            "retired_at": datetime.utcnow().isoformat()
        })
        meta["current_version"] = new_version
        meta["created_at"] = datetime.utcnow().isoformat()
        self._save_metadata(meta)

    def status(self) -> dict:
        meta = self._load_metadata()
        return {
            "current_version": meta["current_version"],
            "created_at": meta["created_at"],
            "rotation_due": self.is_rotation_due(),
            "past_rotations": len(meta["history"])
        }

if __name__ == "__main__":
    km = KeyManager()
    print(km.status())