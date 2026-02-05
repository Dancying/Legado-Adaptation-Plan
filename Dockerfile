FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai \
    GUNICORN_THREADS=8 \
    BASE_URL="https://api.dancying.cn" \
    API_PREFIX="/legado" \
    PORT=39966

WORKDIR /novel

RUN export DEBIAN_FRONTEND=noninteractive && \
    sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources || \
    (echo "deb https://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
     echo "deb https://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list) && \
    apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    xvfb \
    xauth \
    fonts-wqy-zenhei && \
    wget -q -O microsoft-edge-stable.deb https://packages.microsoft.com/repos/edge/pool/main/m/microsoft-edge-stable/microsoft-edge-stable_131.0.2903.112-1_amd64.deb && \
    (dpkg -i microsoft-edge-stable.deb || apt-get install -f -y) && \
    useradd -m -s /bin/bash novel && \
    rm microsoft-edge-stable.deb && \
    rm -rf /var/lib/apt/lists/*

COPY --chown=novel:novel requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.ustc.edu.cn/pypi/web/simple -r requirements.txt && \
    find /usr/local -depth -name '__pycache__' -exec rm -rf {} ';'

COPY --chown=novel:novel . .
RUN chown -R novel:novel /novel

USER novel

EXPOSE $PORT

CMD ["sh", "-c", "exec gunicorn main:app -b 0.0.0.0:$PORT --workers 1 --threads $GUNICORN_THREADS --worker-class gthread"]
