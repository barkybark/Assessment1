# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성(필요하면 추가)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# 파이썬 패키지 복사 및 설치
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# 앱 소스 복사
COPY . /app

# 스트림릿이 쓸 포트
EXPOSE 8501

# 컨테이너 시작 시 실행 커맨드
CMD ["streamlit", "run", "Assessment1.py", "--server.port=8501", "--server.address=0.0.0.0"]