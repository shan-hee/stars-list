import os
import requests
import json
import time
from datetime import datetime

# GitHub API 相关信息
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")
OUTPUT_FILE = "README.md"

def get_starred_repos():
    """获取用户的所有star项目"""
    all_stars = []
    page = 1
    
    while True:
        url = f"https://api.github.com/users/{GITHUB_USERNAME}/starred?page={page}&per_page=100"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {GITHUB_TOKEN}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"获取starred仓库失败: {response.status_code}")
            print(response.text)
            break
            
        repos = response.json()
        if not repos:
            break
            
        all_stars.extend(repos)
        page += 1
        
        # 避免触发GitHub API速率限制
        time.sleep(1)
    
    return all_stars

def generate_stars_list(starred_repos):
    """生成格式化的stars列表"""
    content = "# 我的GitHub Stars\n\n"
    content += f"*最后更新于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    content += "| 项目名 | About |\n"
    content += "| ------ | ----- |\n"
    
    for repo in starred_repos:
        name = repo["full_name"]
        about = repo["description"] or "无描述"
        about = about.replace("\n", " ").replace("|", "\\|")  # 处理markdown表格中的特殊字符
        content += f"| [{name}]({repo['html_url']}) | {about} |\n"
    
    return content

def update_readme(content):
    """更新README.md文件"""
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{OUTPUT_FILE}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    
    # 检查是否已存在README文件
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # 文件存在，更新它
        file_data = response.json()
        update_data = {
            "message": "自动更新GitHub Stars列表",
            "content": content.encode("utf-8").hex(),
            "sha": file_data["sha"]
        }
        response = requests.put(url, headers=headers, data=json.dumps(update_data))
    else:
        # 文件不存在，创建它
        create_data = {
            "message": "创建GitHub Stars列表",
            "content": content.encode("utf-8").hex()
        }
        response = requests.put(url, headers=headers, data=json.dumps(create_data))
    
    if response.status_code not in [200, 201]:
        print(f"更新README失败: {response.status_code}")
        print(response.text)
    else:
        print("README更新成功!")

def main():
    """主函数"""
    if not GITHUB_USERNAME or not GITHUB_TOKEN or not GITHUB_REPO:
        print("请设置所需的环境变量: GITHUB_USERNAME, GITHUB_TOKEN, GITHUB_REPO")
        return
    
    starred_repos = get_starred_repos()
    if starred_repos:
        content = generate_stars_list(starred_repos)
        update_readme(content)
    else:
        print("没有找到star的仓库或获取失败")

if __name__ == "__main__":
    main()
