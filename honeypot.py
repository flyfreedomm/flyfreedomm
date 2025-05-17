import socket
import threading
import time
import logging
from datetime import datetime

class SimpleHoneypot:
    def __init__(self, ports=[21, 22, 23, 80, 443, 3389], log_file="honeypot.log"):
        self.ports = ports
        self.servers = []
        self.log_file = log_file
        self.setup_logging()
        
    def setup_logging(self):
        """配置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("honeypot")
        
    def handle_connection(self, client_socket, client_address, port):
        """处理客户端连接"""
        try:
            # 记录连接信息
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.logger.info(f"连接尝试 - 来源: {client_address[0]}:{client_address[1]}, 目标端口: {port}")
            
            # 模拟服务响应
            if port == 22:  # SSH
                client_socket.send(b"SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.8\r\n")
            elif port == 80:  # HTTP
                client_socket.send(b"HTTP/1.1 404 Not Found\r\nServer: Apache\r\n\r\n")
            elif port == 21:  # FTP
                client_socket.send(b"220 Welcome to the FTP server\r\n")
            
            # 保持连接一段时间，模拟真实服务
            time.sleep(2)
            
        except Exception as e:
            self.logger.error(f"处理连接时出错: {str(e)}")
        finally:
            # 关闭连接
            client_socket.close()
    
    def start_server(self, port):
        """启动单个端口的服务器"""
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', port))
            server.listen(5)
            self.logger.info(f"在端口 {port} 上启动蜜罐服务")
            
            while True:
                client_socket, client_address = server.accept()
                # 为每个连接创建一个新线程
                client_handler = threading.Thread(
                    target=self.handle_connection,
                    args=(client_socket, client_address, port)
                )
                client_handler.daemon = True
                client_handler.start()
                
        except Exception as e:
            self.logger.error(f"在端口 {port} 启动服务时出错: {str(e)}")
    
    def start(self):
        """启动所有端口的蜜罐服务"""
        self.logger.info("启动蜜罐服务...")
        for port in self.ports:
            server_thread = threading.Thread(target=self.start_server, args=(port,))
            server_thread.daemon = True
            server_thread.start()
            self.servers.append(server_thread)
        
        # 保持主线程运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("蜜罐服务已停止")

if __name__ == "__main__":
    # 创建并启动蜜罐
    honeypot = SimpleHoneypot()
    honeypot.start()    