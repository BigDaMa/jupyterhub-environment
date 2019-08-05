FROM jupyter/minimal-notebook:latest
ARG JUPYTERHUB_VERSION=1.0.0

USER jovyan
RUN pip install --no-cache \
    nbgitpuller

RUN git clone https://github.com/jupyter/nbgrader /home/jovyan/nbgrader
RUN pip install -r /home/jovyan/nbgrader/dev-requirements.txt -e /home/jovyan/nbgrader

RUN jupyter serverextension enable nbgitpuller --sys-prefix
RUN jupyter nbextension install --user --py nbgrader --overwrite
RUN jupyter nbextension enable --user --py nbgrader
RUN jupyter serverextension enable --user --py nbgrader
RUN jupyter nbextension disable --sys-prefix create_assignment/main
RUN jupyter nbextension disable --sys-prefix formgrader/main --section=tree
RUN jupyter serverextension disable --sys-prefix nbgrader.server_extensions.formgrader

USER root
RUN groupadd -g 1024 jupyter
RUN usermod -a -G jupyter jovyan

USER jovyan
RUN mkdir /home/jovyan/exchange
COPY nbgrader_config.py /home/jovyan/.jupyter/nbgrader_config.py

USER root
RUN chown jovyan:1024 /home/jovyan/.jupyter/nbgrader_config.py
RUN rm /usr/local/bin/start-notebook.sh
COPY start-notebook.sh /usr/local/bin/start-notebook.sh
