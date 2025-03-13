# How to Run the Project on Google Colab

Follow these steps to set up and run the project:

1. **Open a New Colab Notebook:**  
   Go to [Google Colab](https://colab.research.google.com/) and create a new Python notebook.

2. **Run the Following Code in a New Cell:**  
   Copy and paste the code below into a cell, then run the cell. This code will:
   - Mount your Google Drive.
   - Create (if necessary) and switch to the target directory.
   - Clone the repository (or pull the latest changes if it already exists).
   - Install the required Python packages.
   - Download and install the Cloudflare Tunnel package if it isn't already present.
   - Start the application.

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

3. **Access the Application via the Tunnel:**  
   After the above cell runs, a Cloudflare Tunnel link will be provided.
  
   Click the link below to open the tunnel and access the application's frontend.
   
   ![img](https://github.com/lmj8133/sign_in/blob/master/cloudflared_tunnel_link.png)
   
# Troubleshooting
   - **Google Drive Mounting Issues:**
   
     Ensure you are logged into your Google account and have granted Colab permission to access your Drive.
   - **Repository Issues:**
   
     If cloning fails, double-check your internet connection or manually update the repository.
   - **Cloudflare Tunnel Issues:**
    
     Verify that the `.deb` file is downloaded correctly. Re-run the cell if necessary.
    
Enjoy using the project!
