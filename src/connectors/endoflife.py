import requests
from typing import List, Dict, Any
from datetime import datetime
from connectors.base import BaseConnector
from config import ENDOFLIFE_API_BASE, ENDOFLIFE_PRODUCTS, DEFAULT_HEADERS

class EndOfLifeConnector(BaseConnector):
    def fetch_devices(self) -> List[Dict[str, Any]]:
        devices = []
        today_str = datetime.now().strftime("%Y-%m-%d")

        for prod_info in ENDOFLIFE_PRODUCTS:
            brand = prod_info["brand"]
            product = prod_info["product"]
            url = f"{ENDOFLIFE_API_BASE}/{product}.json"

            try:
                response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
                if response.status_code != 200:
                    continue
                
                data = response.json()
                for item in data:
                    cycle_name = str(item.get("cycle") or item.get("release") or "Unknown")
                    if product == "iphone":
                        model_name = f"iPhone {cycle_name}"
                    elif product == "pixel":
                        model_name = f"Pixel {cycle_name}"
                    elif product == "samsung-galaxy":
                        model_name = f"Galaxy {cycle_name}" if not cycle_name.lower().startswith("galaxy") else cycle_name
                    else:
                        model_name = cycle_name
                    
                    eol_val = item.get("eol")
                    support_val = item.get("support")
                    
                    is_eol = False
                    security_end = "N/A"
                    os_end = "N/A"

                    # Parse EOL
                    if isinstance(eol_val, bool):
                        is_eol = eol_val
                        security_end = "EOL" if eol_val else "Podporováno"
                    elif isinstance(eol_val, str):
                        security_end = eol_val
                        if eol_val <= today_str:
                            is_eol = True
                    
                    # Parse Support (OS updates)
                    if isinstance(support_val, str):
                        os_end = support_val
                    elif isinstance(support_val, bool):
                        os_end = "Ano" if support_val else "Ne"

                    status = "EOL (Podpora ukončena)" if is_eol else "Aktivně podporováno"

                    devices.append({
                        "brand": brand,
                        "model": model_name,
                        "status": status,
                        "os_support_end": os_end,
                        "security_support_end": security_end,
                        "is_eol": is_eol,
                        "source": f"endoflife.date ({product})"
                    })
            except Exception as e:
                print(f"[EndOfLifeConnector] Chyba při stahování {product}: {e}")

        return devices
