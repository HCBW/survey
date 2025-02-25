import paramiko
import os
from datetime import datetime

def download_db_from_server():
    # SSH连接信息
    hostname = "54.193.24.67"  # Remove http:// prefix and port number for SSH connections
    username = "ec2-user"
    key_filename = "/Users/haochengwang/desktop/survey/survey.pem"  # 如果使用密钥认证
    
    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, key_filename=key_filename)
    
    # 创建SFTP客户端
    sftp = ssh.open_sftp()
    
    # 下载文件
    remote_path = '/home/ec2-user/survey/survey_responses.db'
    local_path = f'survey_responses_{datetime.now().strftime("%Y%m%d")}.db'
    sftp.get(remote_path, local_path)
    
    # 关闭连接
    sftp.close()
    ssh.close()
    
    print(f"Database downloaded to {local_path}")

if __name__ == "__main__":
    download_db_from_server() 