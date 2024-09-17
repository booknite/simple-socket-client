import socket
import ssl
import sys

# Input for domain and protocol/port combination
domain = input("Enter a domain name (e.g., www.google.com): ")
protocol_or_port = input("Enter the protocol or port (e.g., HTTP, HTTPS, 80, 443): ").strip().lower()

# Accept inputs as string or int
if protocol_or_port == "http" or protocol_or_port == "80":
    protocol = "HTTP"
    port = 80
    print("Using HTTP (port 80, no encryption).")
elif protocol_or_port == "https" or protocol_or_port == "443":
    protocol = "HTTPS"
    port = 443
    print("Using HTTPS (port 443, SSL encryption).")
else:
    print("Invalid protocol or port. Please enter 'HTTP', 'HTTPS', '80', or '443'.")
    sys.exit()

# Input for number of characters to display from the HTTP body
body_length = int(input("HTTP body character display count (e.g., 500): "))

# Try to resolve the host IP and connect
try:
    # Socket using IPv4 and TCP 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # If HTTPS is selected, wrap the socket with SSL for secure communication
    if protocol == "HTTPS":
        context = ssl.create_default_context()  # Create SSL context
        s = context.wrap_socket(s, server_hostname=domain)  # Wrap socket with SSL for HTTPS 
    s.settimeout(5)  # Set a timeout in case the server is slow or unresponsive

    print('Socket successfully created!')
    host_ip = socket.gethostbyname(domain)  # Resolve the domain name to an IP address
    s.connect((host_ip, port))  # Connect to the server at the resolved IP and port
    print(f"Socket has successfully connected to {domain} on port {port} ({host_ip})")

except socket.gaierror:
    print(f'Error resolving the host {domain}')
    sys.exit()  
except socket.timeout:
    print("Connection timed out.")
    sys.exit()  
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit()  

# Send HTTP GET request
request = f"GET / HTTP/1.1\r\nHost: {domain}\r\nConnection: close\r\n\r\n"  # Basic HTTP GET request
s.send(request.encode())  # Send the request encoded as bytes

# Receive and print response
buffer_size = 4000  
response = b""  # Empty byte string to store the server's response

try:
    while True:
        data = s.recv(buffer_size)  # Receive data in chunks
        if not data:
            break  
        response += data  # Append data to the response

except socket.timeout:
    print("Timed out while waiting for a response.")
except Exception as e:
    print(f"An error occurred while receiving data: {e}")

# Split headers and body
try:
    # HTTP response headers and body are separated by two newlines: \r\n\r\n.
    # Split the response using b"\r\n\r\n" to separate the headers from the body.
    header_data, body_data = response.split(b"\r\n\r\n", 1)
    headers = header_data.decode()  # Decode headers from bytes to string (UTF-8)

    print("\nHTTP Headers:")
    print(headers)  # Print the headers

    # Print x-number of characters from the body
    if "Content-Type" in headers and "text" in headers:
        print(f"\nHTTP Body (First {body_length} characters):")
        print(body_data[:body_length].decode(errors='ignore'))  # Ignore decoding errors
    else:
        print("Binary Data in Body:")
        print(f"Received binary data of length {len(body_data)} bytes.")

except UnicodeDecodeError:
    print("Received data could not be decoded as UTF-8.")
except ValueError:
    print("Could not separate headers from body.")

s.close()

