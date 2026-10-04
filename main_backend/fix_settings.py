import re

with open('src/settings.py', 'r') as f:
    content = f.read()

# Remove Configuration import
content = re.sub(r'from configurations import Configuration\n', '', content)
content = re.sub(r'from configurations import values\n', '', content)

# Find the Dev class body and unindent it
match = re.search(r'class Dev\(Configuration\):\n(.*?)class Prod\(Dev\):', content, re.DOTALL)
if match:
    dev_body = match.group(1)
    # unindent
    dev_body = '\n'.join([line[4:] if line.startswith('    ') else line for line in dev_body.split('\n')])
    
    # Replace everything from Dev onwards
    content = content[:content.find('class Dev')] + dev_body

with open('src/settings.py', 'w') as f:
    f.write(content)

with open('manage.py', 'r') as f:
    manage = f.read()

manage = manage.replace('from configurations.management import execute_from_command_line', 'from django.core.management import execute_from_command_line')
with open('manage.py', 'w') as f:
    f.write(manage)

with open('src/wsgi.py', 'r') as f:
    wsgi = f.read()
wsgi = wsgi.replace('from configurations.wsgi import get_wsgi_application', 'from django.core.wsgi import get_wsgi_application')
with open('src/wsgi.py', 'w') as f:
    f.write(wsgi)

if __import__('os').path.exists('src/asgi.py'):
    with open('src/asgi.py', 'r') as f:
        asgi = f.read()
    asgi = asgi.replace('from configurations.asgi import get_asgi_application', 'from django.core.asgi import get_asgi_application')
    with open('src/asgi.py', 'w') as f:
        f.write(asgi)
