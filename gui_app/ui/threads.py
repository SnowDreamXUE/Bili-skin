from PySide6.QtCore import QThread, Signal

from gui_app.core.api_client import ApiClient
from gui_app.core.downloader import Downloader


class SearchThread(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, keyword: str):
        super().__init__()
        self.keyword = keyword

    def run(self):
        try:
            results = ApiClient.search_items(self.keyword)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class DownloadThread(QThread):
    progress = Signal(int, str)
    finished = Signal(int)
    error = Signal(str)
    log = Signal(str)

    def __init__(self, item: dict, save_dir: str):
        super().__init__()
        self.item = item
        self.save_dir = save_dir
        self.downloader = Downloader()

    def stop(self):
        self.downloader.stop()

    def run(self):
        try:
            name = self.item.get("name", "未知")
            part_id = self.item.get("part_id", 0)
            properties = self.item.get("properties", {})

            if part_id == 0:
                act_id = properties.get("dlc_act_id")
                lottery_id = properties.get("dlc_lottery_id")
                if not act_id or not lottery_id:
                    self.error.emit("无法获取收藏集的 act_id 或 lottery_id")
                    return
                count = self.downloader.download_collectible(
                    name, int(act_id), int(lottery_id), self.save_dir,
                    progress_callback=lambda p, f: self.progress.emit(p, f),
                    log_callback=lambda m: self.log.emit(m)
                )
            else:
                item_id = self.item.get("item_id")
                if not item_id:
                    self.error.emit("无法获取装扮的 item_id")
                    return
                count = self.downloader.download_suit(
                    name, int(item_id), self.save_dir,
                    progress_callback=lambda p, f: self.progress.emit(p, f),
                    log_callback=lambda m: self.log.emit(m)
                )
            self.finished.emit(count)
        except Exception as e:
            self.error.emit(str(e))