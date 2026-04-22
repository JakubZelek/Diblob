import multiprocessing
import threading
import time
import tracemalloc


def func_runner(func, ret_dict, args, kwargs, interval=0.01):
    tracemalloc.start()
    ret_dict['peak_memory_mb'] = 0
    ret_dict['result'] = None
    ret_dict['duration_s'] = 0
    start_time = time.time()

    def monitor_peak():
        peak = 0
        while True:
            _, peak_mem = tracemalloc.get_traced_memory()
            if peak_mem > peak:
                peak = peak_mem
                ret_dict['peak_memory_mb'] = peak / (1024*1024)
            time.sleep(interval)

    monitor_thread = threading.Thread(target=monitor_peak, daemon=True)
    monitor_thread.start()

    try:
        ret_dict['result'] = func(*args, **kwargs)
        ret_dict['duration_s'] = time.time() - start_time
    finally:
        _, peak = tracemalloc.get_traced_memory()
        if peak / (1024*1024) > ret_dict['peak_memory_mb']:
            ret_dict['peak_memory_mb'] = peak / (1024*1024)
        ret_dict['duration_s'] = time.time() - start_time
        tracemalloc.stop()


def measure_memory_and_time(func, timeout, *args, **kwargs):
    manager = multiprocessing.Manager()
    ret_dict = manager.dict()
    ret_dict['peak_memory_mb'] = 0
    ret_dict['duration_s'] = 0
    ret_dict['result'] = None

    p = multiprocessing.Process(target=func_runner, args=(func, ret_dict, args, kwargs))
    p.start()

    p.join(timeout)
    if p.is_alive():
        print("TIMEOUT! Kill the process")
        p.terminate()
        p.join()

    return ret_dict.get('result'), ret_dict.get('peak_memory_mb'), ret_dict.get('duration_s')
