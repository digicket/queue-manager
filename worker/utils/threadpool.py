import logging
import traceback

from queue import Queue
from threading import Thread

logger = logging.getLogger(__name__)


class ThreadPool(object):
  """
  Pool of threads consuming tasks from a queue
  """

  class Worker(Thread):
    """
    Thread executing tasks from a given tasks queue
    """

    def __init__(self, tasks):
      Thread.__init__(self)
      self.tasks = tasks
      self.daemon = True
      self.start()

    def run(self):
      """
      Trigger the threads
      """
      while True:
        func, args, kargs = self.tasks.get()
        try:
          func(*args, **kargs)
        except Exception as ex:
          # An exception happened in this thread
          logger.error("Failed: %s" % ex)
          logger.error(traceback.format_exc())
        finally:
          # Mark this task as done, whether an exception happened or not
          self.tasks.task_done()

  def __init__(self, max_threads=1):
    self.tasks = Queue(max_threads)
    for _ in range(max_threads):
      ThreadPool.Worker(self.tasks)

  def add_task(self, func, *args, **kargs):
    """
    Add a task to the queue
    """
    self.tasks.put((func, args, kargs))

  def map(self, func, args_list):
    """
    Add a list of tasks to the queue
    """
    for args in args_list:
      self.add_task(func, args)

  def wait_completion(self):
    """
    Wait for completion of all the tasks in the queue
    """
    self.tasks.join()