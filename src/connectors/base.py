from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseConnector(ABC):
    @abstractmethod
    def fetch_devices(self) -> List[Dict[str, Any]]:
        """
        Fetches mobile device lifecycle data.
        Returns a list of dicts with keys:
        - brand (str)
        - model (str)
        - status (str): e.g. "Active", "Quarterly", "EOL"
        - os_support_end (str): Date or "N/A"
        - security_support_end (str): Date or "N/A"
        - is_eol (bool): True if updates ended
        - source (str): Name of data source
        """
        pass
