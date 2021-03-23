from worker.config import settings
from worker.utils.threadpool import ThreadPool


class TaskScheduler(object):
    def __init__(self, max_threads=None):
        if not max_threads:
            max_threads = settings.MAX_THREADS

        self._thread_pool = ThreadPool(max_threads=max_threads)

    def add_task_to_pool(self, func):
        """
        Add a task to the thread pool
        Args:
          func(func): Function to add to pool
        Raises:
          AsyncProcessorError: When the async request cannot be processed.
        """
        self._thread_pool.add_task(func)

    def is_task_pool_vacant(self):
        """
        Check if the task pool has a free thread to process a request
        Returns:
          boolean: True if task_pool is not empty, False otherwise.
        """
        return self._thread_pool.tasks.maxsize > (
            self._thread_pool.tasks.unfinished_tasks)

    def get_free_worker_size(self):
        """
        Get the free task worker size
        Returns:
            int: Number of free workers
        """
        return self._thread_pool.tasks.maxsize - self._thread_pool.tasks.unfinished_tasks
