FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-devel

# Arguments to build Docker Image using CUDA
ARG USE_CUDA=0
ARG TORCH_ARCH=

ENV AM_I_DOCKER True
ENV BUILD_WITH_CUDA "${USE_CUDA}"
ENV TORCH_CUDA_ARCH_LIST "${TORCH_ARCH}"
ENV CUDA_HOME /usr/local/cuda-11.6/

RUN apt-get update && apt-get install --no-install-recommends wget unzip ffmpeg=7:* \
    libsm6=2:* libxext6=2:* git=1:* nano=2.* \
    vim=2:* -y \
    && apt-get clean && apt-get autoremove && rm -rf /var/lib/apt/lists/*

# Install build-essential
RUN apt-get update && apt-get install -y build-essential

WORKDIR /home/appuser

# Install tokenizers before transformers
RUN python -m pip install --no-cache-dir tokenizers
RUN python -m pip install --no-cache-dir fastapi==0.65.2 
RUN python -m pip install --no-cache-dir uvicorn==0.15.0
RUN python -m pip install --no-cache-dir werkzeug==2.0.1 
RUN python -m pip install --no-cache-dir regex==2021.4.4 
RUN python -m pip install --no-cache-dir torch==2.0.1 
RUN python -m pip install --no-cache-dir pyngrok==5.0.5 
RUN python -m pip install --no-cache-dir timm==0.4.12 


# Add Rust compiler
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

RUN python -m pip install --upgrade pip

# Now add your Python dependencies
RUN pip install transformers==4.15.0


RUN python -m pip install --no-cache-dir transformers==4.15.0 
RUN python -m pip install --no-cache-dir fairscale==0.4.4 
RUN python -m pip install --no-cache-dir pycocoevalcap 
RUN python -m pip install --no-cache-dir torch torchvision Pillow scipy
RUN python -m pip install --no-cache-dir git+https://github.com/openai/CLIP.git numpy
RUN python -m pip install --no-cache-dir opencv-python-headless

RUN wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip \
    && unzip ngrok-stable-linux-amd64.zip \
    && rm ngrok-stable-linux-amd64.zip

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

