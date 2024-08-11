
# FileSharingSystem_TechTitans

## Overview

This repository contains both the server and client applications built using Streamlit. The server is integrated with Firebase and allows you to upload files, send them to clients in specific groups, and manage file-sharing operations efficiently. The client application connects to the server to receive files, measure network bandwidth, and acknowledge receipt of the file.

## Setting up Firebase

### Firebase Setup

To set up Firebase and integrate it with the server, follow these steps:

1. **Create a Firebase Project:**

    - Log in to the [Firebase Console](https://console.firebase.google.com/) with your Google account.
    - Click on "Add Project" and enter a project name. Follow the on-screen instructions to set up the project.

2. **Setup Firestore Database:**

    - In the Firebase Console, go to the left-hand menu and select **Firestore Database** under the "Build" section.
    - Click on "Create Database" if you haven't set it up yet. Choose the appropriate security rules and proceed.

3. **Create Collections and Documents:**

    - Inside the Firestore Database, create a collection named `Groups`.
    - Add documents for each group (e.g., `Group1`, `Group2`).
    - Inside each group document, add a sub-collection named `clients`, and for each client, add fields such as `client_id`.

4. **Generate the Firebase Service Account Key:**

    - Go to the Project Settings by clicking the gear icon (⚙️) next to your project name in the Firebase Console.
    - Select **Service Accounts** and click on **Generate New Private Key**.
    - Confirm the generation by clicking **Generate Key**. The key will be downloaded as a JSON file. Keep this file secure.

5. **Add Firebase Admin SDK to Your Application:**

    - In your server code, initialize Firebase using the following snippet:

    ```python
    import firebase_admin
    from firebase_admin import credentials, firestore

    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        cred = credentials.Certificate('path/to/your/serviceAccountKey.json')
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'your-bucket-name.appspot.com'
        })

    # Initialize Firestore
    db = firestore.client()
    ```

    - Replace `'path/to/your/serviceAccountKey.json'` with the actual path to the JSON file you downloaded.

## Running the Server - ui_server.py

### How to Setup and Run the Server

### Prerequisites

Before you start, ensure you have the following installed:

- Python 3.x
- Streamlit
- Firebase Admin SDK
- Google Cloud Storage Client Library
- psutil library

1. **Clone the repository:**

    ```bash
    git clone https://github.com/TechTitans-TallyHackathon/FileSharingSystem_TechTitans.git
    cd FileSharingSystem_TechTitans
    ```

2. **Install the required Python libraries:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Streamlit application for the server:**

    ```bash
    streamlit run ui_server.py
    ```

4. **Upload Files and Send to Clients:**

    - Select the appropriate group from the dropdown in the UI.
    - Upload a file you wish to send to the clients.
    - Click the "Send File" button to start the file transfer process. The server will send the file to all clients in the selected group.

## Running the Client - ui_client.py

### How to Run the Code

### Prerequisites

Before you start, ensure you have the following installed:

- Python 3.x
- Streamlit
- psutil library

1. **Clone the repository:**

    ```bash
    git clone https://github.com/TechTitans-TallyHackathon/FileSharingSystem_TechTitans.git
    cd FileSharingSystem_TechTitans
    ```

2. **Install the required Python libraries:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Streamlit application:**

    ```bash
    streamlit run ui_client.py
    ```

4. **Enter the required details in the UI:**

    - **Server IP Address:** Enter the IP address of the server from which you want to receive the file.
    - **Server Port:** Specify the port number on which the server is listening.
    - **Client ID:** Input your unique client ID. Currently, this is directly entered into the UI, but it can be extended with a proper user ID and login system for authentication and identification.
    - **Network Interface:** Specify the network interface (e.g., Wi-Fi, eth0) to measure the network bandwidth.
    - **Bandwidth Measurement Duration:** Adjust the duration for measuring bandwidth.

5. **Click the "Receive File" button:** This will initiate the connection to the server, receive the file, and save it to your system.

6. **Acknowledgment:** After receiving the file, the client will reconnect to the server to send an acknowledgment message.

7. **Download the Received File:** The UI provides a download button to save the received file.

## Customizations and Future Enhancements

### Current Limitations

- **Changing Group Client Details:** Once a group has been created and clients have been added, changing the details of clients in a group can be cumbersome. This requires manual updates in Firebase or modifications in the code.

- **Sending Large Files:** The current implementation sends files in chunks of 64 KB, which might not be efficient for very large files. This can lead to performance issues or timeouts.

- **Resending Files:** Once all clients have received a file, you must change the file name before resending it. Otherwise, the system may encounter errors or fail to recognize the new file.

### Future Enhancements

- Implementing a more dynamic system for managing group client details.
- Optimizing file transfer for large files to avoid performance bottlenecks.
- Improving the resending mechanism to handle previously sent files more gracefully.

## Notes

- The client is designed to terminate after successfully receiving a file and sending an acknowledgment.
- Ensure that the server is correctly configured and running before attempting to connect with the client.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
