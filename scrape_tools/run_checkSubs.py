import os
import threading
import checkSubs
import time

def run_check_subs():
    while True:
        checkSubs.main()  # Run the subscription checking and notification code
        
        # Adjust the delay between checks as needed
        time.sleep(86400)  # 1day

if __name__ == "__main__":
    thread = threading.Thread(target=run_check_subs)
    thread.start()
