FROM python:3.12-slim

# Tk + X11 tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-tk x11-apps && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
ENV LIBGL_ALWAYS_INDIRECT=1

WORKDIR /app

# --- deps first (cache friendly) ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- app code ---
# if your file is named chat_gui_fastapi.py, rename to chat_gui.py inside the image
COPY chat_gui.py ./chat_gui.py

CMD ["python", "chat_gui.py"]
