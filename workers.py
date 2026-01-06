import threading
from queue import Queue
from classifier import Category
from processor import compress, trim, trim_and_compress
import traceback
from logging_setup import logger


class EncodeWorker(threading.Thread):
    def __init__(self, queue: Queue, progress_queue=None):
        super().__init__(daemon=True)
        self.queue = queue
        # optional queue.Queue() where we post ('start'|'end', Path, Category)
        self.progress_queue = progress_queue

    def run(self):
        while True:
            item = self.queue.get()
            # sentinel used to request shutdown
            if item is None:
                self.queue.task_done()
                break

            try:
                category, inp, out = item
                logger.info(f"start_processing file={inp} category={category.name}")
                if self.progress_queue:
                    try:
                        self.progress_queue.put(("start", str(inp), category.name))
                    except Exception:
                        pass

                if category == Category.COMPRESS_ONLY:
                    compress(inp, out)
                elif category == Category.TRIM_ONLY:
                    trim(inp, out)
                elif category == Category.TRIM_AND_COMPRESS:
                    trim_and_compress(inp, out)

                logger.info(f"end_processing file={inp} category={category.name}")
                if self.progress_queue:
                    try:
                        self.progress_queue.put(("end", str(inp), category.name))
                    except Exception:
                        pass
            except Exception as e:
                # avoid killing the worker thread on a single failure
                logger.exception(f"processing error for item={item}: {e}")
            finally:
                self.queue.task_done()
