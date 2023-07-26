import os
import requests
import datetime
import fuzzywuzzy
from fuzzywuzzy import process

token = "6241896510:AAFMUc_t6T1BwsEx-ixtoBOMk3dY7f9AjgU"

path_dic = "tbot_dataset.txt"


class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        resp_json = resp.json()

        if 'result' in resp_json:
            result_json = resp_json['result']
            return result_json
        else:
            print('Error: Response does not contain the "result" field.')
            return []

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = get_result
        return last_update


def read_dictionary(our_file):
    with open(our_file, "r", encoding="utf-8") as fi:
        data = fi.readlines()
    return data

greet_bot = BotHandler(token)

now = datetime.datetime.now()

def write_chats(filename, information, today):
    new = open(filename, "a")
    new.write(today + "\n")
    new.write(str(information) + "\n")

rate = 77

def main():
    new_offset = None
    hour = now.hour
    dicti = []
    resp = read_dictionary(path_dic)
    dicti.append(resp)

    unanswered_questions = []

    while True:
        updates = greet_bot.get_updates(new_offset)

        if len(updates) > 0:
            # Process each update independently
            for update in updates:
                last_update = update

                last_update_id = last_update['update_id']
                last_chat_text = last_update['message']['text']
                last_chat_id = last_update['message']['chat']['id']
                last_chat_name = last_update['message']['chat']['first_name']
                try:
                    first_chat_name = last_update['message']['chat']['last_name']
                except:
                    first_chat_name = "none"

                if last_chat_text == "/start":
                    greet_bot.send_message(last_chat_id, 'Привет, {}! Пожалуйста, задайте свой вопрос.'.format(last_chat_name))
                else:
                    counter = 0
                    best_match = None
                    greet_bot.send_message(last_chat_id, 'Пожалуйста, подождите немного, {}.'.format(last_chat_name))
                    for el in dicti[0]:
                        if el.startswith("вопрос:"):
                            components = el.split("ответ:")
                            if len(components) == 2:
                                question, answer = components
                                leven = fuzzywuzzy.fuzz.partial_ratio(last_chat_text.lower(), question.lower().strip())
                                if leven >= rate and leven > counter:
                                    print("Understand")
                                    counter = leven
                                    best_match = answer.strip()

                    if best_match:
                        greet_bot.send_message(last_chat_id, best_match)
                    else:
                        greet_bot.send_message(last_chat_id, 'На данный момент я не знаю ответа на этот вопрос, но в будущем постараюсь узнать.'.format(last_chat_name))
                        unanswered_questions.append(last_chat_text)

                write_chats(last_chat_name + "_" + first_chat_name, last_update, str(datetime.datetime.now()))
                new_offset = last_update_id + 1

        else:
            print("No updates")

    if unanswered_questions:
        unanswered_file_path = "unanswered.txt"
        with open(unanswered_file_path, "a", encoding="utf-8") as file:
            file.write("\n".join(unanswered_questions))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
