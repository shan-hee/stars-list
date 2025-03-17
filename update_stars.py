import os
import requests
import json
import base64
from datetime import datetime

# 直接设置默认值，避免依赖环境变量
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "shan-hee")  # 默认为你的用户名
GITHUB_REPO = os.environ.get("GITHUB_REPO", "stars-list").split("/")[-1]  # 提取仓库名部分
# 尝试使用GITHUB_TOKEN环境变量，如果没有则使用默认的GITHUB_TOKEN
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("INPUT_TOKEN") or os.environ.get("INPUT_GITHUB_TOKEN")
OUTPUT_FILE = "README.md"

def get_starred_repos():
    """获取用户的所有star项目，不需要认证也可以获取公开数据"""
    print(f"正在获取用户 {GITHUB_USERNAME} 的star列表")
    all_stars = []
    page = 1
    
    try:
        while True:
            url = f"https://api.github.com/users/{GITHUB_USERNAME}/starred?page={page}&per_page=100"
            headers = {"Accept": "application/vnd.github.v3+json"}
            
            # 尝试使用token，但即使没有也可以访问公开数据
            if GITHUB_TOKEN:
                headers["Authorization"] = f"token {GITHUB_TOKEN}"
            
            response = requests.get(url, headers=headers)
            print(f"页面 {page} 响应状态: {response.status_code}")
            
            if response.status_code != 200:
                print(f"获取数据失败: {response.text}")
                break
                
            repos = response.json()
            if not repos:
                break
                
            all_stars.extend(repos)
            print(f"获取到 {len(repos)} 个star项目")
            page += 1
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
    
    print(f"总共获取到 {len(all_stars)} 个star项目")
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
        if about:
            # 处理markdown表格中的特殊字符
            about = about.replace("\n", " ").replace("|", "\\|")
        content += f"| [{name}]({repo['html_url']}) | {about} |\n"
    
    return content

def main():
    """使用git命令而不是API来更新文件"""
    print("开始运行...")
    print(f"用户名: {GITHUB_USERNAME}")
    print(f"仓库名: {GITHUB_REPO}")
    print(f"Token是否存在: {bool(GITHUB_TOKEN)}")
    
    starred_repos = get_starred_repos()
    if not starred_repos:
        print("没有找到star的仓库或获取失败")
        return
        
    content = generate_stars_list(starred_repos)
    
    # 将内容写入README.md
    print("正在更新README.md...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("已创建README.md文件")
    print("请使用git命令提交更改")

if __name__ == "__main__":
    main()
