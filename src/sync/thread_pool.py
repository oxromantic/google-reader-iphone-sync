import thread, time, threading
from output import *

def ping():
	try:
		threading.currentThread().ping()
	except AttributeError, e:
		pass

# threaded decorator
# relies on the decorated method's instance having an initialised _lock variable
def locking(process):
	def fn(self, *args, **kwargs):
		self._lock.acquire()
		try:
			ret = process(self, *args, **kwargs)
		finally:
			self._lock.release()
		return ret
	fn.__name__ = process.__name__
	return fn

class ThreadAction(threading.Thread):
	def __init__(self, func, on_error = None, on_success = None, name=None, *args, **kwargs):
		super(self.__class__, self).__init__(group=None, target=None, name=name, args=(), kwargs={})
		self.args = args
		self.kwargs = kwargs
		self.func = func
		self.on_error = on_error
		self.on_success = on_success
		self.name = name
		self._killed = False
		self._lock = thread.allocate_lock()
		self.start_time = time.time()

	def kill(self):
		self._killed = True
	
	def ping(self):
		self.start_time = time.time()
	
	def run(self):
		if self._killed: return
		if self.name is not None:
			threading.currentThread().setName(self.name)
		
		try:
			self.func(*self.args, **self.kwargs)
		except StandardError, e:
			error("thread error! %s " % e)
			if self._killed: return
			if self.on_error is not None:
				self.on_error(e)
				return
			else:
				raise
			
		if self._killed: return
		if self.on_success is not None:
			self.on_success()
	

class ThreadPool:
	_max_count = 6
	_threads = []
	_global_count = 0
	_action_buffer = []
	
	def __init__(self):
		self._lock = thread.allocate_lock()

	def _get_count(self):
		return len(self._threads)
	_count = property(_get_count)
	
	def _sleep(self, seconds = 1):
		self._lock.release()
		time.sleep(seconds)
		self._lock.acquire()
	
	def _wait_for_any_thread_to_finish(self):
		initial_count = self._count
		global_count = self._global_count
		silence_threshold = 60
		sleeps = 0
		
		initial_threads = list(self._threads) # take a copy
		
		if self._count == 0:
			debug("no threads running!")
			return

		def threads_unchanged():
			if self._count != initial_count:
				return False
			return all(a is b for a,b in zip(self._threads, initial_threads))
		
		def partition_threads():
			now = time.time()
			old = []
			new = []
			for th in self._threads:
				if th.start_time + silence_threshold > now:
					new.append(th)
				else:
					old.append(th)
			return (old, new)
		
		while threads_unchanged():
			old_threads, new_threads = partition_threads()
			if len(old_threads) > 0:
				error("%s threads have been running over %s seconds" % (len(old_threads), silence_threshold))
				for thread_ in old_threads:
					info(" - killing thread: %s" % (thread.name,))
					thread_.kill()
				error("%s threads killed" % (len(old_threads),))
				self._threads = new_threads
				break

			self._sleep(1)
			sleeps += 1

	
	@locking
	def spawn(self, function,
		name = None,
		on_success = None,
		on_error = None,
		*args, **kwargs):
		while self._count >= self._max_count:
			self._wait_for_any_thread_to_finish()

		debug("there are currently %s threads running" % self._count)
		self._global_count += 1
		thread_id = "%s.%s" % (self._global_count, ascii(name)) if name is not None else "thread %s" % (self._global_count,)
		action = ThreadAction(
			function,
			name = thread_id,
			*args, **kwargs)
		action.on_error = lambda e: self._thread_error(action, on_error, e)
		action.on_success = lambda: self._thread_finished(action, on_success)
		self._threads.append(action)
		debug("starting new thread")
		action.start()
	
	@locking
	def _thread_error(self, thread, callback, e):
		self._locked_thread_finished(thread)
		if callback is None:
			exception("thread raised an exception and ended: %s" % (e,))
		else:
			callback(e)
		
	@locking
	def _thread_finished(self, thread, next_action):
		self._action_buffer.append(next_action)
		self._locked_thread_finished(thread)
	
	def _locked_thread_finished(self, thread):
		self._threads.remove(thread)
		debug("thread finished - there remain %s threads" % (self._count,))
	
	@locking
	def collect(self):
		self._collect()
	
	@locking
	def collect_all(self):
		debug("waiting for %s threads to finish" % self._count)
		while self._count > 0:
			self._wait_for_any_thread_to_finish()
			
		self._collect()

	# non-locking - for internal use only
	def _collect(self):
		for next_action in self._action_buffer:
			if next_action is not None:
				debug("calling action: %s" % (next_action,))
				next_action()
		self._action_buffer = []
