import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage as gcs_storage
import google.auth
from google.oauth2 import service_account
import socket
import os
import struct
import psutil
import time
import threading

# Check if the Firebase app is already initialized
if not firebase_admin._apps:
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate('Tech Titans Firebase Service Account.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'tech-titans-329c8.appspot.com'
    })

# Initialize Firestore
db = firestore.client()

def get_groups():
    groups_ref = db.collection('Groups')
    docs = groups_ref.stream()
    groups = [doc.id for doc in docs]
    return groups

def upload_file_to_firebase(group, file):
    # Load the service account credentials from the JSON file
    credentials = service_account.Credentials.from_service_account_file(
        'Tech Titans Firebase Service Account.json'
    )
    
    # Create a Google Cloud Storage client with the credentials
    storage_client = gcs_storage.Client(credentials=credentials, project=credentials.project_id)
    
    # Access the bucket
    bucket = storage_client.bucket('tech-titans-329c8.appspot.com')
    blob = bucket.blob(f"{group}/{file.name}")
    
    # Upload the file
    blob.upload_from_string(file.getvalue(), content_type=file.type)
    
    # Return the public URL
    return blob.public_url


# Function to get the network bandwidth (in bytes per second)
def get_network_bandwidth(interface='en0', duration=1):
    net_info_start = psutil.net_io_counters(pernic=True)[interface]
    start_time = time.time()

    time.sleep(duration)

    net_info_end = psutil.net_io_counters(pernic=True)[interface]
    end_time = time.time()

    time_elapsed = end_time - start_time
    bytes_sent = net_info_end.bytes_sent - net_info_start.bytes_sent
    bytes_recv = net_info_end.bytes_recv - net_info_start.bytes_recv

    bandwidth_sent_bps = (bytes_sent / time_elapsed) * 8
    bandwidth_recv_bps = (bytes_recv / time_elapsed) * 8

    return {
        'bandwidth_sent_bps': bandwidth_sent_bps,
        'bandwidth_recv_bps': bandwidth_recv_bps
    }

def start_server(file_path, allowed_client_ids):
    # Server details
    server_address = ('0.0.0.0', 10000)  # Listen on all interfaces on port 10000

    # Create a TCP/IP socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(server_address)
    server_sock.listen(5)  # Listen for up to 5 incoming connections

    # File to send
    file_name = os.path.basename(file_path)

    print(f'Server is listening on {server_address[0]}:{server_address[1]}')

    # Track clients that have successfully received the file
    received_client_ids = set()

    try:
        while len(received_client_ids) < len(allowed_client_ids):
            print('Waiting for a connection...')
            connection, client_address = server_sock.accept()
            print(f'Connection from {client_address}')

            try:
                # Receive the client ID
                client_id_data = connection.recv(4)
                if not client_id_data:
                    print('No client ID received, closing connection')
                    connection.close()
                    continue
                
                client_id = struct.unpack('!I', client_id_data)[0]
                print(f'Received client ID: {client_id}')

                # Check if the client ID is allowed and hasn't already received the file
                if client_id in allowed_client_ids and client_id not in received_client_ids:
                    # Use a fixed chunk size for now
                    chunk_size = 64 * 1024  # 64 KB
                    print(f'Using fixed chunk size: {chunk_size} bytes')

                    # Send the file name first
                    file_name_encoded = file_name.encode()
                    file_name_length = len(file_name_encoded)
                    connection.sendall(struct.pack('!I', file_name_length))
                    connection.sendall(file_name_encoded)
                    print(f'Sent file name: {file_name}')

                    # Send the file data
                    with open(file_path, 'rb') as file:
                        while True:
                            chunk = file.read(chunk_size)
                            if not chunk:
                                break
                            connection.sendall(chunk)
                            print(f'Sent chunk of size {len(chunk)}')

                    print('File transfer complete. Closing connection.')
                    connection.close()

                    # Reopen connection to wait for acknowledgment
                    connection, client_address = server_sock.accept()
                    connection.settimeout(30)  # Set a timeout for receiving acknowledgment
                    print(f'Waiting for acknowledgment from {client_address}')

                    try:
                        ack_message = connection.recv(1024).decode()
                        expected_ack_message = f"ACK_{client_id}"
                        if ack_message == expected_ack_message:
                            print(f'Received acknowledgment from client ID {client_id}')
                            received_client_ids.add(client_id)  # Mark client as having received the file
                            print(f'Client ID {client_id} has been marked as completed.')
                        else:
                            print(f'Received incorrect acknowledgment: {ack_message}')
                    except socket.timeout:
                        print('Acknowledgment timeout. No response received.')

                else:
                    print(f'Client ID {client_id} is not allowed or has already received the file, closing connection.')
                    connection.close()

            finally:
                connection.close()
                print(f'Connection with {client_address} closed')

        print('All clients have received the file. Server shutting down.')

    finally:
        server_sock.close()


# Streamlit application
st.title("Server: File Sharing Tool")

# Select group
groups = get_groups()
if not groups:
    st.write("No groups available.")
else:
    group = st.selectbox("Select Group", groups)

    # Upload file (Support all file types by not specifying a type)
    uploaded_file = st.file_uploader("Choose a file")

    # Add or update client information
    if st.button("Send File"):
        if uploaded_file is not None:
            # Save the uploaded file temporarily
            temp_file_path = f"/tmp/{uploaded_file.name}"
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.getbuffer())

            # Upload file to Firebase
            file_url = upload_file_to_firebase(group, uploaded_file)
            
            # Update Firestore
            group_ref = db.collection('Groups').document(group)
            group_data = group_ref.get().to_dict()
            
            if 'client_id' in group_data:
                client_ids = group_data['client_id']
                
                for client_id in client_ids:
                    client_doc_ref = group_ref.collection('clients').document(str(client_id))
                    client_doc_ref.set({
                        'file_url': file_url,
                        'file_name': uploaded_file.name
                    })
                
                # Optionally update the group document with the latest file
                group_ref.update({
                    'latest_file': file_url,
                    'filename': uploaded_file.name
                })
                
                # Start the server in a separate thread
                threading.Thread(target=start_server, args=(temp_file_path, client_ids)).start()
                
                st.success("File sent successfully and server started!")
