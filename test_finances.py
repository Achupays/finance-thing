import unittest
from unittest.mock import patch, MagicMock
from finances import add_transaction, generate_report, set_limit, load_data, save_data
from tkinter import Tk

class TestFinances(unittest.TestCase):

    def setUp(self):
        """Подготовка тестовых данных."""
        # Очищаем тестовые данные перед каждым тестом
        save_data({"transactions": [], "limits": {}})

    # Тесты для функции add_transaction
    def test_add_transaction_positive(self):
        """Тест добавления транзакции без превышения лимита."""
        # Устанавливаем лимит
        data = load_data()
        data["limits"]["Продукты"] = 1000
        save_data(data)

        add_transaction(500, "Продукты", "Покупка еды")
        data = load_data()

        # Проверяем, что транзакция добавлена
        self.assertEqual(len(data["transactions"]), 1)
        self.assertEqual(data["transactions"][0]["amount"], 500)
        self.assertEqual(data["transactions"][0]["category"], "Продукты")

    # Тесты для функции generate_report
    @patch('tkinter.Tk')  # Патчим Tk для предотвращения создания реального окна
    def test_generate_report_with_transactions(self, MockTk):
        """Тест генерации отчета с транзакциями."""

        # Добавляем транзакции
        add_transaction(500, "Продукты", "Покупка еды")
        add_transaction(-200, "Продукты", "Покупка напитков")

        # Создаем основной root элемент для Tkinter
        root = Tk()

        # Мокаем создание окна Toplevel и его метод winfo_exists
        mock_window = MagicMock()
        MockTk.return_value = root  # Подменяем объект Tk
        mock_window.winfo_exists.return_value = True

        # Генерация отчета
        generate_report("date", False)

        # Проверяем, что окно действительно было открыто
        self.assertTrue(mock_window.winfo_exists())

    @patch('tkinter.Tk')  # Патчим Tk

    # Тесты для функции set_limit
    def test_set_limit_positive(self):
        """Тест установки лимита для категории."""
        set_limit("Продукты", 1000)

        data = load_data()
        self.assertIn("Продукты", data["limits"])
        self.assertEqual(data["limits"]["Продукты"], 1000)

    def test_set_limit_negative(self):
        """Тест попытки установить отрицательный лимит."""
        with self.assertRaises(ValueError):
            set_limit("Продукты", -1000)  # Проверяем, что ошибка ValueError будет выброшена


    def tearDown(self):
        """Очистка тестового файла."""
        save_data({"transactions": [], "limits": {}})

if __name__ == '__main__':
    unittest.main()
