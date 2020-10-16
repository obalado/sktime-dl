FROM tensorflow/tensorflow:2.3.1-gpu-jupyter
RUN pip install Cython
COPY build_tools/requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /usr/src/app
COPY sktime_dl sktime_dl
CMD ["bash", "-c", "source /etc/bash.bashrc && jupyter lab --notebook-dir=/usr/src/app --ip 0.0.0.0 --no-browser --allow-root"]
