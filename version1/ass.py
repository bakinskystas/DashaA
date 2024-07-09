import speech_recognition as sr
import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext, Entry, Button
from gtts import gTTS
import playsound
import tempfile
import psutil  # для мониторинга системы
import threading  # для работы с потоками

# Функция синтеза речи с использованием gTTS
def speak(text):
    tts = gTTS(text=text, lang='ru')
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(fp.name)
        playsound.playsound(fp.name)

# Функция распознавания речи
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Слушаю...")
        log_output("Слушаю...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio, language='ru-RU')
        print(f"Вы сказали: {command}")
        log_output(f"Вы сказали: {command}")
        return command
    except sr.UnknownValueError:
        response = "Извините, я не поняла. Повторите, пожалуйста."
        speak(response)
        log_output(response)
        return ""
    except sr.RequestError:
        response = "Ошибка при запросе к сервису распознавания."
        speak(response)
        log_output(response)
        return ""

# Функция выполнения команд
def execute_command(command):
    if 'открой браузер' in command:
        subprocess.Popen(["firefox"])
        response = "Браузер открыт."
    elif 'закрой браузер' in command:
        os.system("pkill firefox")
        response = "Браузер закрыт."
    elif 'открой терминал' in command:
        subprocess.Popen(["gnome-terminal"])
        response = "Терминал открыт."
    elif 'время' in command:
        time = subprocess.getoutput("date +%H:%M")
        response = f"Сейчас {time}"
    elif 'открой файл' in command:
        file_path = command.replace('открой файл', '').strip()
        if os.path.exists(file_path):
            subprocess.Popen(["xdg-open", file_path])
            response = f"Файл {file_path} открыт."
        else:
            response = f"Файл {file_path} не найден."
    elif 'запусти программу' in command:
        program_name = command.replace('запусти программу', '').strip()
        try:
            subprocess.Popen([program_name])
            response = f"Программа {program_name} запущена."
        except FileNotFoundError:
            response = f"Программа {program_name} не найдена."
    elif 'перезагрузи систему' in command:
        os.system("reboot")
        response = "Система перезагружается."
    elif 'выключи систему' in command:
        os.system("poweroff")
        response = "Система выключается."
    elif 'блокировка экрана' in command:
        os.system("gnome-screensaver-command -l")
        response = "Экран заблокирован."
    elif 'создай папку' in command:
        folder_name = command.replace('создай папку', '').strip()
        os.makedirs(folder_name, exist_ok=True)
        response = f"Папка {folder_name} создана."
    elif 'удали файл' in command:
        file_path = command.replace('удали файл', '').strip()
        if os.path.exists(file_path):
            os.remove(file_path)
            response = f"Файл {file_path} удалён."
        else:
            response = f"Файл {file_path} не найден."
    elif 'громкость' in command:
        volume_level = command.replace('громкость', '').strip()
        os.system(f"amixer set Master {volume_level}%")
        response = f"Громкость установлена на {volume_level}%."
    elif 'список процессов' in command:
        processes = subprocess.getoutput("ps -aux")
        response = "Список процессов:\n" + processes
    elif 'заверши процесс' in command:
        process_name = command.replace('заверши процесс', '').strip()
        os.system(f"pkill {process_name}")
        response = f"Процесс {process_name} завершён."
    elif 'системная информация' in command:
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        response = (f"Использование CPU: {cpu_usage}%\n"
                    f"Использование памяти: {memory_info.percent}%\n"
                    f"Использование диска: {disk_info.percent}%")
    else:
        response = "Команда не распознана. Повторите, пожалуйста."

    speak(response)
    log_output(response)

# Функция лога
def log_output(text):
    log_area.config(state=tk.NORMAL)
    log_area.insert(tk.END, text + "\n")
    log_area.config(state=tk.DISABLED)
    log_area.yview(tk.END)

# Основной цикл программы
def main():
    speak("Привет! Я ваш голосовой помощник.")
    while not stop_flag.is_set():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Слушаю ключевую фразу...")
            log_output("Слушаю ключевую фразу...")
            audio = recognizer.listen(source)
        try:
            trigger = recognizer.recognize_google(audio, language='ru-RU')
            if trigger.lower() == "даша":
                speak("Я вас слушаю")
                log_output("Активировано: Даша")
                command = listen().lower()
                if command == "стоп":
                    response = "До свидания!"
                    speak(response)
                    log_output(response)
                    break
                else:
                    execute_command(command)
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            response = "Ошибка при запросе к сервису распознавания."
            speak(response)
            log_output(response)

# Функция запуска ассистента в отдельном потоке
def start_assistant():
    global stop_flag
    stop_flag = threading.Event()
    assistant_thread = threading.Thread(target=main)
    assistant_thread.start()

# Функция остановки ассистента
def stop_assistant():
    stop_flag.set()
    speak("Ассистент остановлен.")
    log_output("Ассистент остановлен.")

# Функция отправки команд вручную
def manual_command():
    command = entry.get()
    if command:
        log_output(f"Вы сказали: {command}")
        entry.delete(0, tk.END)
        execute_command(command)

# Интерфейс с помощью Tkinter
root = tk.Tk()
root.title("Голосовой помощник")

log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, width=50, height=20)
log_area.pack(padx=10, pady=10)

entry = Entry(root, width=50)
entry.pack(pady=10)

send_button = Button(root, text="Отправить команду", command=manual_command)
send_button.pack(pady=10)

start_button = Button(root, text="Запустить помощника", command=start_assistant)
start_button.pack(pady=10)

stop_button = Button(root, text="Остановить помощника", command=stop_assistant)
stop_button.pack(pady=10)

root.mainloop()
