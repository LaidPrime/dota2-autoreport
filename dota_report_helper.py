# -*- coding: utf-8 -*-
"""
Dota 2 Report Helper (версия с автоопределением игрока по нику)

ВАЖНО ПРО OCR:
Для работы распознавания текста на вашем компьютере ДОЛЖЕН быть установлен
Tesseract OCR. Скачать можно здесь:
https://github.com/UB-Mannheim/tesseract/wiki
После установки проверьте путь в константе TESSERACT_PATH ниже.

Что нужно сделать перед запуском:
1. Установить Tesseract OCR и библиотеки: pip install pytesseract Pillow
2. Запустить coord_finder.py и заполнить координаты в словаре COORDS:
   - scoreboard_region (область колонки ников, ровно 10 строк);
   - rows 1..10 (кнопки репорта для каждой строки скорборда);
   - checkboxes и submit (окно репорта).
3. Вписать свой ник в поле "Your Nickname".
4. Запустить скрипт, выбрать режим и игроков, нажать START REPORTS.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

import threading
import time
import random
import os
import re
import pyautogui

# ------------------------------------------------------------
# Попытка использовать pydirectinput (лучше работает в играх).
# Если не установлен — будет использован pyautogui.
# ------------------------------------------------------------
try:
    import pydirectinput
    CLICKER = pydirectinput
except ImportError:
    CLICKER = pyautogui

# ------------------------------------------------------------
# OCR (распознавание текста).
# pytesseract — обёртка над Tesseract OCR.
# Если библиотека не установлена, OCR_AVAILABLE = False.
# ------------------------------------------------------------
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    pytesseract = None
    OCR_AVAILABLE = False

# ------------------------------------------------------------
# Подключение Tesseract OCR БЕЗ изменения системного PATH.
#
# 1) Указываем pytesseract полный путь к tesseract.exe.
# 2) На всякий случай добавляем папку Tesseract в PATH,
#    но ТОЛЬКО внутри этого процесса (os.environ).
#    Система и другие программы этого не увидят,
#    а pytesseract сможет найти программу и по имени "tesseract".
#
# Если Tesseract установлен в другое место — поменяйте TESSERACT_DIR.
# ------------------------------------------------------------
TESSERACT_DIR = r"C:\Program Files\Tesseract-OCR"
TESSERACT_PATH = os.path.join(TESSERACT_DIR, "tesseract.exe")

if OCR_AVAILABLE and os.path.exists(TESSERACT_PATH):
    # Полный путь для pytesseract
    pytesseract.tesseract_cmd = TESSERACT_PATH

    # PATH только для текущего процесса Python
    if TESSERACT_DIR not in os.environ.get("PATH", ""):
        os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + TESSERACT_DIR

# Язык распознавания. Ники обычно латиницей, поэтому "eng".
# Если ник содержит кириллицу — установите язык в Tesseract
# и поменяйте на "eng+rus".
OCR_LANG = "eng"

# Клавиша, которая ОТКРЫВАЕТ скорборд, пока её держат.
# В Dota 2 по умолчанию это Tab. Если у вас другая — поменяйте.
SCOREBOARD_KEY = "tab"

# Безопасность: резкий увод мыши в левый верхний угол останавливает скрипт
pyautogui.FAILSAFE = True

try:
    CLICKER.FAILSAFE = True
except Exception:
    pass

pyautogui.PAUSE = 0.0

try:
    CLICKER.PAUSE = 0.0
except Exception:
    pass

# Задержка перед стартом кликов (секунды)
START_DELAY_SECONDS = 5

# Случайная задержка между кликами (имитация пауз)
MIN_CLICK_DELAY = 0.2
MAX_CLICK_DELAY = 0.6


# ============================================================
# КООРДИНАТЫ
# ============================================================
# ВАЖНО: сейчас здесь плейсхолдеры. Заполните их через coord_finder.py.
#
# НОВАЯ СТРУКТУРА:
# - scoreboard_region: (x, y, width, height) — область КОЛОНКИ С НИКАМИ.
#   Она должна начинаться с верхней границы строки 1 и заканчиваться
#   нижней границей строки 10. Высота делится на 10 равных строк.
# - rows: координаты КНОПКИ РЕПОРТА (флажка) для каждой из 10 строк
#   скорборда. Строки 1-5 — верхняя команда, 6-10 — нижняя.
# - checkboxes / submit — окно репорта, как раньше.
#
# Союзники и враги больше не задаются вручную: скрипт сам находит
# вашу строку по нику и понимает, кто союзник, а кто враг.
# ============================================================

COORDS = {
    # --------------------------------------------------------
    # Режим TURBO
    # --------------------------------------------------------
    "turbo": {
        # Область колонки ников: (x, y, ширина, высота)
        "scoreboard_region": (2, 63, 1014, 847),

        # Кнопки репорта для строк скорборда 1..10
        "rows": {
            1: (861, 133),   # строка 1 (верхняя команда)
            2: (861, 213),   # строка 2
            3: (861, 289),   # строка 3
            4: (861, 369),   # строка 4
            5: (859, 444),   # строка 5
            6: (863, 559),   # строка 6 (нижняя команда)
            7: (866, 636),   # строка 7
            8: (866, 716),   # строка 8
            9: (863, 791),   # строка 9
            10: (864, 869),  # строка 10
        },

        # Чекбоксы жалоб в окне репорта
        "checkboxes": [
            (777, 496),
            (943, 510),
            (1117, 517),
            (854, 680),
            (1041, 691),
        ],

        # Кнопка Submit
        "submit": (1071, 901),
    },


    # --------------------------------------------------------
    # Режим ALL PICK
    # --------------------------------------------------------
    "all_pick": {
        "scoreboard_region": (0, 60, 907, 847),

        "rows": {
            1: (750, 230),
            2: (750, 280),
            3: (750, 330),
            4: (750, 380),
            5: (750, 430),
            6: (750, 480),
            7: (750, 530),
            8: (750, 580),
            9: (750, 630),
            10: (750, 680),
        },

        "checkboxes": [
            (260, 310),
            (260, 350),
            (260, 390),
            (260, 430),
            (260, 470),
        ],

        "submit": (310, 540),
    },
}


class DotaReportHelper(ctk.CTk):
    """Главное окно программы."""

    def __init__(self):
        super().__init__()

        self.title("Dota 2 Report Helper")
        self.geometry("600x780")
        self.minsize(560, 720)
        self.resizable(False, False)

        self.running = False
        self.abort = False

        self.mode_var = tk.StringVar(value="turbo")
        self.team_var = tk.StringVar(value="enemies")

        # ------------------------------------------------------------
        # Заголовок
        # ------------------------------------------------------------
        ctk.CTkLabel(
            self,
            text="Dota 2 Report Helper",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(14, 2))

        ctk.CTkLabel(
            self,
            text="Ник будет найден на скорборде автоматически,\n"
                 "союзники и враги определятся по вашей стороне.",
            text_color="gray"
        ).pack(pady=(0, 10))

        # ------------------------------------------------------------
        # Поле ввода ника
        # ------------------------------------------------------------
        nickname_frame = ctk.CTkFrame(self)
        nickname_frame.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(
            nickname_frame,
            text="Your Nickname:",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=10, pady=8)

        self.nickname_var = tk.StringVar(value="")
        ctk.CTkEntry(
            nickname_frame,
            textvariable=self.nickname_var,
            width=220
        ).pack(side="left", padx=10, pady=8)

        ctk.CTkLabel(
            nickname_frame,
            text="Точно как в игре",
            text_color="gray"
        ).pack(side="left")

        # ------------------------------------------------------------
        # Выбор режима игры
        # ------------------------------------------------------------
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(
            mode_frame,
            text="Режим игры:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(8, 0))

        ctk.CTkRadioButton(
            mode_frame, text="Report in Turbo",
            variable=self.mode_var, value="turbo"
        ).pack(anchor="w", padx=26, pady=2)

        ctk.CTkRadioButton(
            mode_frame, text="Report in All Pick",
            variable=self.mode_var, value="all_pick"
        ).pack(anchor="w", padx=26, pady=(2, 8))

        # ------------------------------------------------------------
        # Выбор команды (союзники / враги)
        # ------------------------------------------------------------
        team_frame = ctk.CTkFrame(self)
        team_frame.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(
            team_frame,
            text="Кого репортить:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(8, 0))

        ctk.CTkRadioButton(
            team_frame, text="Allies (ваши союзники)",
            variable=self.team_var, value="allies",
            command=self.update_player_frame
        ).pack(anchor="w", padx=26, pady=2)

        ctk.CTkRadioButton(
            team_frame, text="Enemies (враги)",
            variable=self.team_var, value="enemies",
            command=self.update_player_frame
        ).pack(anchor="w", padx=26, pady=(2, 8))

        # ------------------------------------------------------------
        # Контейнер выбора игроков
        # ------------------------------------------------------------
        self.players_container = ctk.CTkFrame(self)
        self.players_container.pack(fill="x", padx=16, pady=4)

        # Союзники: 4 слота (вы себя не репортите)
        self.allies_frame = ctk.CTkFrame(self.players_container)
        self.ally_vars = {}

        ctk.CTkLabel(
            self.allies_frame,
            text="Союзники (кроме вас):",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(8, 0))

        for i in range(1, 5):
            var = tk.BooleanVar(value=False)
            ctk.CTkCheckBox(
                self.allies_frame, text=f"Игрок {i}", variable=var
            ).pack(anchor="w", padx=26, pady=2)
            self.ally_vars[i] = var

        ctk.CTkLabel(self.allies_frame, text="").pack(pady=(0, 4))

        # Враги: 5 слотов
        self.enemy_frame = ctk.CTkFrame(self.players_container)
        self.enemy_vars = {}

        ctk.CTkLabel(
            self.enemy_frame,
            text="Враги:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=10, pady=(8, 0))

        for i in range(1, 6):
            var = tk.BooleanVar(value=False)
            ctk.CTkCheckBox(
                self.enemy_frame, text=f"Игрок {i}", variable=var
            ).pack(anchor="w", padx=26, pady=2)
            self.enemy_vars[i] = var

        ctk.CTkLabel(self.enemy_frame, text="").pack(pady=(0, 4))

        self.update_player_frame()

        # ------------------------------------------------------------
        # Report Duration (sec)
        # ------------------------------------------------------------
        duration_frame = ctk.CTkFrame(self)
        duration_frame.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(
            duration_frame,
            text="Report Duration (sec):",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=10, pady=8)

        self.report_duration_var = tk.StringVar(value="5")
        ctk.CTkEntry(
            duration_frame,
            textvariable=self.report_duration_var,
            width=90
        ).pack(side="left", padx=10, pady=8)

        ctk.CTkLabel(
            duration_frame,
            text="Общее время на чекбоксы одного репорта",
            text_color="gray"
        ).pack(side="left", padx=10)

        # ------------------------------------------------------------
        # Кнопки START / STOP
        # ------------------------------------------------------------
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(fill="x", padx=16, pady=10)

        self.start_btn = ctk.CTkButton(
            controls_frame,
            text="START REPORTS",
            height=52,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#B22222",
            hover_color="#8B0000",
            command=self.start_reports
        )
        self.start_btn.pack(fill="x")

        self.stop_btn = ctk.CTkButton(
            controls_frame,
            text="STOP",
            height=34,
            fg_color="#444444",
            hover_color="#660000",
            state="disabled",
            command=self.stop
        )
        self.stop_btn.pack(fill="x", pady=(8, 0))

        # ------------------------------------------------------------
        # Статус
        # ------------------------------------------------------------
        self.status_label = ctk.CTkLabel(
            self,
            text="Готов к работе.",
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 12))

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ============================================================
    # Вспомогательные методы GUI
    # ============================================================

    def update_player_frame(self):
        """Показывает нужный фрейм: союзники или враги."""
        for child in self.players_container.winfo_children():
            child.pack_forget()

        if self.team_var.get() == "allies":
            self.allies_frame.pack(fill="x", padx=8, pady=8)
        else:
            self.enemy_frame.pack(fill="x", padx=8, pady=8)

    def get_selected_players(self):
        """Возвращает номера выбранных слотов (1..4 или 1..5)."""
        variables = (
            self.ally_vars if self.team_var.get() == "allies"
            else self.enemy_vars
        )
        return [num for num, var in variables.items() if var.get()]

    def get_nickname(self):
        """Возвращает ник из поля ввода."""
        return self.nickname_var.get().strip()

    def get_report_duration(self):
        """
        Возвращает Report Duration (sec).
        Если введено не число — значение по умолчанию 5.
        """
        raw = self.report_duration_var.get().strip().replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            self.after(0, lambda: self.report_duration_var.set("5"))
            return 5.0

        return max(0.0, value)

    def set_status(self, text):
        """Потокобезопасное обновление статуса."""
        self.after(0, lambda: self.status_label.configure(text=text))

    def stop(self):
        self.abort = True
        self.set_status("Останавливаю процесс...")

    def on_close(self):
        self.abort = True
        self.destroy()

    def finish(self):
        self.after(0, self._finish_ui)

    def _finish_ui(self):
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    # ============================================================
    # Запуск
    # ============================================================

    def start_reports(self):
        if self.running:
            return

        selected_players = self.get_selected_players()

        if not selected_players:
            messagebox.showwarning(
                "Никто не выбран", "Выберите хотя бы одного игрока."
            )
            return

        if not self.get_nickname():
            messagebox.showwarning(
                "Нет ника", "Введите ваш ник в поле Your Nickname."
            )
            return

        if not OCR_AVAILABLE:
            messagebox.showerror(
                "OCR не установлен",
                "Выполните: pip install pytesseract Pillow"
            )
            return

        if not os.path.exists(TESSERACT_PATH):
            messagebox.showerror(
                "Tesseract не найден",
                "Установите Tesseract OCR и проверьте константу "
                "TESSERACT_PATH в начале скрипта."
            )
            return

        confirm = messagebox.askyesno(
            "Подтверждение",
            "Запустить автоматическую отправку репортов?\n\n"
            "Используйте только для реальных жалоб."
        )
        if not confirm:
            return

        self.running = True
        self.abort = False
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        threading.Thread(target=self.worker, args=(selected_players,), daemon=True).start()

    # ============================================================
    # Рабочий поток
    # ============================================================

    def worker(self, selected_players):
        try:
            # --------------------------------------------------------
            # Отсчёт перед стартом, чтобы вы переключились в Dota 2
            # --------------------------------------------------------
            for seconds_left in range(START_DELAY_SECONDS, 0, -1):
                if self.abort:
                    self.set_status("Остановлено до старта.")
                    return
                self.set_status(f"Переключитесь в Dota 2: {seconds_left}...")
                time.sleep(1)

            mode = self.mode_var.get()
            team = self.team_var.get()

            if mode not in COORDS:
                self.set_status(f"Ошибка: режим '{mode}' не настроен.")
                return

            mode_data = COORDS[mode]

            # --------------------------------------------------------
            # 1) Находим вашу строку на скорборде по нику
            # --------------------------------------------------------
            self.set_status("Открываю скорборд и ищу ваш ник...")
            user_row = self.detect_user_row(mode_data)

            if user_row is None:
                self.set_status(
                    "Ник не найден на скорборде. Проверьте ник, "
                    "scoreboard_region и что скорборд открылся."
                )
                return

            # --------------------------------------------------------
            # 2) Определяем сторону и строим карту слотов
            # --------------------------------------------------------
            mapping = self.build_mapping(user_row)
            side = "верхняя" if user_row <= 5 else "нижняя"

            self.set_status(
                f"Вы: строка {user_row} ({side}). Начинаю репорты..."
            )

            report_duration = self.get_report_duration()

            # --------------------------------------------------------
            # 3) Репортим выбранные слоты
            # --------------------------------------------------------
            for slot in selected_players:
                if self.abort:
                    break

                self.report_player(
                    mode_data, mapping, team, slot, report_duration
                )
                self.random_sleep(0.7, 1.3)

            if self.abort:
                self.set_status("Остановлено пользователем.")
            else:
                self.set_status("Готово. Все выбранные игроки обработаны.")

        except pyautogui.FailSafeException:
            self.set_status("FailSafe: курсор в углу экрана. Остановлено.")
        except Exception as e:
            self.set_status(f"Ошибка: {e}")
        finally:
            self.finish()

    # ============================================================
    # OCR: поиск вашего ника
    # ============================================================

    @staticmethod
    def normalize_text(text):
        """
        Приводит текст к нижнему регистру и убирает всё,
        кроме букв и цифр. Это делает сравнение ника устойчивым
        к пробелам, регистру и случайным символам OCR.
        """
        return re.sub(r"[^0-9a-zа-яё]", "", text.lower())

    def detect_user_row(self, mode_data):
        """
        Делает скриншот области скорборда, распознаёт текст и
        возвращает номер строки (1..10), где найден ваш ник.
        Если не нашёл — возвращает None.
        """
        region = mode_data.get("scoreboard_region")
        if not region:
            raise ValueError("Не задан scoreboard_region для режима.")

        norm_nick = self.normalize_text(self.get_nickname())

        # Держим клавишу скорборда, делаем скриншот, отпускаем
        try:
            CLICKER.keyDown(SCOREBOARD_KEY)
            time.sleep(0.7)  # даём скорборду открыться
            screenshot = pyautogui.screenshot(region=region)
        finally:
            CLICKER.keyUp(SCOREBOARD_KEY)

        # Распознаём текст с координатами каждого слова
        data = pytesseract.image_to_data(
            screenshot,
            lang=OCR_LANG,
            output_type=pytesseract.Output.DICT
        )

        # Собираем слова в строки по ключу (block, par, line)
        lines = {}
        for i in range(len(data["text"])):
            word = (data["text"][i] or "").strip()
            if not word:
                continue

            key = (
                data["block_num"][i],
                data["par_num"][i],
                data["line_num"][i],
            )
            entry = lines.setdefault(key, {"ys": [], "words": []})
            entry["ys"].append(data["top"][i] + data["height"][i] / 2.0)
            entry["words"].append(word)

        # Список строк: (средний Y, текст), отсортированный сверху вниз
        parsed_lines = []
        for entry in lines.values():
            y_center = sum(entry["ys"]) / len(entry["ys"])
            text = " ".join(entry["words"])
            parsed_lines.append((y_center, text))

        parsed_lines.sort(key=lambda item: item[0])

        # Высота одной строки скорборда: вся область / 10
        x, y, w, h = region
        row_height = h / 10.0

        # Ищем строку, содержащую ник
        for y_center, text in parsed_lines:
            if norm_nick and norm_nick in self.normalize_text(text):
                row = int(y_center // row_height) + 1
                row = min(max(row, 1), 10)
                return row

        return None

    @staticmethod
    def build_mapping(user_row):
        """
        Строит карту: какой СЛОТ GUI какому СТРOКЕ скорборда соответствует.

        Строки 1-5 — верхняя команда, 6-10 — нижняя.
        Если вы в верхней команде:
          - враги = строки 6..10 (слоты 1..5);
          - союзники = строки 1..5 без вашей (слоты 1..4).
        И наоборот.
        """
        top_rows = [1, 2, 3, 4, 5]
        bottom_rows = [6, 7, 8, 9, 10]

        if user_row <= 5:
            ally_rows = [r for r in top_rows if r != user_row]
            enemy_rows = bottom_rows
        else:
            ally_rows = [r for r in bottom_rows if r != user_row]
            enemy_rows = top_rows

        return {
            "allies": {i + 1: row for i, row in enumerate(ally_rows)},
            "enemies": {i + 1: row for i, row in enumerate(enemy_rows)},
        }

    # ============================================================
    # Отправка репорта
    # ============================================================

    def report_player(self, mode_data, mapping, team, slot, total_report_duration):
        """
        Репорт одного игрока:
        слот GUI -> строка скорборда -> координаты кнопки репорта.
        """
        row = mapping[team].get(slot)
        if row is None:
            raise ValueError(f"Нет строки для слота {slot} ({team}).")

        report_button = mode_data["rows"].get(row)
        if not report_button:
            raise ValueError(f"Нет координат для строки {row}.")

        # Пауза перед кликом по флажку
        self.random_sleep(MIN_CLICK_DELAY, MAX_CLICK_DELAY)
        if self.abort:
            return

        self.click(report_button)

        # Даём окну репорта открыться
        self.random_sleep(0.4, 0.8)
        if self.abort:
            return

        checkboxes = mode_data.get("checkboxes", [])
        checkbox_count = len(checkboxes)

        # ------------------------------------------------------------
        # Динамический интервал между чекбоксами:
        # checkbox_delay = Report Duration / количество чекбоксов
        # Пример: 5 сек / 5 чекбоксов = 1 сек после каждого клика.
        # ------------------------------------------------------------
        if checkbox_count > 0 and total_report_duration > 0:
            checkbox_delay = total_report_duration / checkbox_count
        else:
            checkbox_delay = 0.0

        for checkbox_pos in checkboxes:
            if self.abort:
                return

            self.click(checkbox_pos)

            if checkbox_delay > 0:
                self.interruptible_sleep(checkbox_delay)

            if self.abort:
                return

        submit_pos = mode_data.get("submit")
        if submit_pos:
            self.click(submit_pos)

        # Даём окну закрыться
        self.random_sleep(0.6, 1.1)

    # ============================================================
    # Клики и паузы
    # ============================================================

    def click(self, position):
        x, y = position
        CLICKER.click(x, y)

    def random_sleep(self, min_delay, max_delay):
        delay = random.uniform(min_delay, max_delay)
        end_time = time.time() + delay
        while time.time() < end_time:
            if self.abort:
                return
            time.sleep(0.02)

    def interruptible_sleep(self, seconds):
        """Пауза, прерываемая кнопкой STOP."""
        if seconds <= 0:
            return
        end_time = time.time() + seconds
        while time.time() < end_time:
            if self.abort:
                return
            time.sleep(0.02)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = DotaReportHelper()
    app.mainloop()