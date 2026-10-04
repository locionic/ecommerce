with open('src/celery.py', 'r') as f:
    lines = f.readlines()

with open('src/celery.py', 'w') as f:
    for line in lines:
        if 'import configurations' not in line and 'configurations.setup()' not in line:
            f.write(line)
