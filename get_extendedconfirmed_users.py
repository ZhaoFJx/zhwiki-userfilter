import requests

# 更优雅版本，不过只能找特定用户组
def get_all_extendedconfirmed_users(aufrom="", user_list=[]):
    url = "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "allusers",
        "augroup": "extendedconfirmed",
        "format": "json",
        "aufrom": aufrom
    }

    response = requests.get(url, params=params)
    data = response.json()

    users = data['query']['allusers']
    
    for user in users:
        user_list.append(user['name'])

    if 'continue' in data:
        next_aufrom = data['continue']['aufrom']
        get_all_extendedconfirmed_users(next_aufrom, user_list)
    
    return user_list

user_list = get_all_extendedconfirmed_users()

with open("extendedconfirmed_users.txt", "w", encoding="utf-8") as file:
    for user in user_list:
        file.write(user + "\n")

print(f"已成功获取 {len(user_list)} 位拥有 extendedconfirmed 权限的用户，并保存到 'extendedconfirmed_users.txt'")