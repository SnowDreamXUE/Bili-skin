from typing import Optional, List, Dict
import requests

from gui_app.config.api import SEARCH_API, SUIT_DETAIL_API, DLC_DETAIL_API, HEADERS


class ApiClient:
    @staticmethod
    def search_items(keyword: str, ps: int = 20) -> List[Dict]:
        params = {"key_word": keyword, "ps": ps, "pn": 1}
        try:
            resp = requests.get(SEARCH_API, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0 and data.get("data", {}).get("list"):
                return data["data"]["list"]
            return []
        except Exception as e:
            raise Exception(f"搜索失败：{str(e)}")

    @staticmethod
    def get_suit_detail(item_id: int) -> Optional[Dict]:
        params = {"item_id": item_id}
        try:
            resp = requests.get(SUIT_DETAIL_API, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data")
            return None
        except Exception as e:
            raise Exception(f"获取装扮详情失败：{str(e)}")

    @staticmethod
    def get_dlc_detail(act_id: int, lottery_id: int) -> Optional[Dict]:
        params = {"act_id": act_id, "lottery_id": lottery_id}
        try:
            resp = requests.get(DLC_DETAIL_API, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data")
            return None
        except Exception as e:
            raise Exception(f"获取收藏集详情失败：{str(e)}")