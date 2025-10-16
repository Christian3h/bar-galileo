with open('bar_galileo/bar_galileo/settings.py', 'r') as f:
    content = f.read()

content = content.replace("'expenses',", "'expenses',\n    'nominas',")
content = content.replace("'django.contrib.auth.middleware.AuthenticationMiddleware',", "'django.contrib.auth.middleware.AuthenticationMiddleware',\n    'accounts.middleware.AdminRedirectMiddleware',")

with open('bar_galileo/bar_galileo/settings.py', 'w') as f:
    f.write(content)
