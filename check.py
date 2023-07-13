import requests

output = open('output.txt', 'a')
counter = 1

with open('domain.txt', 'r') as f :
    for line in f :
        print(counter, end='\r')
        link = line.split('\n')[0]
        
        try:
            r = requests.get(link, timeout=0.8)
            if r.status_code == 200:
                print(link, ' @Success!')
                output.write(line)
                output.flush()
        except Exception as e:
            pass
            
        counter += 1
