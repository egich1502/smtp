import socket
import ssl
import base64
import os


def request(socket, request):
    socket.send((request + '\n').encode())
    recv_data = socket.recv(65535).decode()
    return recv_data


def main(host, user, password, recipient):
    port = 465
    msg = ''
    boundry = '123mystring123'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host, port))
        client = ssl.wrap_socket(client)
        print(client.recv(1024))
        print(request(client, f'ehlo {user}'))

        base64login = base64.b64encode(user.encode()).decode()
        base64password = base64.b64encode(password.encode()).decode()

        print(request(client, 'AUTH LOGIN'))
        print(request(client, base64login))

        print(request(client, base64password))
        print(request(client, f'MAIL FROM: {user}@{host[5:]}'))
        print(request(client, f'RCPT TO: {recipient}'))
        print(request(client, 'DATA'))

        with open('messageHeaders.txt', 'r') as file:
            msg += file.read() + '\n'

        msg += 'MIME-Version: 1.0\n'
        msg += f'Content-Type: multipart/mixed; boundary={boundry}\n\n'

        with open('msg.txt', 'r') as file:
            msg += f'--{boundry}' + '\n' + 'Content-Type: text/plain' + '\n\n'
            msg += file.read() + '\n'

        for file in os.scandir('attachments'):
            with open(file, 'rb') as f:
                msg += f'--{boundry}' + '\n'
                msg += f'''Content-Disposition: attachment;
        filename="{f.name}"
    Content-Transfer-Encoding: base64
    Content-Type: application/octet-stream;
        name="{f.name}"''' + '\n\n'
                content = f.read()
                msg += base64.b64encode(content).decode() + '\n'

        msg += f'--{boundry}--'
        msg += '\n.\n'
        print(msg)
        print(request(client, msg))


if __name__ == '__main__':
    with open('inputData.txt', 'r') as file:
        host_address = file.readline()[:-1]
        login = file.readline()[:-1]
        password = file.readline()[:-1]
        recipient = file.readline()
    main(host_address, login, password, recipient)