# FileSharingSystem_TechTitans


# File Receiver Client - Streamlit Interface

## Overview

This repository contains a simple file receiver client application built using Streamlit. The client connects to a server to receive files, measure network bandwidth, and acknowledge receipt of the file.

## How to Run the Code

### Prerequisites

Before you start, ensure you have the following installed:

- Python 3.x
- Streamlit
- psutil library

### Setup Steps

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

### Customizations and Future Enhancements

- **Client ID and Authentication:** Currently, the client ID is manually inputted. This can be extended by implementing a user ID and login system for proper authentication and identification.

- **Automated IP Address and Port Configuration:** The server IP address and port need to be manually entered in the UI. This can be enhanced by automating the detection of the server's IP address and port configuration.

- **Network Interface Selection:** The network interface is also manually set. It can be automated by detecting the active interface or allowing the user to select from a list of available interfaces.

## Notes

- The client is designed to terminate after successfully receiving a file and sending an acknowledgment.
- Ensure that the server is correctly configured and running before attempting to connect with the client.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
