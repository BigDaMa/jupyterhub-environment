import os
import sys

# Public access
c.JupyterHub.ip = '172.28.128.3'
c.JupyterHub.port = 443

# Docker access
c.JupyterHub.hub_ip = '172.28.128.3'
c.JupyterHub.hub_port = 8081

# SSL configuration
c.JupyterHub.ssl_key = '/home/data8/certs/server.key'
c.JupyterHub.ssl_cert = '/home/data8/certs/server.crt'

# Use docker spawner
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = 'jupyter-node'

# Persist workspaces
notebook_dir = '/home/jovyan/DS1EDP'
exchange_dir = '/var/exchange'
workspace_dir = '/home/jovyan'
c.DockerSpawner.notebook_dir = workspace_dir
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir, 'exchange':  exchange_dir}

# TU Berlin LDAP authenticator
c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.LDAPAuthenticator.server_address = 'ldap-slaves.tu-berlin.de'
c.LDAPAuthenticator.bind_dn_template = ['uid={username},ou=user,dc=tu-berlin,dc=de']
c.LDAPAuthenticator.lookup_dn = False
c.LDAPAuthenticator.use_ssl = True
c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'cn'
c.LDAPAuthenticator.user_search_base = 'ou=user,dc=tu-berlin,dc=de'
c.LDAPAuthenticator.user_attribute = 'sAMAccountName'
c.LDAPAuthenticator.escape_userdn = False

# User whitelist
c.Authenticator.admin_users = {'data8'}
c.Authenticator.username_map = {'boninho': 'data8', 'esmailoghli': 'data8', 'abedjan': 'data8', 'm.mahdavi': 'data8', 'hagenanuth': 'data8'}
# c.Authenticator.whitelist = {'mal', 'zoe', 'inara', 'kaylee'}

# Dummy Authenticator: Uncommed for testing only. Any Username/Password combination works
# c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'

# Automatically stop idle containers after 1 hour
c.JupyterHub.services = [
    {
        'name': 'cull-idle',
        'admin': True,
        'command': [sys.executable, 'cull_idle_servers.py', '--timeout=3600'],
    }
]
