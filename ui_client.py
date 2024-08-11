import streamlit as st
import socket
import struct
import psutil
import time
import os

# Function to get the network bandwidth (in bytes per second)
def get_network_bandwidth(interface='Wi-Fi', duration=1):
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

# Streamlit UI

st.title("File Receiver Client")

server_ip = st.text_input("Server IP Address", "192.168.240.188")
server_port = st.number_input("Server Port", value=10000)
client_id = st.number_input("Client ID", value=5)
network_interface = st.text_input("Network Interface", "Wi-Fi")
duration = st.slider("Bandwidth Measurement Duration (seconds)", min_value=1, max_value=5, value=1)
receive_button = st.button("Receive File")

if receive_button:
    try:
        # Server details
        server_address = (server_ip, server_port)

        # First connection to receive the file
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect(server_address)
        st.write(f'Connected to server at {server_address[0]}:{server_address[1]}')

        # Send the client ID
        client_sock.sendall(struct.pack('!I', client_id))
        st.write(f'Sent client ID: {client_id}')

        # Receive the file name
        file_name_length_data = client_sock.recv(4)
        if not file_name_length_data:
            raise ValueError("Failed to receive file name length")

        file_name_length = struct.unpack('!I', file_name_length_data)[0]
        file_name = client_sock.recv(file_name_length).decode()
        st.write(f'Received file name: {file_name}')

        # Measure the available bandwidth
        bandwidth_info = get_network_bandwidth(interface=network_interface, duration=duration)
        download_bandwidth_bps = bandwidth_info['bandwidth_recv_bps']

        # Calculate chunk size based on bandwidth (targeting a 1-second transfer per chunk)
        chunk_size = min(int(download_bandwidth_bps / 8), 64 * 1024)  # Cap chunk size to 64 KB max
        st.write(f'Calculated chunk size: {chunk_size} bytes')

        # Save the file with the received name
        received_file_path = os.path.abspath(f'received_{file_name}')

        with open(received_file_path, 'wb') as file:
            while True:
                data = client_sock.recv(chunk_size)
                if not data:
                    # If no more data is received, break the loop
                    break
                file.write(data)
                st.write(f'Received chunk of size {len(data)}')

        st.success(f'File transfer complete. File saved as: {received_file_path}')

        # Close the connection after receiving the file
        client_sock.close()

        # Reconnect to send acknowledgment
        ack_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ack_sock.connect(server_address)
        st.write(f'Reconnected to server at {server_address[0]}:{server_address[1]} for acknowledgment')

        # Send acknowledgment
        ack_message = f"ACK_{client_id}"
        ack_sock.sendall(ack_message.encode())
        st.write(f'Sent acknowledgment: {ack_message}')

        ack_sock.close()

        # Provide a download button to save the received file
        with open(received_file_path, 'rb') as file:
            st.download_button(
                label="Download Received File",
                data=file,
                file_name=os.path.basename(received_file_path),
                mime='application/octet-stream'
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Terminate after receiving the file once and sending acknowledgment
st.write("Client terminated after receiving the file and sending acknowledgment.")
