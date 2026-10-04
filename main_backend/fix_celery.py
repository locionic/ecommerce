with open('src/celery.py', 'r') as f:
    celery = f.read()

celery = celery.replace('import os\nimport configurations\n\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")\n\nif not os.environ.get("DJANGO_CONFIGURATION"):\n    os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")\n\nconfigurations.setup()', 'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")')

with open('src/celery.py', 'w') as f:
    f.write(celery)
