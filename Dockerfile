FROM python:3.10

WORKDIR /app

# Installer les dépendances système pour OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgthread-2.0-0 \
    libgl1 \
    libglx0 \
    libegl1 \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Installer oemer sans ses dépendances (pour éviter le conflit numpy)
RUN pip install --no-cache-dir oemer

# Installer homr
RUN pip install --no-cache-dir homr

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV OPENCV_OPENCL_RUNTIME=
ENV OPENCV_OPENCL_DEVICE=:
ENV OPENCV_FFMPEG_CAPTURE_DEVICES=0

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
