# BigDaMa - DS1EDP - JupyterHub infrastructure
## 1 - Requirements

The following software is required:

1. [Docker](https://www.docker.com/)
1. [JupyterHub](https://jupyter.org/hub)
1. [Python 3](https://www.python.org/)

*Note:* Sudo permissions may be required at some points.

## 2 - Architecture

![alt text][architectureDiagram]

#### JupyterHub
The JupyterHub is the central component of thi architecture. The hub authenticates users with the **TUBIT LDAP** authentication service. In order to log in to the hub, stundents not only have to be authenticated by the LDAP service, they also need to be mentioned in the authentication whitelist. As soon as a user is successfully authenticated, the hub spawns a new Docker container, that runs a Jupyter Notebook server.

#### Docker containers
Every Jupyter Notebook server is started within an isolated and unique docker container. Thus, every user has its own docker container. These containers can be started and stopped dynamically, hence only the containers of users that are cuurently active have to be running concurrently. The docker image that is used in this setup is based on the Jupyter Notebook minimal image and was customized in order to enable nbgrader functionality.

#### Persistent workspaces
A dedicated volume is created for every container (user). This allows to persist the users workspaces event if the container is delted (e.g. if the image of the container has to be updated). These volumes are mounted to the docker container on startup.

#### Shared nbgrader exchange volume
The nbgrader extension that we use to create, distribute, collect and grade assignments requires a shared exchange directory. In contrast to the persistent workspace volumes, this volume is shared by all users and therefore mounted to every container.

#### Git repository
The course material is managed in a Git repository. The **nbgitpuller** tool allows us to synchronize the persistent workspaces with our git repository and distribute new course materials.


## 3 - Configuration

### JupyterHub
The JupyterHub is configured via *jupyterhub_config.py*.

#### General configuration

| Field | Description |
|---|---|
| `c.JupyterHub.ip` | Has to match the server domain/ip. Students will access the hub via this domain |
| `c.JupyterHub.port` | The port to use with the ip/domain. Should be `443` as we use https. Make sure the port is exposed |
| `c.JupyterHub.hub_ip` | This should also match the server ip. The spawned notebook servers will use this endpoint to communicate with the hub |
| `c.JupyterHub.hub_port` | E.g. 8081. This port is used for notebook and hub communication |
| `c.JupyterHub.ssl_key` | Location of the ssl key. Required for HTTPS communication |
| `c.JupyterHub.ssl_cert` | Location of the ssl cert. Required for HTTPS communication |

#### Spawner and container configuration
| Field | Description |
|---|---|
| `c.JupyterHub.spawner_class` | The desired [spawner](https://jupyterhub.readthedocs.io/en/stable/reference/spawners.html). In our case this has to be `'dockerspawner.DockerSpawner'`. Make sure that dockerspawner is installed via pip |
| `c.DockerSpawner.image` | As we want to use a customized docker image, we have to provide the name. Mind that the image has to be available in the remote/local registry |
| `c.Spawner.mem_limit` | The memory limit for every container. The value can either be an integer (bytes) or a string with a 'K', 'M', 'G' or 'T' prefix. |
| `notebook_dir` | We store the path of the jupyter servers workspace in this variable (inside container). This directory will be persisted. We use a [minimal image](https://github.com/jupyter/docker-stacks/tree/master/minimal-notebook) provided by the jupyter project, which comes with the default user **jovyan**. Thus, we set this variable to `/home/jovyan` |
| `exchange_dir` | This variable should contain the path to the nbgrader exchange directory (shared by all users). The persistent exchange directory will be mounted to this path. This path should match the configured `c.Exchange.root` in the `nbgrader_config.py`. We will use `/home/jovyan/.exchange` here |
| `c.DockerSpawner.notebook_dir` | The entrypoint for the notebook server. Should match the mounted persistent directory. Thus it has to be `notebook_dir`, that we declared earlier |
| `c.DockerSpawner.volumes` | The persistent volumes that we want to mount on the container. There is the users workspace and the shared excahnge directory. Set this to `{ 'jupyterhub-user-{username}': notebook_dir, 'exchange':  exchange_dir}`. On the server, the persistent user workspace will be created at `/var/lib/docker/volumes/jupyterhub-user-{username}` (while `{username}` is the TUBIT ID). The exchange directory can be found at `/var/lib/docker/volumes/exchange` accordingly |

#### Authentication
| Field | Description |
|---|---|
| `c.JupyterHub.authenticator_class` | The desired [authenticator](https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html). In our case this has to be `'ldapauthenticator.LDAPAuthenticator'`. Make sure to install it via pip |
| `c.Authenticator.admin_users` | A list with all user IDs, that should get access to the JupyterHub admin panel. E.g. `{'data8'}` |
| `c.Authenticator.username_map` | Map specific IDs. We use this to redirect all instructor user IDs to a single admin account. E.g. `{'boninho': 'data8', 'esmailoghli': 'data8', 'abedjan': 'data8', 'm.mahdavi': 'data8', 'hagenanuth': 'data8'}` |
| `c.Authenticator.whitelist` | A whitelist for users. If this list is not provided, every user that is authenticated by the authenticator (e.g. every TUBIT user) can access the hub. If provided, only the mentioned user IDs can access the hub. E.g. `{'stundent1', 'student2'}` |

**Note:** For more information on the usermanagement, whitelists, etc. refer to the [JupyterHub authenticator docs](https://jupyterhub.readthedocs.io/en/stable/getting-started/authenticators-users-basics.html)

**Note:** In order to use the TUBIT LDAP service for authentication, the following configurations can be used

	c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
	c.LDAPAuthenticator.server_address = 'ldap-slaves.tu-berlin.de'
	c.LDAPAuthenticator.bind_dn_template = ['uid={username},ou=user,dc=tu-berlin,dc=de']
	c.LDAPAuthenticator.lookup_dn = False
	c.LDAPAuthenticator.use_ssl = True
	c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'cn'
	c.LDAPAuthenticator.user_search_base = 'ou=user,dc=tu-berlin,dc=de'
	c.LDAPAuthenticator.user_attribute = 'sAMAccountName'
	c.LDAPAuthenticator.escape_userdn = False

**DummyAuthenticator:** For testing use (not for production!), the [DummyAuthenticator](https://github.com/jupyterhub/dummyauthenticator) can be used. This Authenticator accepts all username/password combinations. Just uncomment the last line of the **jupyterhub_config.py**.

#### cull-idle

The service `cull-idle` stops idle containers after the configured time. E.g: `--timeout=3600` stops idle instances after 1 hour. Refer to the [cull-idle docs](https://github.com/jupyterhub/jupyterhub/tree/master/examples/cull-idle) for further information.

### Docker

In order to provide **nbgrader** and **nbgitpuller** support, a customized docker image is necessary.

The docker image is based on the [minimal-notebook](https://github.com/jupyter/docker-stacks/tree/master/minimal-notebook) image. It further installs and enables the nbgitpuller tool and the nbgrader extension.

The latest stable version of nbgrader is currently v.0.5.5, but in our case it is important to install version >= v.0.6.0, because earlier versions would choose the system username **jovyan** instead of the actual JupyterHub username (which is the TUBIT ID) as student id. Currently v.0.6.0 has to be installed from the github sources.

It also creates the directory `/home/jovyan/.exchange` which is the mounting point of the shared exchange directory. A nbgrader configuration is copied to `/home/jovyan/.jupyter`, this file is further explained in the following section.

Last but not least, python libraries are installed that can be used within notenooks. Currently `numpy` and `datascience` are installed. Further libraries can be added by simply extending the list.

### NbGrader

The `nbgrader_config.py` file includes some basic configurations for the nbgrader extension.

| Field | Description |
|---|---|
| `c.CourseDirectory.course_id` | The ID of the nbgrader course. E.g. `'ds1edp_ws19'` |
| `c.Exchange.root` | The path to the shared nbgrader directory. Must match the `exchange_dir` variable in `jupyterhub_config.py`. E.g. `'/home/jovyan/.exchange'` |
| `c.CourseDirectory.root` | This variable is relevant for the instructors (where formgrader is available). It should contain the location of the actual nbgrader course. E.g. `/home/jovyan/ds1edp_ws19`. It should be a subdirectory of the persisted workspace of the admin user, so the course data will be persisted |

### NbGitPuller

Share a nbgitpuller link with the students. Via this link, the specified git repository is clone to the students container. The repositories are located at `/home/jovyan`, thus all the changes by students are persisted on their containers persistent volume. The nbgitpuller prevents most of the possible merge conflicts that could occur. 

**Note:** Best practice would be to ask the students to click on a nbgitpuller link when they log in for the first time. On this way, the students already have the repository cloned when they first use the hub. This will reduce confusion.

If you want to share a new repository with the students, just share a new nbgitpuller link. NbGitPuller links can be generated [here](https://jupyterhub.github.io/nbgitpuller/link.html).

## 4 - Installation

**1. Install python and pip (>=python3.5)**

**2. Install docker**

**3. Install npm**

**4. Install neccessary libs**

	pip install jupyterhub dockerspawner jupyterhub-ldapauthenticator jupyterhub-dummyauthenticator
	
**5. Install http-proxy**

	npm install -g configurable-http-proxy

**6. Clone git repository** (assuming $WORKSPACE is the path where jupyterhub should be installed)

	cd $WORKSPACE
	git clone https://github.com/BigDaMa/JupyterHub_environment

**7. Edit jupyterhub_conf.sh** (Insert IP, SSL-certificate location and user whitelist)

	vi ${WORKSPACE}/JupyterHub_environment/src/jupyterhub_config.py

**8. Build docker image** (Note: The tag should equal the `c.DockerSpawner.image` configuration in `jupyterhub_config.py`)

	cd ${WORKSPACE}/JupyterHub_environment/src
	docker build -t jupyter-node .

**9. Start jupyterhub**
	
	cd ${WORKSPACE}/JupyterHub_environment/src
	jupyterhub

**11. Activate extensions for admin**
- Log in to JupyterHub as **admin** - Students containers should **not** activate the extensions
- Open the terminal (New > Terminal)


	jupyter nbextension enable --user create_assignment/main
	jupyter nbextension enable --user formgrader/main --section=tree
	jupyter serverextension enable --user nbgrader.server_extensions.formgrader


- The formgrader might not work right away and show a 404 instead. Just restart the container and you should be good to go.

**10. Create nbgrader course** (If there is no nbgrader course created yet)
- Log in to JupyterHub as admin
- Open the terminal (New > Terminal)

	
	cd /home/jovyan
	nbgrader quickstart ds1edp_ws19

Note: `ds1edp_ws19` is the course id. It has to match `c.CourseDirectory.course_id` and `c.CourseDirectory.root` in `nbgrader_config.py`.

## 5. Operation

### Current installation on data8 server

- The installation is currently located at `/home/data8/anaconda3/envs/ds1edp_ws19/JupyterHub_environment`
- JupyterHub is running in a detached [screen](https://www.gnu.org/software/screen/manual/screen.html), use `screen -r ${SCREEN_NAME}` to access the screen that is running the JupyterHub
- Also make sure to activate the conda environment, that was created for this scenario by using `conda activate ds1edp_ws19`
- The persistent volumes for the docker containers can be found at `/var/lib/docker/volumes`
- The current server's IP is `130.149.21.99`
- The location of the SSL certificates is `/home/data8/anaconda3/envs/ds1edp_ws19/certs`

### Delete a user

1. Remove user from whitelist (edit `c.Authenticator.whitelist` in `${WORKSPACE}/JupyterHub_environment/src/jupyterhub_config.py`)
2. Remove user from JupyterHub:
	- Log in as admin
	- Control Panel > Admin > delete user
3. Delete persistent volume from `/var/lib/docker/volumes` (optional)

### Move to a new server

1. Copy persistent volumes from old server (usually at `/var/lib/docker/volumes`)
2. Setup the new server and install JupyterHub as described in **4.**
3. Before you log in for the first time, copy the persistent volumes to the new server (again usually to `/var/lib/docker/volumes`)
4. Log in to JupyterHub and the workspace from the old server should be loaded

[architectureDiagram]: ./resources/JupyterHub2.png "Architecture diagram"