# How to Run the Project on Google Colab

Follow these easy steps to set up and run the project on Google Colab. No coding experience required.

---

## Step 1: Open a New Colab Notebook

- Visit [Google Colab](https://colab.research.google.com/).
- Click on "New Notebook" and ensure you are using the **Python 3** environment.

---

## Step 2: Run the Project Setup Code

Copy and paste the following code block into a single cell in your Colab notebook:

```python
# Download and install Cloudflare Tunnel
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
!sudo dpkg -i cloudflared-linux-amd64.deb

# Mount your Google Drive (you'll need to authorize access)
from google.colab import drive
drive.mount('/content/drive')

# Create and switch to the sign_in directory
!mkdir -p '/content/drive/MyDrive/sign_in'
%cd '/content/drive/MyDrive/sign_in'

# Clone or update the repository
!if [ ! -d ".git" ]; then git clone https://github.com/lmj8133/sign_in.git .; else git pull; fi

# Install required Python packages
!pip install flask flask_socketio eventlet

# Start the application
!python3 main.py
```

- After pasting the code, click the "Run" button on the left side of the cell to execute.

- Execution may take a few minutes, displaying many messages, which is normal.

---

## Step 3: Accessing the Application

After the code finishes executing successfully, you'll see a public URL starting with `https://` provided by Cloudflare Tunnel in the output.  

Click the URL to open the web interface of your application.

The generated URL should look something like this (example only):

![Cloudflare Tunnel Example Link](https://github.com/lmj8133/sign_in/blob/master/cloudflared_tunnel_link.png)

---

## Troubleshooting

- **Issue mounting Google Drive:**
  - Ensure you're logged into your Google account.
  - Allow Colab the permissions to access your Google Drive.

- **Problems cloning or updating repository:**  
  - Check your internet connection and retry by re-running the code.

- **Cloudflare Tunnel URL is not generated:**  
  - Check execution logs for errors and try running the code cell again.
  - If the issue persists, consider restarting the notebook and repeating the setup process.

