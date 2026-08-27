# -*- coding: utf-8 -*-
"""
Coord Finder
Мини-скрипт для определения координат мыши.

Как использовать:
1. Запустите этот скрипт.
2. Наведите курсор на нужный элемент в Dota 2.
3. Посмотрите X и Y в этом окне.
4. Скопируйте их и вставьте в COORDS в dota_report_helper.py.

Примечание:
Если Dota 2 работает в эксклюзивном полноэкранном режиме,
окно coord_finder может быть не видно. В таком случае используйте
Windowed или Borderless Window режим в Dota 2.
"""

import customtkinter as ctk
import pyautogui


class CoordFinder(ctk.CTk):
    """
    Небольшое окно, которое постоянно показывает текущие координаты мыши.
    """

    def __init__(self):
        super().__init__()

        # ------------------------------------------------------------
        # Настройки окна
        # ------------------------------------------------------------
        self.title("Coord Finder")
        self.geometry("430x220")
        self.resizable(False, False)

        # Окно поверх остальных окон, чтобы его было удобно видеть
        self.attributes("-topmost", True)

        # Текущие координаты
        self.coords = (0, 0)

        # ------------------------------------------------------------
        # Элементы интерфейса
        # ------------------------------------------------------------
        title_label = ctk.CTkLabel(
            self,
            text="Текущие координаты мыши:",
            font=ctk.CTkFont(size=14)
        )
        title_label.pack(pady=(14, 0))

        self.position_label = ctk.CTkLabel(
            self,
            text="X: 0, Y: 0",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.position_label.pack(pady=6)

        hint_label = ctk.CTkLabel(
            self,
            text=(
                "Наведите курсор на нужную кнопку в игре.\n"
                "Затем скопируйте координаты и вставьте их в COORDS.\n"
                "Esc — закрыть окно."
            ),
            text_color="gray"
        )
        hint_label.pack(padx=12, pady=(0, 8))

        copy_button = ctk.CTkButton(
            self,
            text="Скопировать X, Y",
            command=self.copy_coords
        )
        copy_button.pack(pady=(0, 12))

        self.copy_button = copy_button

        # Закрытие по Escape
        self.bind("<Escape>", lambda event: self.destroy())

        # Запускаем цикл обновления координат
        self.after(50, self.update_position)

    # ------------------------------------------------------------
    # Обновление позиции мыши каждые 50 мс
    # ------------------------------------------------------------
    def update_position(self):
        try:
            x, y = pyautogui.position()
            self.coords = (x, y)
            self.position_label.configure(text=f"X: {x}, Y: {y}")
        except Exception:
            # Если вдруг не удалось получить позицию, просто игнорируем
            pass

        # Повторно планируем обновление
        self.after(50, self.update_position)

    # ------------------------------------------------------------
    # Копирование координат в буфер обмена
    # ------------------------------------------------------------
    def copy_coords(self):
        text = f"{self.coords[0]}, {self.coords[1]}"

        # Очистка буфера обмена
        self.clipboard_clear()

        # Добавление координат
        self.clipboard_append(text)

        # Визуальная обратная связь
        self.copy_button.configure(text="Скопировано!")

        # Вернуть текст кнопки обратно через 900 мс
        self.after(900, lambda: self.copy_button.configure(text="Скопировать X, Y"))


# ------------------------------------------------------------
# Точка входа
# ------------------------------------------------------------
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = CoordFinder()
    app.mainloop()