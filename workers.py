import threading
from queue import Queue
from classifier import Category
from processor import compress, trim, trim_and_compress


class EncodeWorker(threading.Thread):
    def __init__(self, queue):
        super().__init__(daemon=True)
        self.queue = queue

    def run(self):
        while True:
            item = self.queue.get()
            if item is None:
                break

            category, inp, out = item

            if category == Category.COMPRESS_ONLY:
                compress(inp, out)
            elif category == Category.TRIM_AND_COMPRESS:
                trim_and_compress(inp, out)

            self.queue.task_done()
