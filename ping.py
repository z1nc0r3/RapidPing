import requests

def load_or_create_counter():
    try:
        with open('counter.txt', 'r') as counter_file:
            return int(counter_file.read())
    except FileNotFoundError:
        return int(input('Enter the starting point: '))

counter = load_or_create_counter()

output = open('output.txt', 'a')

with open('domain.txt', 'r') as f:
    lines = f.readlines()
    start = counter

    for line in lines[start - 1:]:
        print(counter, end='\r')
        link = line.strip()

        try:
            r = requests.get(link, timeout=0.65)
            if r.status_code == 200:
                print(link, ' @Success!')
                output.write(line)
                output.flush()
        except Exception as e:
            pass

        counter += 1

        with open('counter.txt', 'w') as counter_file:
            counter_file.write(str(counter))
            counter_file.flush()