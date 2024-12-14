import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

DATA_FILE = "finances.json"


def load_data():
    """Загружает данные из файла или создает пустую структуру.

    Если файл данных не существует, создается структура с пустыми транзакциями и лимитами.

    Returns:
        dict: Структура данных с транзакциями и лимитами.
    """
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"transactions": [], "limits": {}}


def save_data(data):
    """Сохраняет данные в файл.

    Сохраняет переданные данные в файл DATA_FILE в формате JSON.

    Args:
        data (dict): Данные, которые нужно сохранить.
    """
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def add_transaction(amount, category, note=""):
    """Добавляет транзакцию и проверяет превышение бюджета по категории.

    Добавляет транзакцию с указанной суммой, категорией и примечанием в список транзакций.
    Если для категории установлен лимит, проверяется, не превышен ли он.

    Args:
        amount (float): Сумма транзакции (может быть отрицательной для списаний).
        category (str): Категория транзакции.
        note (str, optional): Примечание к транзакции. По умолчанию пустое.

    Raises:
        ValueError: Если категория не указана или сумма некорректна.
    """
    data = load_data()
    transaction_type = "списание" if amount < 0 else "начисление"
    transaction = {
        "amount": float(amount),
        "category": category,
        "note": note,
        "date": datetime.now().isoformat(),  # Здесь записывается дата с миллисекундами
        "type": transaction_type,
    }

    # Проверка лимита категории
    category_limit = data["limits"].get(category, None)
    if category_limit is not None:
        total_amount_in_category = sum(t["amount"] for t in data["transactions"] if t["category"] == category)
        new_total_amount = total_amount_in_category + float(amount)
        if new_total_amount > category_limit:
            messagebox.showwarning("Предупреждение",
                                   f"Лимит для категории '{category}' превышен! Ваши текущие расходы: {new_total_amount:.2f}, лимит: {category_limit:.2f}")

    data["transactions"].append(transaction)
    save_data(data)
    messagebox.showinfo("Успех", f"Транзакция ({transaction_type}) успешно добавлена!")


def calculate_balance():
    """Возвращает текущий баланс.

    Рассчитывает баланс как сумму всех транзакций (начислений и списаний).

    Returns:
        float: Текущий баланс.
    """
    data = load_data()
    return sum(t["amount"] for t in data["transactions"])


def generate_report(sort_by="date", reverse=False, start_date=None, end_date=None, category=None):
    """Генерирует отчет о транзакциях с сортировкой и фильтрацией по диапазону дат и категории.

    Генерирует отчет по транзакциям с возможностью фильтрации по дате, категории
    и сортировки по дате, сумме или категории.

    Args:
        sort_by (str, optional): Поле для сортировки ("date", "amount", "category", "note"). По умолчанию "date".
        reverse (bool, optional): Направление сортировки. По умолчанию False (по возрастанию).
        start_date (str, optional): Дата начала периода в формате "ДД.ММ.ГГГГ".
        end_date (str, optional): Дата конца периода в формате "ДД.ММ.ГГГГ".
        category (str, optional): Категория для фильтрации транзакций.
    """
    data = load_data()
    transactions = data["transactions"]

    # Фильтрация транзакций по диапазону дат, если указаны
    if start_date or end_date:
        try:
            # Преобразуем строки в даты
            if start_date:
                start_date = datetime.strptime(start_date, "%d.%m.%Y")
            if end_date:
                end_date = datetime.strptime(end_date, "%d.%m.%Y")

            # Фильтруем транзакции по диапазону
            transactions = [t for t in transactions if
                            (start_date is None or datetime.strptime(t["date"],
                                                                     "%Y-%m-%dT%H:%M:%S.%f") >= start_date) and
                            (end_date is None or datetime.strptime(t["date"], "%Y-%m-%dT%H:%M:%S.%f") <= end_date)]
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте DD.MM.YYYY.")
            return

    # Фильтрация по категории
    if category:
        transactions = [t for t in transactions if t["category"] == category]

    # Сортировка
    if sort_by == "дата":
        key = lambda t: t["date"]
    elif sort_by == "сумма":
        key = lambda t: t["amount"]
    elif sort_by == "категория":
        key = lambda t: t["category"]
    else:
        key = lambda t: t["note"]

    sorted_transactions = sorted(transactions, key=key, reverse=reverse)

    # Окно отчета
    report_window = tk.Toplevel()
    report_window.title(f"Отчет (сортировка по {sort_by}, {'убыванию' if reverse else 'возрастанию'})")
    ttk.Label(report_window, text="Дата", width=25, anchor="w").grid(row=0, column=0)
    ttk.Label(report_window, text="Сумма", width=10, anchor="w").grid(row=0, column=1)
    ttk.Label(report_window, text="Тип", width=15, anchor="w").grid(row=0, column=2)
    ttk.Label(report_window, text="Категория", width=20, anchor="w").grid(row=0, column=3)
    ttk.Label(report_window, text="Примечание", width=30, anchor="w").grid(row=0, column=4)

    for idx, t in enumerate(sorted_transactions):
        formatted_date = datetime.strptime(t["date"], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d.%m.%y, %H:%M:%S")
        ttk.Label(report_window, text=formatted_date).grid(row=idx + 1, column=0)
        ttk.Label(report_window, text=f"{t['amount']:.2f}").grid(row=idx + 1, column=1)
        ttk.Label(report_window, text=t["type"]).grid(row=idx + 1, column=2)
        ttk.Label(report_window, text=t["category"]).grid(row=idx + 1, column=3)
        ttk.Label(report_window, text=t["note"]).grid(row=idx + 1, column=4)


def set_limit(category, limit):
    """Устанавливает лимит для категории.

    Устанавливает лимит для указанной категории.Так же проверяет положительность лимита.

    Args:
        category (str): Категория, для которой устанавливается лимит.
        limit (float): Лимит для указанной категории.
    """
    if limit < 0:
        raise ValueError("Лимит не может быть отрицательным.")
    data = load_data()
    data["limits"][category] = float(limit)
    save_data(data)
    messagebox.showinfo("Успех", f"Лимит для категории '{category}' установлен на {limit}")


# Графический интерфейс
def create_gui():
    """Создает графический интерфейс.

    Создает окно с возможностью добавления транзакций, просмотра баланса,
    генерации отчетов и установки лимитов для категорий.
    """
    root = tk.Tk()
    root.title("Управление личными финансами")

    # Добавление транзакции
    ttk.Label(root, text="Добавить транзакцию").grid(row=0, column=0, columnspan=2, pady=5)
    ttk.Label(root, text="Сумма:").grid(row=1, column=0, sticky="w")
    amount_entry = ttk.Entry(root)
    amount_entry.grid(row=1, column=1, padx=5)

    ttk.Label(root, text="Категория:").grid(row=2, column=0, sticky="w")
    category_entry = ttk.Entry(root)
    category_entry.grid(row=2, column=1, padx=5)

    ttk.Label(root, text="Примечание:").grid(row=3, column=0, sticky="w")
    note_entry = ttk.Entry(root)
    note_entry.grid(row=3, column=1, padx=5)

    def handle_add_transaction():
        try:
            amount = float(amount_entry.get())
            category = category_entry.get()
            note = note_entry.get()
            if not category:
                raise ValueError("Категория не может быть пустой.")
            add_transaction(amount, category, note)
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")

    ttk.Button(root, text="Добавить", command=handle_add_transaction).grid(row=4, column=0, columnspan=2, pady=10)

    # Просмотр баланса
    ttk.Label(root, text="Текущий баланс:").grid(row=5, column=0, sticky="w")
    balance_label = ttk.Label(root, text=f"{calculate_balance():.2f}")
    balance_label.grid(row=5, column=1, sticky="w")

    def update_balance():
        balance_label.config(text=f"{calculate_balance():.2f}")

    ttk.Button(root, text="Обновить баланс", command=update_balance).grid(row=6, column=0, columnspan=2, pady=5)

    # Генерация отчета с сортировкой
    ttk.Label(root, text="Отчет (сортировка по):").grid(row=7, column=0, pady=5)
    sort_by_combobox = ttk.Combobox(root, values=["дата", "сумма"], state="readonly")
    sort_by_combobox.grid(row=7, column=1)
    sort_by_combobox.set("дата")

    sort_order_var = tk.BooleanVar(value=False)
    sort_order_checkbox = ttk.Checkbutton(root, text="Сортировать по убыванию", variable=sort_order_var)
    sort_order_checkbox.grid(row=8, column=0, columnspan=2)

    # Ввод даты начала и конца периода
    ttk.Label(root, text="Дата начала (ДД.ММ.ГГГГ):").grid(row=9, column=0, sticky="w")
    start_date_entry = ttk.Entry(root)
    start_date_entry.grid(row=9, column=1, padx=5)

    ttk.Label(root, text="Дата конца (ДД.ММ.ГГГГ):").grid(row=10, column=0, sticky="w")
    end_date_entry = ttk.Entry(root)
    end_date_entry.grid(row=10, column=1, padx=5)

    # Выбор категории
    data = load_data()
    existing_categories = list(set(t["category"] for t in data["transactions"]))
    ttk.Label(root, text="Выберите категорию для отчета:").grid(row=11, column=0, sticky="w")
    category_combobox = ttk.Combobox(root, values=existing_categories, state="readonly")
    category_combobox.grid(row=11, column=1)

    def handle_generate_report():
        sort_by = sort_by_combobox.get()
        reverse = sort_order_var.get()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        category = category_combobox.get()
        generate_report(sort_by, reverse, start_date, end_date, category)

    ttk.Button(root, text="Сгенерировать отчет", command=handle_generate_report).grid(row=12, column=0, columnspan=2,
                                                                                      pady=5)

    # Установка лимита
    ttk.Label(root, text="Установить лимит").grid(row=13, column=0, columnspan=2, pady=5)
    ttk.Label(root, text="Категория:").grid(row=14, column=0, sticky="w")
    limit_category_entry = ttk.Entry(root)
    limit_category_entry.grid(row=14, column=1, padx=5)

    ttk.Label(root, text="Лимит:").grid(row=15, column=0, sticky="w")
    limit_entry = ttk.Entry(root)
    limit_entry.grid(row=15, column=1, padx=5)

    def handle_set_limit():
        try:
            category = limit_category_entry.get()
            limit = float(limit_entry.get())
            if not category:
                raise ValueError("Категория не может быть пустой.")
            set_limit(category, limit)
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")

    ttk.Button(root, text="Установить", command=handle_set_limit).grid(row=16, column=0, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
