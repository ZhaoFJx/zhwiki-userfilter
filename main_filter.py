import requests
import json
from datetime import datetime, timedelta, timezone
import os

# 此处用自确认用户省一点点时间，因为满足下方过滤条件的用户必定是自动确认用户。
# 如果要查找所有用户，可以将augroup改为user，但是会花费更多时间
def get_autoconfirmed_users(save_file="autoconfirmed_users.json"):
    user_list = []
    url = "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "allusers",
        "augroup": "autoconfirmed", # 改这里
        "format": "json",
        "aulimit": "max"
    }

    total_users = 0

    while True:
        response = requests.get(url, params=params)
        data = response.json()

        users = data['query']['allusers']
        user_list.extend(users)
        total_users += len(users)

        print(f"已获取 {total_users} 名自动确认用户")

        if 'continue' not in data:
            break

        params['aufrom'] = data['continue']['aufrom']

    # 保存到当前文件夹user_list.json
    with open(save_file, "w", encoding="utf-8") as file:
        json.dump(user_list, file, ensure_ascii=False, indent=4)
    
    print(f"已完成并保存 {total_users} 名自动确认用户名单到 '{save_file}'")

    return user_list


# 检查文件
def load_autoconfirmed_users(file="autoconfirmed_users.json"):
    if os.path.exists(file):
        print(f"从 {file} 获取列表...")
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print(f"未找到存在的名单，准备请求MediaWiki API")
        return get_autoconfirmed_users()


# 通过注册时间和编辑次数过滤用户
def filter_users_by_criteria(user_list, min_days_registered=90, min_edit_count=500): # 改这里
    filtered_users = []
    today = datetime.now(timezone.utc)
    min_registration_date = today - timedelta(days=min_days_registered)

    total_users = len(user_list)
    print(f"正在按照标准过滤 {total_users} 名用户")

    batch_size = 50
    for i in range(0, total_users, batch_size):
        batch_users = user_list[i:i + batch_size]
        user_info_list = get_batch_user_info([user['name'] for user in batch_users])

        for user_info in user_info_list:
            if user_info.get('registration') and user_info.get('editcount'):
                registration_date = datetime.strptime(user_info['registration'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                edit_count = user_info['editcount']

                if registration_date < min_registration_date and edit_count > min_edit_count:
                    filtered_users.append(user_info['name'])

        print(f"已过滤 {min(i + batch_size, total_users)} / {total_users} 名用户")

    print(f"已完成过滤，总用户：{len(filtered_users)}")
    return filtered_users


# query
def get_batch_user_info(usernames):
    url = "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "users",
        "ususers": "|".join(usernames),
        "usprop": "registration|editcount",
        "format": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()
    return data['query']['users']



if __name__ == "__main__":
    print("欢迎使用半自动用户过滤器")

    autoconfirmed_users = load_autoconfirmed_users()

    filtered_users = filter_users_by_criteria(autoconfirmed_users)

    output_file = "filtered_users.txt"
    with open(output_file, "w", encoding="utf-8") as file:
        for user in filtered_users:
            file.write(user + "\n")

    print(f"已成功过滤 {len(filtered_users)} 名用户并保存至 '{output_file}'")