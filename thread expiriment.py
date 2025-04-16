import threading
import time

stop_event = threading.Event()

def print_to_terminal():
    while not stop_event.is_set():
        try:
            print("[]", input(""))
        except EOFError:
            break  # In case input is interrupted

def countw():
    count = 0
    while not stop_event.is_set():
        print(count)
        count += 1
        time.sleep(1)

thread = threading.Thread(target=print_to_terminal)
thread2 = threading.Thread(target=countw)

try:
    thread.start()
    thread2.start()
    
    # MAIN THREAD WAITS HERE
    thread.join()
    thread2.join()

except KeyboardInterrupt:
    print("KeyboardInterrupt received! Stopping...")
    stop_event.set()
    # Optionally wait again to make sure threads clean up
    thread.join()
    thread2.join()

print("Program exited gracefully.")
