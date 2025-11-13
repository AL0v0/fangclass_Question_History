import requests
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Author  : Ryuuuuko
# @Date    : 2025-11-13
# @Desc    : 目前仅实现研讨厅查询功能，查询时需保持自己的登陆状态，用token查询,由于查询逻辑设计需要遍历每一节课，结果输出较慢，请同学们耐心等待，任何问题或优化建议可留言github或邮箱 :)
# @email   : RK0v0@outlook.com

token="<token>"
NAME = "<你的名字>"

my_headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua-platform': '"Windows"',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    'token': token,
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://class.fangban.net/course',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',

    'Cookie': 'token=%s' % token
    # ... 您可以根据需要添加更多 sec- 开头的 header ...
}


'''整合每节课的数据'''
def data_extract(data):
    global NAME
    result_list = []

    validate=""
    date = data.get('date') #日期
    class_name = data.get('class') #班级
    period = data.get('period')  #期数
    classroom = data.get('offline_classroom') #教室

    for report in data.get('report', []):
        reporter_name = report.get('reporter')

        for ask_student in report.get('ask_student', []):
            if 'nick' in ask_student:
                if ask_student['nick'] == NAME:
                    if 'is_validate' in ask_student:
                        if ask_student['is_validate']:
                            validate = "有效"
                        else:
                            validate = "无效"
                    else:
                        validate = "未出结果"
                    result= f"{validate} + {date} + {class_name} + {period} + {classroom} + {reporter_name}"
                    result_list.append(result)
    return result_list

def get_each_class_result(id):
    #给每节课发送请求
    class_url = f"https://class.fangban.net/api/course/info/{id}"
    try:
        response = requests.get(class_url, headers=my_headers)

        if response.status_code == 200:
            each_class_json = response.json()
            each_class_list = data_extract(each_class_json['data'])
            return each_class_list

        else:
            print(f"--- 请求失败 ---")
            print(f"状态码 (Status Code): {response.status_code}")
            print(f"返回内容: {response.text[:200]}...")  # 打印部分错误信息
            return []

    except requests.exceptions.RequestException as e:
        print(f"--- 发生网络错误 ---")
        print(e)

'''获取研讨厅上课的时间列表'''
def get_dates_by_name(json_data, name="厅",theme = "#297ECC"):  #目前只支持研讨厅
    found_dates = set()
    data_list = json_data.get('data', [])
    for entry in data_list:
        stats_list = entry.get('course_stats', [])
        for stat in stats_list:
            if stat.get('name') == name and stat.get('theme') == theme:
                entry_date = entry.get('date')
                if entry_date:
                    found_dates.add(entry_date)
                break
    return sorted(list(found_dates))

'''获取指定日期每节课程的id，然后组成url'''
def get_class_id(date):
    class_id_list = set()
    course_query_url = f"https://class.fangban.net/api/course/list/?date={date}"

    res = requests.get(course_query_url, headers=my_headers)
    if res.status_code == 200:
        res_json = res.json()
        if res_json:
            data_list = res_json.get('data', [])['data']
            for entry in data_list:
                id = entry.get('id')
                if id:
                    class_id_list.add(id)
        return list(class_id_list)
    else:
        print("课程查询失败")


def get_course_date(name="2025%E5%B9%B4%E7%A7%8B%E5%AD%A3%E8%AF%BE%E7%A8%8B"):  #name:2025秋季课程
    '''这里换学期要更换'''
    query_url = f"https://class.fangban.net/api/course/calendar_list/?name={name}"
    response = requests.get(query_url, headers=my_headers)
    if response.status_code == 200:
        res_json = response.json()
        if res_json:
            class_date_list = get_dates_by_name(res_json)
            return class_date_list
        else:
            print("上课日期查询失败")
    else:
        print(f"--- 请求失败 ---")
        print(f"状态码 (Status Code): {response.status_code}")
        print(f"返回内容: {response.text[:200]}...")  # 打印部分错误信息
        return []



if __name__ == "__main__":
    '''查询逻辑：按日期查找研讨厅课程列表--》按每节课查询提问学生数据--》判断我是否在提问学生数据中'''
    total_result=[]
    total_count = 0
    all_course_date = get_course_date()
    print(f"---开始查询【{NAME}】的提问情况---")
    for date in all_course_date:
        class_id_list = get_class_id(date)
        if class_id_list:
            for id in class_id_list:  #每节课的数据
                result = get_each_class_result(id)
                if result:
                    for r in result:
                        print(r)
                    total_count += len(result)
                    total_result.extend(result)

    print(f"{NAME}共提问【{total_count}】次")
    valid_count = 0
    invalid_count = 0
    unknown = 0
    for result in total_result:
        if "有效" in result:
            valid_count += 1
        elif "无效" in result:
            invalid_count += 1
        else:
            unknown += 1
    print(f"其中，有效【{valid_count}】次，无效【{invalid_count}】次，未出结果【{unknown}】次")


