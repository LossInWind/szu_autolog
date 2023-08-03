import requests
import socket
import json
import configparser
import PySimpleGUI as sg

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def get_local_ip():
    try:
        # 获取本地主机名
        host_name = socket.gethostname()

        # 获取本地IP地址
        local_ip = socket.gethostbyname(host_name)
        return local_ip
    except socket.error as e:
        print("获取本地IP地址失败:", e)
        return None

def is_internet_connected():
    try:
        # 使用百度作为一个简单的测试URL
        response = requests.get("http://www.baidu.com", timeout=5)
        return True if response.status_code == 200 else False
    except requests.exceptions.RequestException:
        return False

def login_campus(username, password):
    # 获取本地IP地址
    local_ip = get_local_ip()
    if not local_ip:
        print("无法获取本地IP地址。登录失败。")
        return

    # 登录校园网的URL
    login_url = "http://172.30.255.42:801/eportal/portal/login"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "DNT": "1",
        "Host": "172.30.255.42:801",  # 请求的目标主机
        "Referer": "http://172.30.255.42/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
    }

    # 构建GET请求的参数
    params = {
        "callback": "dr1003",
        "login_method": "1",
        "user_account": username,
        "user_password": password,
        "wlan_user_ip": local_ip,  # 使用获取到的本地IP地址作为参数
        "wlan_user_ipv6": "",
        "wlan_user_mac": "000000000000",
        "wlan_ac_ip": "172.30.255.41",
        "wlan_ac_name": "",
        "jsVersion": "4.1.3",
        "terminal_type": "1",
        "lang": "zh-cn",
        "v": "2573",
    }

    try:
        # 发送GET请求来登录
        response = requests.get(login_url, headers=headers, params=params)

        #print(response.text)

        # 修改登录成功的判断逻辑
        if "result" in response.text and "msg" in response.text:
            json_response = response.text.split("(", 1)[1].rsplit(")", 1)[0]
            data = json.loads(json_response)

            if data["result"] == 1 and data["msg"] == "Portal协议认证成功！":
                print("登录成功！")
                if is_internet_connected():
                    print("已成功联网！")
                else:
                    print("未能联网。")
            elif data["result"] == 0 and data["msg"] == "IP: 172.29.20.95 已经在线！" and data["ret_code"] == 2:
                print("已经在线")
            else:
                print("登录失败，请检查用户名和密码。")
        else:
            print("登录失败，请检查用户名和密码。")
    except requests.exceptions.RequestException as e:
        print("登录失败:", e)


def main():
    # Read or create the configuration file
    config = read_config()

    # Check if username and password are already saved in the config file
    if 'Credentials' in config:
        username = config['Credentials']['username']
        password = config['Credentials']['password']
    else:
        # If not, create a simple GUI to ask for the username and password
        layout = [
            [sg.Text('Username:'), sg.InputText(key='username')],
            [sg.Text('Password:'), sg.InputText(key='password', password_char='*')],
            [sg.Button('OK')]
        ]

        window = sg.Window('Login', layout)

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'OK':
                break

        window.close()

        username = values['username']
        password = values['password']

        # Save the username and password to the config file
        config['Credentials'] = {'username': username, 'password': password}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    # Call the login function with the saved username and password
    login_campus(username, password)
    # Pause the execution to keep the console window open after the .exe finishes running
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()





