import requests
import concurrent.futures
import signal
import sys
import threading

# Global shutdown event
shutdown_event = threading.Event()
print_lock = threading.Lock()
counter_lock = threading.Lock()

def load_or_create_counter():
    try:
        with open('counter.txt', 'r') as counter_file:
            return int(counter_file.read().strip())
    except FileNotFoundError:
        return int(input('Enter the starting point: '))

def save_counter(counter):
    with open('counter.txt', 'w') as counter_file:
        counter_file.write(str(counter))
        counter_file.flush()

def ping_domain(domain):
    if shutdown_event.is_set():
        return domain, 'Skipped'
    
    try:
        response = requests.get(domain, timeout=1.25) # Tune the timeout value
        if response.status_code == 200:
            return domain, 'Success'
        else:
            return domain, 'Failed'
    except requests.RequestException:
        return domain, 'Failed'

def signal_handler(sig, frame, executor):
    print('Received interrupt signal. Shutting down...')
    shutdown_event.set()
    executor.shutdown(wait=False)
    sys.exit(0)

def main():
    counter = load_or_create_counter()

    with open('domain.txt', 'r') as domain_file:
        domains = [line.strip() for line in domain_file.readlines()]

    start_index = counter - 1
    domains_to_ping = domains[start_index:]

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, executor))

        future_to_domain = {executor.submit(ping_domain, domain): domain for domain in domains_to_ping}

        with open('output.txt', 'a') as output_file:
            for future in concurrent.futures.as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    domain, status = future.result()
                    with counter_lock:
                        current_counter = counter
                        counter += 1
                        save_counter(counter)

                    if status == 'Success':
                        output_file.write(f"{domain}\n")
                        output_file.flush()

                    with print_lock:
                        if status == 'Success':
                            print(f"{current_counter} {domain} @ {status}")
                        else:
                            print(f"{current_counter}\r", end='')

                except Exception as exc:
                    with print_lock:
                        print(f"{counter} {domain} @ Exception: {exc}")

if __name__ == '__main__':
    main()
