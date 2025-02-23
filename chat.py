import traceback
import tools
import kimi
import coze
from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

API_KEY = os.getenv('API_KEY')
if not API_KEY:
    print("API_KEY not found in environment variables. Please set it up in your.env file.")
    exit(1)
MODEL = os.getenv('MODEL')
BASE_URL = os.getenv('BASE_URL')
ROLE = os.getenv('ROLE')

client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
)

def chat_with_model():
    print("欢迎使用 超级助理！ 输入 'exit' 退出对话。")
    with open(ROLE, 'r', encoding='utf-8') as file:
        content = file.read()
    # 初始化消息历史
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    messages = [
        {'role': 'system', 'content': f"{content}。现在的时间是{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}，{weekdays[datetime.today().weekday()]}"}
    ]

    while True:
        try:
            # 获取用户输入
            user_input = input("你: ")
            if user_input.lower() == 'exit':
                print("对话已结束。")
                break
            count = 0
            # 添加用户消息到对话历史
            messages.append({'role': 'user', 'content': user_input})
            while True:
                # 调用模型，开启流式输出
                stream = client.chat.completions.create(model=MODEL, messages=messages, stream=True)
                print("助手: ", end="", flush=True)

                # 收集助手的响应
                assistant_response = ""
                for chunk in stream:
                        content = chunk.choices[0].delta.content
                        assistant_response += content
                        print(content, end="", flush=True)

                print()  # 换行

                # 将助手响应添加到对话历史
                messages.append({'role': 'assistant', 'content': assistant_response})
                try:
                    command = tools.getJsonObject(assistant_response)
                    if not command:
                        print("成功执行了任务！")
                        break
                    if command["action"] == "check_package_installed":
                        result = tools.check_package_installed(command["package_name"])
                        messages.append({'role': 'assistant', 'content': f"已经成功执行{command['action']}方法，返回为{result}"})
                    elif command["action"] == "write_to_file":
                        result = tools.write_to_file(command["file_path"], command["content"])
                        messages.append({'role': 'assistant', 'content': f"已经成功执行{command['action']}方法，返回为{result}"})
                    elif command["action"] == "execute_command":
                        result = tools.execute_command(command["command"])
                        messages.append({'role': 'assistant', 'content': f"已经成功执行{command['action']}方法，返回为{result}"})
                    elif command["action"] == "send_email":
                        result = tools.send_email(command["subject"], command["content"], command["to"], command.get("file_path", ""), command.get("file_name", ""))
                        messages.append({'role': 'assistant', 'content': f"已经成功执行{command['action']}方法，返回为{result}"})
                    elif command["action"] == "read_from_file":
                        result = tools.read_from_file(command["file_path"])
                        messages.append({'role': 'assistant', 'content': f"已经成功执行{command['action']}方法，返回为{result}"})
                    elif command["action"] == "extract_text_from_ppt":
                        result = tools.extract_text_from_ppt(command["ppt_path"])
                        messages.append({'role': 'assistant', 'content': f"已经成功执行{command['action']}方法，返回为{result}"})
                    elif command["action"] == "extract_text_from_docx":
                        result = tools.extract_text_from_docx(command["docx_path"])
                        messages.append({'role': 'assistant', 'content': f"已经成功执行{command['action']}方法，返回为{result}"})
                    elif command["action"] == "web_search":
                        result = kimi.web_search(command["content"])
                        messages.append({'role': 'assistant', 'content': f"已经成功执行{command['action']}方法，返回为{result}"})
                    elif command["action"] == "create_image":
                        result = coze.create_image(command["image_prompt"], command["file_path"])
                        messages.append({'role': 'assistant', 'content': f"已经成功执行{command['action']}方法，返回为{result}"})
                    elif command["action"] == "wait_for_user_input":
                        print("已执行任务，请进一步指示。")
                        break
                    elif command["action"] == "exit":
                        print("成功执行了任务！")
                        break
                    else:
                        messages.append({'role': 'user', 'content': f"我不太明白你的意思，没有找到具体的指令。请重新回答。你可以自己通过写python文件执行你自己的指令。"})
                    # 以用户的口吻提醒模型继续执行。
                    messages.append({'role': 'user', 'content': f"好的，请根据执行结果判断是否继续执行或者终止。"})
                except Exception as e:
                    print(f"发生错误: {e}")
                    if count>=10:
                        break
                    traceback.print_exc()
                    count+=1
                    messages.append({'role': 'user', 'content': f"发生错误: {e}"})

        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == "__main__":
    chat_with_model()
