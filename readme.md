# sign_in on Google Colab

```python
from google.colab import drive
drive.mount('/content/drive')

!mkdir -p '/content/drive/MyDrive/sign_in'
%cd '/content/drive/MyDrive/sign_in'

!if [ ! -d ".git" ]; then git clone https://github.com/lmj8133/sign_in.git .; else git pull; fi

!pip install flask flask_socketio eventlet

!if [ ! -f "cloudflared-linux-amd64.deb" ]; then wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb; fi

!sudo dpkg -i cloudflared-linux-amd64.deb

!python3 main.py
