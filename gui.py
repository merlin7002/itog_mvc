"""
Интерфейс графического приложения для управления интернет-магазином.
Реализует управление клиентами, товарами, заказами и аналитические отчёты.
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import networkx as nx
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from controllers import AppController

class MainApp(tk.Tk):
    """
    Главный класс приложения для управления интернет-магазином.

    Attributes
    ----------
    title : str
        Заголовок окна приложения.
    geometry : str
        Размер окна приложения.
    controller : AppController
        Контроллер для взаимодействия с бизнес-логикой.
    sort_params : dict
        Параметры сортировки данных.
    search_entries : dict
        Словарь для хранения ссылок на поля поиска.
    """

    def __init__(self):
        """
        Инициализация главного окна приложения.
        """
        super().__init__()
        plt.ioff()
        self.title("Интернет-магазин | Менеджмент клиентов и заказов")
        self.geometry("1200x800")
        self.controller = AppController(self)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Treeview.Heading', background='lightyellow')
        self.create_menus()
        self.sort_params = {"heading": "id", "id": "asc"}  # Глобальная переменная для хранения настроек сортировки
        # Изначально создаем пустой словарь для ссылок на поля поиска
        self.search_entries = {
            "customers": None,
            "products": None,
            "orders": None
        }
        self.create_tabs()

    def create_menus(self):
        """
        Создание пунктов меню в приложении.
        """
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Выход", command=self.quit)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="О программе", command=self.show_about_dialog)
        menu_bar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menu_bar)
        # Протокол для обработки события закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """
        Обработчик события закрытия окна.
        """
        self.quit()

    def show_about_dialog(self):
        """
        Показ информационного окна о программе.
        """
        messagebox.showinfo("О программе", "Программа для управления магазином\nВерсия 2.0\nАвтор: Фёдоров Алексей")

    def create_tabs(self):
        """
        Создание вкладок в главном окне приложения.
        """
        tab_control = ttk.Notebook(self)
        self.tab_customers = ttk.Frame(tab_control)
        self.tab_products = ttk.Frame(tab_control)
        self.tab_orders = ttk.Frame(tab_control)
        self.tab_analysis = ttk.Frame(tab_control)

        tab_control.add(self.tab_customers, text="Клиенты")
        tab_control.add(self.tab_products, text="Товары")
        tab_control.add(self.tab_orders, text="Заказы")
        tab_control.add(self.tab_analysis, text="Аналитика и визуализация")
        tab_control.pack(expand=True, fill="both")

        self.setup_customers_tab()
        self.setup_products_tab()
        self.setup_orders_tab()
        self.setup_analysis_tab()

    def clear_search_field(self, section):
        """
        Очистка поискового поля для заданной вкладки.

        Parameters
        ----------
        section : str
            Идентификатор вкладки ('customers', 'products', 'orders'), определяющий, какое поле поиска очищать.
        """
        if section is None:
            # Чистка всех полей сразу
            for entry in self.search_entries.values():
                if entry is not None:
                    entry.delete(0, tk.END)
        else:
            # Чистка конкретного поля
            entry = self.search_entries[section]
            if entry is not None:
                entry.delete(0, tk.END)
        # Дополнительно перезагрузить соответствующие данные
        if section == "customers":
            self.load_customers()
        elif section == "products":
            self.load_products()
        elif section == "orders":
            self.load_orders()

    def setup_customers_tab(self):
        """
        Настройка вкладки "Клиенты".
        """
        frame = ttk.LabelFrame(self.tab_customers, text="Управление клиентами")
        frame.pack(padx=10, pady=10, fill="x", side="top", expand=True, anchor="n")

        # Поиск клиента
        search_frame = ttk.Frame(frame)
        search_label = ttk.Label(search_frame, text="Поиск клиентов:")
        search_label.pack(side="left")
        clear_button = ttk.Button(search_frame, text="Очистить", command=lambda: self.clear_search_field('customers'))
        clear_button.pack(side="right", pady=5)
        search_button = ttk.Button(search_frame, text="Искать", command=self.search_customers)
        search_button.pack(side="right")
        self.search_var = tk.StringVar()
        self.search_entries["customers"] = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entries["customers"].pack(side="right")
        search_frame.pack(fill="x", padx=5, pady=5)

        # Дерево результатов поиска
        tree_columns = ("ID", "Имя", "Электронная почта", "Телефон")
        self.customers_treeview = ttk.Treeview(frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            self.customers_treeview.heading(col, text=col)
        self.customers_treeview.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.customers_treeview.yview)
        scrollbar.pack(side="right", fill="y")
        self.customers_treeview.configure(yscrollcommand=scrollbar.set)

        # Панель действий
        actions_frame = ttk.Frame(frame)
        add_button = ttk.Button(actions_frame, text="Добавить клиента", command=self.open_add_customer_dialog)
        edit_button = ttk.Button(actions_frame, text="Редактировать клиента", command=self.edit_selected_customer)
        del_button = ttk.Button(actions_frame, text="Удалить клиента", command=self.delete_selected_customer)
        export_button = ttk.Button(actions_frame, text="Экспорт в CSV/JSON", command=self.export_customers)
        import_button = ttk.Button(actions_frame, text="Импорт из CSV/JSON", command=self.import_customers)
        add_button.pack(side="left", padx=5)
        edit_button.pack(side="left", padx=5)
        del_button.pack(side="left", padx=5)
        export_button.pack(side="left", padx=5)
        import_button.pack(side="left", padx=5)
        actions_frame.pack(fill="x", padx=5, pady=5)

        # Загрузка данных при запуске
        self.load_customers()

    def load_customers(self):
        """
        Обновляет дерево клиентов на основании данных, полученных от контроллера.
        """
        customers = self.controller.load_customers()
        self.customers_treeview.delete(*self.customers_treeview.get_children())
        for cust in customers:
            self.customers_treeview.insert("", "end", values=(cust.id, cust.name, cust.email, cust.phone))

    def search_customers(self):
        """
        Осуществляет поиск клиентов по введенному запросу.
        """
        keyword = self.search_var.get().strip()
        filtered_customers = self.controller.search_customers(keyword)
        self.customers_treeview.delete(*self.customers_treeview.get_children())
        for cust in filtered_customers:
            self.customers_treeview.insert("", "end", values=(cust.id, cust.name, cust.email, cust.phone))

    def open_add_customer_dialog(self):
        """
        Открывает диалоговое окно для добавления нового клиента.
        """
        AddCustomerDialog(self)

    def edit_selected_customer(self):
        """
        Открывает диалоговое окно для редактирования выбранного клиента.
        """
        selected = self.customers_treeview.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента перед редактированием!")
            return
        item = self.customers_treeview.item(selected[0])["values"]
        EditCustomerDialog(self, customer_id=int(item[0]))

    def delete_selected_customer(self):
        """
        Удаляет выбранного клиента.
        """
        selected = self.customers_treeview.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента перед удалением!")
            return
        item = self.customers_treeview.item(selected[0])["values"]
        confirmation = messagebox.askyesno(
            "Подтверждение удаления",
            f"Удалить клиента '{item[1]}'?"
        )
        if confirmation:
            res = self.controller.delete_customer(int(item[0]))
            if res[0]:
                messagebox.showwarning("Подтверждение", f"Клиент {item[1]} удален!")
                self.load_customers()
                self.load_analysis()
            else:
                messagebox.showwarning("Ошибка", res[1])

    def export_customers(self):
        """
        Экспорт клиентов в выбранный формат (CSV или JSON).
        """
        filename = asksaveasfilename(defaultextension=".csv", filetypes=[
            ("CSV files", "*.csv"),
            ("JSON files", "*.json")
        ])
        if filename:
            extension = filename.rsplit('.', 1)[-1].lower()
            success, error_msg = self.controller.export_data(filename, "customers", extension)
            if success:
                messagebox.showinfo("Экспорировано", f"Данные успешно экспортированы в файл {filename}.")
            else:
                messagebox.showerror("Ошибка экспорта", f"Возникла ошибка при экспорте: {error_msg}")

    def import_customers(self):
        """
        Импорт клиентов из файла (CSV или JSON).
        """
        filename = askopenfilename(filetypes=[
            ("CSV files", "*.csv"),
            ("JSON files", "*.json")
        ])
        if filename:
            extension = filename.rsplit('.', 1)[-1].lower()
            success, error_msg = self.controller.import_data(filename, "customers", extension)
            if success:
                messagebox.showinfo("Импорт завершен", f"Данные успешно импортированы из файла {filename}.")
                self.load_customers()
                self.load_analysis()
            else:
                messagebox.showerror("Ошибка импорта", f"Возникла ошибка при импорте: {error_msg}")

    def setup_products_tab(self):
        """
        Настройка вкладки "Товары".
        """
        frame = ttk.LabelFrame(self.tab_products, text="Управление товарами")
        frame.pack(padx=10, pady=10, fill="x", side="top", expand=True, anchor="n")

        # Поиск товара
        search_frame = ttk.Frame(frame)
        search_label = ttk.Label(search_frame, text="Поиск товаров:")
        search_label.pack(side="left")
        clear_button = ttk.Button(search_frame, text="Очистить", command=lambda: self.clear_search_field('products'))
        clear_button.pack(side="right", pady=5)
        search_button = ttk.Button(search_frame, text="Искать", command=self.search_products)
        search_button.pack(side="right")
        self.search_prod_var = tk.StringVar()
        self.search_entries["products"] = ttk.Entry(search_frame, textvariable=self.search_prod_var)
        self.search_entries["products"].pack(side="right")
        search_frame.pack(fill="x", padx=5, pady=5)

        # Дерево результатов поиска
        tree_columns = ("ID", "Название", "Цена", "Количество")
        self.products_treeview = ttk.Treeview(frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            self.products_treeview.heading(col, text=col)
        self.products_treeview.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.products_treeview.yview)
        scrollbar.pack(side="right", fill="y")
        self.products_treeview.configure(yscrollcommand=scrollbar.set)

        # Панель действий
        actions_frame = ttk.Frame(frame)
        add_button = ttk.Button(actions_frame, text="Добавить товар", command=self.open_add_product_dialog)
        edit_button = ttk.Button(actions_frame, text="Редактировать товар", command=self.edit_selected_product)
        del_button = ttk.Button(actions_frame, text="Удалить товар", command=self.delete_selected_product)
        export_button = ttk.Button(actions_frame, text="Экспорт в CSV/JSON", command=self.export_products)
        import_button = ttk.Button(actions_frame, text="Импорт из CSV/JSON", command=self.import_products)
        add_button.pack(side="left", padx=5)
        edit_button.pack(side="left", padx=5)
        del_button.pack(side="left", padx=5)
        export_button.pack(side="left", padx=5)
        import_button.pack(side="left", padx=5)
        actions_frame.pack(fill="x", padx=5, pady=5)

        # Загрузка данных при запуске
        self.load_products()

    def load_products(self):
        """
        Обновляет дерево товаров на основании данных, полученных от контроллера.
        """
        products = self.controller.load_products()
        self.products_treeview.delete(*self.products_treeview.get_children())
        for prod in products:
            self.products_treeview.insert("", "end", values=(prod.id, prod.name, prod.price, prod.quantity))

    def search_products(self):
        """
        Осуществляет поиск товаров по введенному запросу.
        """
        keyword = self.search_prod_var.get().strip()
        filtered_products = self.controller.search_products(keyword)
        self.products_treeview.delete(*self.products_treeview.get_children())
        for prod in filtered_products:
            self.products_treeview.insert("", "end", values=(prod.id, prod.name, prod.price, prod.quantity))

    def open_add_product_dialog(self):
        """
        Открывает диалоговое окно для добавления нового товара.
        """
        AddProductDialog(self)

    def edit_selected_product(self):
        """
        Открывает диалоговое окно для редактирования выбранного товара.
        """
        selected = self.products_treeview.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите товар перед редактированием!")
            return
        item = self.products_treeview.item(selected[0])["values"]
        EditProductDialog(self, product_id=int(item[0]))

    def delete_selected_product(self):
        """
        Удаляет выбранный товар.
        """
        selected = self.products_treeview.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите товар перед удалением!")
            return
        item = self.products_treeview.item(selected[0])["values"]
        confirmation = messagebox.askyesno(
            "Подтверждение удаления",
            f"Удалить товар '{item[1]}'?"
        )
        if confirmation:
            res = self.controller.delete_product(int(item[0]))
            if res[0]:
                messagebox.showwarning("Подтверждение", f"Товар '{item[1]}' удален!")
                self.load_products()
                self.load_analysis()
            else:
                messagebox.showwarning("Ошибка", res[1])

    def export_products(self):
        """
        Экспорт товаров в выбранный формат (CSV или JSON).
        """
        filename = asksaveasfilename(defaultextension=".csv", filetypes=[
            ("CSV files", "*.csv"),
            ("JSON files", "*.json")
        ])
        if filename:
            extension = filename.rsplit('.', 1)[-1].lower()
            success, error_msg = self.controller.export_data(filename, "products", extension)
            if success:
                messagebox.showinfo("Экспорировано", f"Данные успешно экспортированы в файл {filename}.")
            else:
                messagebox.showerror("Ошибка экспорта", f"Возникла ошибка при экспорте: {error_msg}")

    def import_products(self):
        """
        Импорт товаров из файла (CSV или JSON).
        """
        filename = askopenfilename(filetypes=[
            ("CSV files", "*.csv"),
            ("JSON files", "*.json")
        ])
        if filename:
            extension = filename.rsplit('.', 1)[-1].lower()
            success, error_msg = self.controller.import_data(filename, "products", extension)
            if success:
                messagebox.showinfo("Импорт завершен", f"Данные успешно импортированы из файла {filename}.")
                self.load_products()
                self.load_analysis()
            else:
                messagebox.showerror("Ошибка импорта", f"Возникла ошибка при импорте: {error_msg}")

    def setup_orders_tab(self):
        """
        Настройка вкладки "Заказы".
        """
        frame = ttk.LabelFrame(self.tab_orders, text="Управление заказами")
        frame.pack(padx=10, pady=10, fill="x", side="top", expand=True, anchor="n")

        # Поиск заказа
        search_frame = ttk.Frame(frame)
        search_label = ttk.Label(search_frame, text="Поиск заказов:")
        search_label.pack(side="left")
        clear_button = ttk.Button(search_frame, text="Очистить", command=lambda: self.clear_search_field('orders'))
        clear_button.pack(side="right", pady=5)
        search_button = ttk.Button(search_frame, text="Искать", command=self.search_orders)
        search_button.pack(side="right")
        self.search_ord_var = tk.StringVar()
        self.search_entries["orders"] = ttk.Entry(search_frame, textvariable=self.search_ord_var)
        self.search_entries["orders"].pack(side="right")
        search_frame.pack(fill="x", padx=5, pady=5)

        # Дерево результатов поиска
        tree_columns = ("ID", "Покупатель", "Дата создания", "Статус заказа", "Итоговая сумма")
        self.orders_treeview = ttk.Treeview(frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            if col in ["ID", "Дата создания", "Итоговая сумма"]:
                # Назначаем обработчики только для этих колонок
                self.orders_treeview.heading(col, text=col, command=lambda c=col: self.sort_orders(c))
            else:
                # Остальные колонки остаются без обработчика
                self.orders_treeview.heading(col, text=col)
            # Установка минимальной ширины колонок
            if col == "Итоговая сумма":
                self.orders_treeview.column(col, minwidth=100, width=155, stretch=True)
            else:
                self.orders_treeview.column(col, minwidth=100, width=155, stretch=True)
        self.orders_treeview.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.orders_treeview.yview)
        scrollbar.pack(side="right", fill="y")
        self.orders_treeview.configure(yscrollcommand=scrollbar.set)

        # Панель действий
        actions_frame = ttk.Frame(frame)
        add_button = ttk.Button(actions_frame, text="Добавить заказ", command=self.open_add_order_dialog)
        edit_button = ttk.Button(actions_frame, text="Редактировать заказ", command=self.edit_selected_order)
        del_button = ttk.Button(actions_frame, text="Удалить заказ", command=self.delete_selected_order)
        export_button = ttk.Button(actions_frame, text="Экспорт в CSV/JSON", command=self.export_orders)
        import_button = ttk.Button(actions_frame, text="Импорт из CSV/JSON", command=self.import_orders)
        add_button.pack(side="left", padx=5)
        edit_button.pack(side="left", padx=5)
        del_button.pack(side="left", padx=5)
        export_button.pack(side="left", padx=5)
        import_button.pack(side="left", padx=5)
        actions_frame.pack(fill="x", padx=5, pady=5)

        # Загрузка данных при запуске
        self.load_orders()

    def sort_orders(self, column):
        """
        Сортирует заказы по указанному полю.

        Parameters
        ----------
        column : str
            Название колонки для сортировки.
        """
        # Получаем текущее направление сортировки для указанного столбца
        new_column = 'id'
        if column == 'Дата создания':
            new_column = 'date'
        elif column == 'Итоговая сумма':
            new_column = 'amount'
        current_dir = self.sort_params.get(new_column, "asc")
        # Переключаем направление сортировки
        new_dir = "desc" if current_dir == "asc" else "asc"
        self.sort_params = {
            "heading": new_column,
            new_column: new_dir
        }
        # Обновляем список заказов с учётом новых параметров сортировки
        self.load_orders()

    def load_orders(self):
        """
        Обновляет дерево заказов на основании данных, полученных от контроллера.
        """
        orders = self.controller.load_sort_orders(self.sort_params)
        self.orders_treeview.delete(*self.orders_treeview.get_children())
        for ord in orders:
            # Получаем имя покупателя по идентификатору
            customer = self.controller.find_customer_by_id(ord.customer_id)
            customer_name = customer.name if customer else "Покупатель не найден"

            # Вставляем данные в дерево заказов
            self.orders_treeview.insert("", "end",
                                        values=(ord.id, customer_name, ord.date_created, ord.status, ord.total_amount))

    def search_orders(self):
        """
        Осуществляет поиск заказов по введенному запросу.
        """
        keyword = self.search_ord_var.get().strip()
        filtered_orders = self.controller.search_orders(keyword)
        self.orders_treeview.delete(*self.orders_treeview.get_children())
        for ord in filtered_orders:
            # Получаем имя покупателя по идентификатору
            customer = self.controller.find_customer_by_id(ord.customer_id)
            customer_name = customer.name if customer else "Не найден"

            # Вставляем данные в дерево заказов
            self.orders_treeview.insert("", "end",
                                        values=(ord.id, customer_name, ord.date_created, ord.status, ord.total_amount))

    def open_add_order_dialog(self):
        """
        Открывает диалоговое окно для добавления нового заказа.
        """
        AddOrderDialog(self, controller=self.controller)

    def edit_selected_order(self):
        """
        Открывает диалоговое окно для редактирования выбранного заказа.
        """
        selected = self.orders_treeview.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ перед редактированием!")
            return
        item = self.orders_treeview.item(selected[0])["values"]
        EditOrderDialog(self, order_id=int(item[0]), controller=self.controller)

    def delete_selected_order(self):
        """
        Удаляет выбранный заказ.
        """
        selected = self.orders_treeview.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ перед удалением!")
            return
        item = self.orders_treeview.item(selected[0])["values"]
        confirmation = messagebox.askyesno(
            "Подтверждение удаления",
            f"Удалить заказ #{item[0]}?"
        )
        if confirmation:
            self.controller.delete_order(int(item[0]))
            self.load_orders()
            self.load_analysis()

    def export_orders(self):
        """
        Экспорт заказов в выбранный формат (CSV или JSON).
        """
        filename = asksaveasfilename(defaultextension=".csv", filetypes=[
            ("CSV files", "*.csv"),
            ("JSON files", "*.json")
        ])
        if filename:
            extension = filename.rsplit('.', 1)[-1].lower()
            success, error_msg = self.controller.export_data(filename, 'orders-details', extension)
            if success:
                messagebox.showinfo("Экспорировано", f"Данные успешно экспортированы в файл {filename}.")
            else:
                messagebox.showerror("Ошибка экспорта", f"Возникла ошибка при экспорте: {error_msg}")

    def import_orders(self):
        """
        Импорт заказов из файла (CSV или JSON).
        """
        filename = askopenfilename(filetypes=[
            ("CSV files", "*.csv"),
            ("JSON files", "*.json")
        ])
        if filename:
            extension = filename.rsplit('.', 1)[-1].lower()
            success, error_msg = self.controller.import_data(filename, 'orders-details', extension)
            if success:
                messagebox.showinfo("Импорт завершен", f"Данные успешно импортированы из файла {filename}.")
                self.load_orders()
                self.load_analysis()
            else:
                messagebox.showerror("Ошибка импорта", f"Возникла ошибка при импорте: {error_msg}")

    def setup_analysis_tab(self):
        """
        Настройка вкладки "Аналитика и визуализация".
        """
        frame = ttk.LabelFrame(self.tab_analysis, text="Аналитика и визуализация")
        frame.pack(padx=10, pady=10, fill="x", side="top", expand=True, anchor="n")

        # Внешний фрейм для графиков
        graphs_frame = ttk.Frame(frame)
        graphs_frame.pack(fill="both", expand=True)

        # Внутренние фреймы для верхнего ряда (два первых графика)
        upper_row_frame = ttk.Frame(graphs_frame)
        upper_row_frame.pack(fill="both", expand=True)

        # Внутренние фреймы для ограничения роста графиков
        self.canvas1_frame = ttk.Frame(upper_row_frame, width=600, height=400)
        self.canvas1_frame.pack_propagate(False)
        self.canvas1_frame.pack(side=tk.LEFT, fill="none", expand=False)

        self.canvas2_frame = ttk.Frame(upper_row_frame, width=600, height=400)
        self.canvas2_frame.pack_propagate(False)
        self.canvas2_frame.pack(side=tk.RIGHT, fill="none", expand=False)

        # Внутренний фрейм для нижнего ряда (третий график)
        lower_row_frame = ttk.Frame(graphs_frame)
        lower_row_frame.pack(fill="both", expand=True, side="bottom", anchor="s")

        self.graph_canvas_frame = ttk.Frame(lower_row_frame, width=1200, height=400)
        self.graph_canvas_frame.pack_propagate(False)
        self.graph_canvas_frame.pack(fill="both", expand=True)
        self.load_analysis()

    def build_fig1(self, data):
        """
        Создает первую диаграмму (топ-5 клиентов по количеству заказов).

        Parameters
        ----------
        data : pandas.DataFrame
            Данные для построения диаграммы.
        """
        fig1 = Figure(figsize=(4, 4), dpi=80)
        ax1 = fig1.add_subplot(111)

        # Строим гистограмму используя plt.bar
        ax1.bar(data['name'], data['number_of_orders'])
        ax1.set_xlabel('Покупатели')
        ax1.set_ylabel('Количество заказов')
        ax1.set_title('ТОП-5 покупателей по числу заказов')
        ax1.tick_params(axis='x', rotation=15)
        plt.tight_layout()  # Оптимизация расположения графики
        canvas1 = FigureCanvasTkAgg(fig1, master=self.canvas1_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def build_fig2(self, data):
        """
        Создает вторую диаграмму (количество заказов по датам).

        Parameters
        ----------
        data : pandas.DataFrame
            Данные для построения диаграммы.
        """
        fig2 = Figure(figsize=(4, 4), dpi=80)
        ax2 = fig2.add_subplot(111)

        # Строим линейный график
        ax2.plot(data['date_created'], data['counts'], marker='o')  # Добавляем маркер точек 'o'
        ax2.set_xlabel('Даты')
        ax2.set_ylabel('Количество заказов')
        ax2.set_title('Динамика количества заказов по датам')
        ax2.grid(True)  # Включаем сетку для удобства восприятия
        plt.tight_layout()  # Подгонка размеров элементов
        canvas2 = FigureCanvasTkAgg(fig2, master=self.canvas2_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def build_fig3(self, data):
        """
        Создает третий график (граф связей покупателей по общим товарам).

        Parameters
        ----------
        data : list of tuples
            Список ребер графа для NetworkX.
        """
        G = nx.Graph()
        G.add_weighted_edges_from(data)

        # Визуализация графа
        pos = nx.spring_layout(G)
        figure = Figure(figsize=(8, 3), dpi=80)
        ax = figure.add_subplot(111)
        nx.draw_networkx_nodes(G, pos, node_size=500, alpha=0.8, ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color='gray', ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif', ax=ax)
        ax.axis('off')
        ax.set_title('Граф связей покупателей по общим товарам')

        canvas3 = FigureCanvasTkAgg(figure, master=self.graph_canvas_frame)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_analysis(self):
        """
        Отображает аналитические графики на вкладке "Анализ".
        """
        # Получаем данные из БД
        top5_data = self.controller.fetch_top5_customers()
        opd_data = self.controller.fetch_orders_per_day()
        graph_data = self.controller.fetch_client_connections()

        # Отправляем данные для анализа
        data1 = self.controller.c_top5(top5_data)
        data2 = self.controller.c_orders_per_day(opd_data)
        data3 = self.controller.c_client_connections((graph_data))

        # Сначала удаляем существующие графики, если они есть
        for widget in self.canvas1_frame.winfo_children():
            widget.destroy()
        for widget in self.canvas2_frame.winfo_children():
            widget.destroy()
        for widget in self.graph_canvas_frame.winfo_children():
            widget.destroy()

        # Строим графики
        self.build_fig1(data1)
        self.build_fig2(data2)
        self.build_fig3(data3)

class AddCustomerDialog(tk.Toplevel):
    """
    Окно для добавления нового клиента.

    Attributes
    ----------
    parent : tk.Tk
        Родительское окно.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Добавить клиента")
        self.resizable(False, False)

        # Вспомогательные переменные для отслеживания меток с ошибками
        self.error_labels = []

        # Основной фрейм
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, padx=5, pady=5)

        # Имя
        self.label_name = ttk.Label(main_frame, text="Имя:")
        self.entry_name = ttk.Entry(main_frame)
        self.label_name.grid(row=0, column=0, sticky="W")
        self.entry_name.grid(row=0, column=1, sticky="WE")

        # Email
        self.label_email = ttk.Label(main_frame, text="Email:")
        self.entry_email = ttk.Entry(main_frame)
        self.label_email.grid(row=1, column=0, sticky="W")
        self.entry_email.grid(row=1, column=1, sticky="WE")

        # Телефон
        self.label_phone = ttk.Label(main_frame, text="Телефон:")
        self.entry_phone = ttk.Entry(main_frame)
        self.label_phone.grid(row=2, column=0, sticky="W")
        self.entry_phone.grid(row=2, column=1, sticky="WE")

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        button_save = ttk.Button(button_frame, text="Сохранить", command=self.save_customer)
        button_cancel = ttk.Button(button_frame, text="Отмена", command=self.destroy)
        button_save.grid(row=0, column=0, padx=5)
        button_cancel.grid(row=0, column=1, padx=5)

    def save_customer(self):
        """
        Передает данные клиента в контроллер для сохрания в базу данных.
        """
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()
        phone = self.entry_phone.get().strip()

        # Сбор данных
        data = {
            "name": name,
            "email": email,
            "phone": phone
        }

        # Пробуем добавить клиента через контроллер
        try:
            success, error_msg = self.parent.controller.add_customer(data)

            if success:
                #Очищаем поле поиска вкладки клиентов, заодно обновляем дерево клиентов
                self.parent.clear_search_field(section="customers")

                #Перестраиваем графики с учетом добавления нового клиента
                self.parent.load_analysis()

                # Закрываем окно только при успехе
                self.destroy()
            else:
                # Иначе показываем ошибки
                # self.display_errors(error_msg)
                messagebox.showerror("Ошибка", error_msg, parent=self)
        except Exception as err:
            messagebox.showerror("Ошибка", str(err), parent=self)

class EditCustomerDialog(tk.Toplevel):
    """
    Окно для редактирования информации о клиенте.

    Parameters
    ----------
    parent : tk.Tk
        Родительское окно.
    customer_id : int
        Уникальный идентификатор клиента.
    """

    def __init__(self, parent, customer_id):
        super().__init__(parent)
        self.parent = parent
        self.customer_id = customer_id
        self.title("Редактировать клиента")
        self.resizable(False, False)
        self.build_form()
        self.load_customer_data()

    def build_form(self):
        """
        Создает интерфейс для редактирования информации о клиенте.
        """
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=10, pady=10)

        # Поля ввода данных
        self.label_name = ttk.Label(form_frame, text="Имя:")
        self.entry_name = ttk.Entry(form_frame)
        self.label_name.grid(row=0, column=0, sticky="W")
        self.entry_name.grid(row=0, column=1, sticky="WE")

        self.label_email = ttk.Label(form_frame, text="Email:")
        self.entry_email = ttk.Entry(form_frame)
        self.label_email.grid(row=1, column=0, sticky="W")
        self.entry_email.grid(row=1, column=1, sticky="WE")

        self.label_phone = ttk.Label(form_frame, text="Телефон:")
        self.entry_phone = ttk.Entry(form_frame)
        self.label_phone.grid(row=2, column=0, sticky="W")
        self.entry_phone.grid(row=2, column=1, sticky="WE")

        # Кнопки
        button_save = ttk.Button(form_frame, text="Сохранить", command=self.save_customer)
        button_cancel = ttk.Button(form_frame, text="Отмена", command=self.destroy)
        button_save.grid(row=3, column=0, pady=10)
        button_cancel.grid(row=3, column=1, pady=10)

    def load_customer_data(self):
        """
        Загружает информацию о клиенте из контроллера и отображает её в полях ввода.
        """
        customer = self.parent.controller.find_customer_by_id(self.customer_id)
        if customer:
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, customer.name)
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, customer.email)
            self.entry_phone.delete(0, tk.END)
            self.entry_phone.insert(0, customer.phone)

    def save_customer(self):
        """
        Сохраняет изменения клиента в базу данных через контроллер.
        """
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()
        phone = self.entry_phone.get().strip()

        # Отправляем данные контроллеру
        try:
            success, error_msg = self.parent.controller.edit_customer(self.customer_id, {"name": name, "email": email, "phone": phone})
            if success:
                # Очищаем поле поиска вкладки клиентов, заодно обновляем дерево клиентов
                self.parent.clear_search_field(section="customers")

                # Перестраиваем графики с учетом добавления нового клиента
                self.parent.load_analysis()

                # Закрываем окно только при успехе
                self.destroy()
            else:
                messagebox.showerror("Ошибка", error_msg, parent=self)
        except Exception as err:
            messagebox.showerror("Ошибка", str(err), parent=self)

class AddProductDialog(tk.Toplevel):
    """
    Окно для добавления нового товара.

    Parameters
    ----------
    parent : tk.Tk
        Родительское окно.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Добавить товар")
        self.resizable(False, False)

        # Вспомогательные переменные для отслеживания меток с ошибками
        self.error_labels = []

        # Основной фрейм
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10)

        # Название товара
        self.label_name = ttk.Label(main_frame, text="Название товара:")
        self.entry_name = ttk.Entry(main_frame)
        self.label_name.grid(row=0, column=0, sticky="W")
        self.entry_name.grid(row=0, column=1, sticky="WE")

        # Цена товара
        self.label_price = ttk.Label(main_frame, text="Цена товара:")
        self.entry_price = ttk.Entry(main_frame)
        self.label_price.grid(row=1, column=0, sticky="W")
        self.entry_price.grid(row=1, column=1, sticky="WE")

        # Количество товара
        self.label_quantity = ttk.Label(main_frame, text="Количество товара:")
        self.entry_quantity = ttk.Entry(main_frame)
        self.label_quantity.grid(row=2, column=0, sticky="W")
        self.entry_quantity.grid(row=2, column=1, sticky="WE")

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        button_save = ttk.Button(button_frame, text="Сохранить", command=self.save_product)
        button_cancel = ttk.Button(button_frame, text="Отмена", command=self.destroy)
        button_save.grid(row=0, column=0, padx=5)
        button_cancel.grid(row=0, column=1, padx=5)

    def save_product(self):
        """
        Сохраняет новый товар в базу данных через контроллер.
        """
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        quantity = self.entry_quantity.get().strip()

        # Сбор данных
        data = {
            "name": name,
            "price": price,
            "quantity": quantity
        }

        # Пробуем добавить товар через контроллер
        try:
            success, error_msg = self.parent.controller.add_product(data)

            if success:
                # Очищаем поле поиска вкладки товаров, заодно обновляем дерево товаров
                self.parent.clear_search_field(section="products")

                # Перестраиваем графики с учетом добавления нового товара
                self.parent.load_analysis()

                # Закрываем окно только при успехе
                self.destroy()
            else:
                # Иначе показываем ошибки
                # self.display_errors(error_msg)
                messagebox.showerror("Ошибка", error_msg, parent=self)
        except Exception as err:
            messagebox.showerror("Ошибка", str(err), parent=self)

class EditProductDialog(tk.Toplevel):
    """
    Окно для редактирования информации о товаре.

    Parameters
    ----------
    parent : tk.Tk
        Родительское окно.
    product_id : int
        Уникальный идентификатор товара.
    """
    def __init__(self, parent, product_id):
        super().__init__(parent)
        self.parent = parent
        self.product_id = product_id
        self.title("Редактировать товар")
        self.resizable(False, False)
        self.build_form()
        self.load_product_data()

    def build_form(self):
        """
        Создает интерфейс для редактирования информации о товаре.
        """
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=10, pady=10)

        # Название товара
        self.label_name = ttk.Label(form_frame, text="Название товара:")
        self.entry_name = ttk.Entry(form_frame)
        self.label_name.grid(row=0, column=0, sticky="W")
        self.entry_name.grid(row=0, column=1, sticky="WE")

        # Цена товара
        self.label_price = ttk.Label(form_frame, text="Цена товара:")
        self.entry_price = ttk.Entry(form_frame)
        self.label_price.grid(row=1, column=0, sticky="W")
        self.entry_price.grid(row=1, column=1, sticky="WE")

        # Количество товара
        self.label_quantity = ttk.Label(form_frame, text="Количество товара:")
        self.entry_quantity = ttk.Entry(form_frame)
        self.label_quantity.grid(row=2, column=0, sticky="W")
        self.entry_quantity.grid(row=2, column=1, sticky="WE")

        # Кнопки
        button_save = ttk.Button(form_frame, text="Сохранить", command=self.save_product)
        button_cancel = ttk.Button(form_frame, text="Отмена", command=self.destroy)
        button_save.grid(row=3, column=0, pady=10)
        button_cancel.grid(row=3, column=1, pady=10)

    def load_product_data(self):
        """
        Загружает информацию о товаре из контроллера и отображает её в полях ввода.
        """
        product = self.parent.controller.find_product_by_id(self.product_id)
        if product:
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, product.name)
            self.entry_price.delete(0, tk.END)
            self.entry_price.insert(0, product.price)
            self.entry_quantity.delete(0, tk.END)
            self.entry_quantity.insert(0, product.quantity)

    def save_product(self):
        """
        Сохраняет изменения товара в базу данных через контроллер.
        """
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        quantity = self.entry_quantity.get().strip()

        # Отправляем данные контроллеру
        try:
            success, error_msg = self.parent.controller.edit_product(self.product_id, {"name": name, "price": price, "quantity": quantity})
            if success:
                # Очищаем поле поиска вкладки товаров, заодно обновляем дерево товаров
                self.parent.clear_search_field(section="products")

                # Перестраиваем графики с учетом редактирования товара
                self.parent.load_analysis()

                # Закрываем окно только при успехе
                self.destroy()
            else:
                messagebox.showerror("Ошибка", error_msg, parent=self)
        except Exception as err:
            messagebox.showerror("Ошибка", str(err), parent=self)

class AddOrderDialog(tk.Toplevel):
    """
    Диалоговое окно для создания нового заказа.

    Parameters
    ----------
    parent : tk.Tk
        Родительское окно.
    controller : AppController
        Контроллер приложения для взаимодействия с базовыми функциями.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.title("Добавить заказ")
        self.resizable(False, False)
        self.build_form()
        self.cart_items = []
        self.total_amount = 0.0

    def build_form(self):
        """
        Формирует пользовательский интерфейс для создания заказа.
        """
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=10, pady=10)

        # Верхний блок с информацией о заказе (сеточная раскладка)
        info_frame = ttk.Frame(form_frame)
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)

        # Выбор покупателя
        self.label_customer = ttk.Label(info_frame, text="Покупатель:", font=('Arial', 10))
        self.combo_customer = ttk.Combobox(info_frame, state="readonly", font=('Arial', 10))
        self.label_customer.grid(row=0, column=0, sticky="w")
        self.combo_customer.grid(row=0, column=1, sticky="w")

        # Итоговая стоимость
        self.label_total = ttk.Label(info_frame, text="Итоговая сумма:", font=('Arial', 10))
        self.label_total_value = ttk.Label(info_frame, text="", font=('Arial', 10))
        self.label_total.grid(row=1, column=0, sticky="w")
        self.label_total_value.grid(row=1, column=1, sticky="w")

        # Деревья товаров и кнопки
        composition_frame = ttk.Frame(form_frame)
        composition_frame.grid(row=1, column=0, columnspan=2, sticky="we", pady=10)

        # Дерево товаров в корзине
        self.label_composition = ttk.Label(composition_frame, text="Состав заказа:", font=('Arial', 10))
        self.label_composition.pack(side="top", anchor="w")

        self.order_items_treeview = ttk.Treeview(composition_frame, columns=("Название", "Цена", "Количество"), height=5,
                                                 show="headings")
        self.order_items_treeview.column("#1", anchor="w", width=200)
        self.order_items_treeview.column("#2", anchor="e", width=100)
        self.order_items_treeview.column("#3", anchor="e", width=100)
        self.order_items_treeview.heading("Название", text="Название")
        self.order_items_treeview.heading("Цена", text="Цена")
        self.order_items_treeview.heading("Количество", text="Количество")
        y_scrollbar = ttk.Scrollbar(composition_frame, orient="vertical", command=self.order_items_treeview.yview)
        y_scrollbar.pack(side="right", fill="y")
        self.order_items_treeview.configure(yscrollcommand=y_scrollbar.set)
        self.order_items_treeview.pack(side="top", fill="both", expand=True)

        # Входное поле для изменения количества
        self.quantity_entry = ttk.Entry(composition_frame, width=10)
        self.quantity_entry.pack(side="left", padx=5)
        btn_change_qty = ttk.Button(composition_frame, text="Изменить количество", command=self.change_quantity)
        btn_change_qty.pack(side="left", padx=5)

        # Фрейм с товарами на складе
        stock_frame = ttk.Frame(form_frame)
        stock_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=10)

        # Дерево товаров на складе
        self.label_stock = ttk.Label(stock_frame, text="Товары на складе:", font=('Arial', 10))
        self.label_stock.pack(side="top", anchor="w")

        self.stock_treeview = ttk.Treeview(stock_frame, columns=("ID", "Наименование", "Цена", "Кол-во на складе"),
                                           height=5, show="headings")
        self.stock_treeview.column("#1", anchor="w", width=50)
        self.stock_treeview.column("#2", anchor="w", width=200)
        self.stock_treeview.column("#3", anchor="e", width=100)
        self.stock_treeview.column("#4", anchor="e", width=100)
        self.stock_treeview.heading("ID", text="ID")
        self.stock_treeview.heading("Наименование", text="Наименование")
        self.stock_treeview.heading("Цена", text="Цена")
        self.stock_treeview.heading("Кол-во на складе", text="Кол-во на складе")
        y_scrollbar_stock = ttk.Scrollbar(stock_frame, orient="vertical", command=self.stock_treeview.yview)
        y_scrollbar_stock.pack(side="right", fill="y")
        self.stock_treeview.configure(yscrollcommand=y_scrollbar_stock.set)
        self.stock_treeview.pack(side="top", fill="both", expand=True)

        # Кнопка добавления товара в заказ
        btn_add_to_order = ttk.Button(stock_frame, text="Добавить в заказ", command=self.add_to_order)
        btn_add_to_order.pack(side="top", pady=5)

        # Нижняя панель с кнопками
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky="we", pady=10)

        # Кнопки
        apply_button = ttk.Button(buttons_frame, text="Оформить заказ", command=self.apply_changes)
        cancel_button = ttk.Button(buttons_frame, text="Отмена", command=self.close_window)
        apply_button.pack(side="left", padx=5)
        cancel_button.pack(side="right", padx=5)

        self.load_order_data()

    def load_order_data(self):
        """
        Загружает начальные данные заказа (список покупателей и доступные товары).
        """
        # Основные данные заказа
        # Загрузка списка покупателей
        customers = self.controller.load_customers()
        self.customer_map = {customer.name: customer.id for customer in customers}
        self.combo_customer['values'] = list(self.customer_map.keys())

        self.label_total_value.config(text="0.00 руб")

        # ОЧИСТКА ДЕРЕВА СКЛАДА ПЕРЕД ЗАГРУЗКОЙ
        self.stock_treeview.delete(*self.order_items_treeview.get_children())

        # Загружаем товары на складе
        products = self.controller.load_products()
        for product in products:
            self.stock_treeview.insert("", "end", values=(product.id, product.name, product.price, product.quantity))

    def close_window(self):
        """
        Закрывает окно без сохранения изменений.
        """
        self.destroy()

    def change_quantity(self):
        """
        Изменяет количество товара в заказе.
        """
        selected = self.order_items_treeview.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар в заказе!", parent=self)
            return

        try:
            new_quantity = int(self.quantity_entry.get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректное целое число.", parent=self)
            return

        item = self.order_items_treeview.item(selected[0])
        product_name = item["values"][0]
        product = next((p for p in self.controller.load_products() if p.name == product_name), None)
        if not product:
            messagebox.showwarning("Ошибка", "Товар не найден.", parent=self)
            return

        # Максимальное разрешённое количество товара
        max_available = product.quantity
        min_allowed = 0

        # Проверка на минимальное и максимальное количество
        if new_quantity < min_allowed or new_quantity > max_available:
            messagebox.showwarning("Ошибка",
                                   f"Для товара '{product_name}' диапазон изменения количества от {min_allowed} до {max_available}.", parent=self)
            return

        # Обновляем дерево товаров в заказе
        self.order_items_treeview.set(selected[0], column="#3", value=new_quantity)

        # Обновляем количество товара на складе (до применения изменений)
        product.quantity -= new_quantity  # Меняем количество товара на складе
        for child in self.stock_treeview.get_children():
            values = self.stock_treeview.item(child)["values"]
            if values[1] == product.name:
                self.stock_treeview.set(child, column="#4", value=product.quantity)

        # Обновляем итоговую сумму заказа
        self.update_total_amount()

        # Сообщаем пользователю об успешном изменении
        messagebox.showinfo("Информация", f"Количество товара '{product_name}' изменено на {new_quantity}.", parent=self)

    def add_to_order(self):
        """
        Добавляет товар из склада в заказ.
        """
        selected = self.stock_treeview.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар на складе!", parent=self)
            return

        if self.combo_customer.current() == -1:
            messagebox.showwarning("Внимание", "Выберите покупателя!", parent=self)
            return

        item = self.stock_treeview.item(selected[0])
        product_id = int(item["values"][0])
        product_name = item["values"][1]
        product_price = item["values"][2]
        product = self.controller.find_product_by_id(product_id)

        # Проверяем наличие товара на складе
        if product.quantity < 1:
            messagebox.showwarning("Ошибка", f"На данный момент товар '{product_name}' отсутствует на складе, добавление отменено.", parent=self)
            return

        # Проверяем, есть ли уже такой товар в списке заказа
        povtor = False
        for child in self.order_items_treeview.get_children():
            order_values = self.order_items_treeview.item(child)["values"]
            order_product_name = order_values[0]
            if order_product_name == product_name:
                # Если товар уже есть, выводим сообщение и прерываем добавление товара в заказ
                messagebox.showwarning("Ошибка",f"Товар '{product_name}' уже есть в составе заказа", parent=self)
                povtor = True
                return
        if not povtor:
            # Если товар новый, добавляем его в заказ
            self.order_items_treeview.insert("", "end", values=(product_name, product_price, 1))

        # Уменьшаем количество товара на складе (временно, до сохранения)
        product.quantity -= 1
        self.stock_treeview.set(selected[0], column="#4", value=product.quantity)

        # Обновляем итоговую сумму заказа
        self.update_total_amount()

        # Сообщаем пользователю об успешном добавлении
        messagebox.showinfo("Информация", f"Товар '{product_name}' с количеством 1 добавлен в заказ.", parent=self)

    def update_total_amount(self):
        """
        Пересчитывает общую сумму заказа исходя из текущих товаров и их цен.
        """
        total_amount = 0.0

        # Проходим по всем товарам в дереве товаров заказа
        for child in self.order_items_treeview.get_children():
            values = self.order_items_treeview.item(child)["values"]
            product_name = values[0]
            quantity = int(values[2])

            # Найти продукт по его названию
            product = next((p for p in self.controller.load_products() if p.name == product_name), None)
            if product:
                # Умножаем цену продукта на количество и добавляем к общей сумме
                total_amount += product.price * quantity

        # Обновляем метку итоговой суммы
        self.label_total_value.config(text=f"{total_amount:.2f}")
        return total_amount

    def apply_changes(self):
        """
        Оформляет заказ, отправляя данные контроллеру и закрывает окно.
        """
        # Подготовка состава заказа
        removed_items = []
        updated_items = []
        for child in self.order_items_treeview.get_children():
            values = self.order_items_treeview.item(child)["values"]
            product_name = values[0]
            quantity = int(values[2])
            product = next((p for p in self.controller.load_products() if p.name == product_name), None)
            if product:
                if quantity > 0:
                    updated_items.append({"product_id": product.id, "quantity": quantity})
                else:
                    removed_items.append(product_name)
        if self.combo_customer.current() == -1:
            messagebox.showwarning("Внимание", "Выберите покупателя!", parent=self)
            return

        if removed_items:
            messagebox.showinfo("Информация",f"В заказе товары с нулевым количеством были удалены: {', '.join(removed_items)}.", parent=self)

        if not updated_items:
            messagebox.showwarning("Внимание", "В заказе количество всех товаров изменилось на 0, заказ отменяется.", parent=self)

        # Отправляем список товаров в заказе в контроллер для записи в БД
        success, message = self.controller.process_checkout(updated_items, self.customer_map[self.combo_customer.get()])
        if success:
            messagebox.showinfo("Информация", message, parent=self)
            # Очищаем поле поиска вкладки заказов
            self.parent.clear_search_field(section="orders")

        else:
            messagebox.showwarning("Внимание", message, parent=self)
        self.destroy()

        # Обновляем интерфейс
        self.refresh_trees()
        self.destroy()  # Закрываем окно после успешного создания заказа

    def refresh_trees(self):
        """
        Обновляет таблицы заказов, товаров и аналитику в главном окне.
        """
        self.parent.load_orders()
        self.parent.load_products()
        self.parent.load_analysis()

class EditOrderDialog(tk.Toplevel):
    """
    Диалоговое окно для редактирования заказа.

    Parameters
    ----------
    parent : tk.Tk
        Родительское окно.
    order_id : int
        Уникальный идентификатор заказа.
    controller : AppController
        Контроллер приложения для взаимодействия с основными операциями.
    """
    def __init__(self, parent, order_id, controller):
        super().__init__(parent)
        self.parent = parent
        self.order_id = order_id
        self.controller = controller
        self.title("Редактировать заказ")
        self.resizable(False, False)
        self.build_form()
        self.original_order_items = {}  # Запоминаем первоначальный состав заказа
        self.load_order_data()

    def build_form(self):
        """
        Формирует пользовательский интерфейс окна редактирования заказа.
        """
        form_frame = ttk.Frame(self)
        form_frame.pack(padx=10, pady=10)

        # Верхний блок с информацией о заказе (сеточная раскладка)
        info_frame = ttk.Frame(form_frame)
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)

        # ID заказа
        self.label_id = ttk.Label(info_frame, text=f"ID заказа:", font=('Arial', 10))
        self.label_id_value = ttk.Label(info_frame, text=str(self.order_id), font=('Arial', 10))
        self.label_id.grid(row=0, column=0, sticky="w")
        self.label_id_value.grid(row=0, column=1, sticky="w")

        # Покупатель
        self.label_customer = ttk.Label(info_frame, text="Покупатель:", font=('Arial', 10))
        self.label_customer_value = ttk.Label(info_frame, text="", font=('Arial', 10))
        self.label_customer.grid(row=1, column=0, sticky="w")
        self.label_customer_value.grid(row=1, column=1, sticky="w")

        # Дата создания заказа
        self.label_date = ttk.Label(info_frame, text="Дата создания:", font=('Arial', 10))
        self.label_date_value = ttk.Label(info_frame, text="", font=('Arial', 10))
        self.label_date.grid(row=2, column=0, sticky="w")
        self.label_date_value.grid(row=2, column=1, sticky="w")

        # Статус заказа
        self.label_status = ttk.Label(info_frame, text="Статус:", font=('Arial', 10))
        self.combo_status = ttk.Combobox(info_frame, state="readonly",
                                         values=["Новый", "Оплачен", "Отправлен", "Исполнен"])
        self.label_status.grid(row=3, column=0, sticky="w")
        self.combo_status.grid(row=3, column=1, sticky="w")

        # Итоговая стоимость
        self.label_total = ttk.Label(info_frame, text="Итоговая сумма:", font=('Arial', 10))
        self.label_total_value = ttk.Label(info_frame, text="", font=('Arial', 10))
        self.label_total.grid(row=4, column=0, sticky="w")
        self.label_total_value.grid(row=4, column=1, sticky="w")

        # Деревья товаров и кнопки
        composition_frame = ttk.Frame(form_frame)
        composition_frame.grid(row=1, column=0, columnspan=2, sticky="we", pady=10)

        # Дерево товаров в заказе
        self.label_composition = ttk.Label(composition_frame, text="Состав заказа:", font=('Arial', 10))
        self.label_composition.pack(side="top", anchor="w")

        self.order_items_treeview = ttk.Treeview(composition_frame, columns=("Название", "Количество"), height=5,
                                                 show="headings")
        self.order_items_treeview.column("#1", anchor="w", width=200)
        self.order_items_treeview.column("#2", anchor="e", width=100)
        self.order_items_treeview.heading("Название", text="Название")
        self.order_items_treeview.heading("Количество", text="Количество")
        y_scrollbar = ttk.Scrollbar(composition_frame, orient="vertical", command=self.order_items_treeview.yview)
        y_scrollbar.pack(side="right", fill="y")
        self.order_items_treeview.configure(yscrollcommand=y_scrollbar.set)
        self.order_items_treeview.pack(side="top", fill="both", expand=True)

        # Входное поле для изменения количества
        self.quantity_entry = ttk.Entry(composition_frame, width=10)
        self.quantity_entry.pack(side="left", padx=5)
        btn_change_qty = ttk.Button(composition_frame, text="Изменить количество", command=self.change_quantity)
        btn_change_qty.pack(side="left", padx=5)

        # Фрейм с товарами на складе
        stock_frame = ttk.Frame(form_frame)
        stock_frame.grid(row=2, column=0, columnspan=2, sticky="we", pady=10)

        # Дерево товаров на складе
        self.label_stock = ttk.Label(stock_frame, text="Товары на складе:", font=('Arial', 10))
        self.label_stock.pack(side="top", anchor="w")

        self.stock_treeview = ttk.Treeview(stock_frame, columns=("ID", "Наименование", "Цена", "Кол-во на складе"),
                                           height=5, show="headings")
        self.stock_treeview.column("#1", anchor="w", width=50)
        self.stock_treeview.column("#2", anchor="w", width=200)
        self.stock_treeview.column("#3", anchor="e", width=100)
        self.stock_treeview.column("#4", anchor="e", width=100)
        self.stock_treeview.heading("ID", text="ID")
        self.stock_treeview.heading("Наименование", text="Наименование")
        self.stock_treeview.heading("Цена", text="Цена")
        self.stock_treeview.heading("Кол-во на складе", text="Кол-во на складе")
        y_scrollbar_stock = ttk.Scrollbar(stock_frame, orient="vertical", command=self.stock_treeview.yview)
        y_scrollbar_stock.pack(side="right", fill="y")
        self.stock_treeview.configure(yscrollcommand=y_scrollbar_stock.set)
        self.stock_treeview.pack(side="top", fill="both", expand=True)

        # Кнопка добавления товара в заказ
        btn_add_to_order = ttk.Button(stock_frame, text="Добавить в заказ", command=self.add_to_order)
        btn_add_to_order.pack(side="top", pady=5)

        # Нижняя панель с кнопками
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky="we", pady=10)

        # Кнопки
        apply_button = ttk.Button(buttons_frame, text="Подтвердить изменения", command=self.apply_changes)
        cancel_button = ttk.Button(buttons_frame, text="Отмена", command=self.close_window)
        apply_button.pack(side="left", padx=5)
        cancel_button.pack(side="right", padx=5)

    def load_order_data(self):
        """
        Загружает данные текущего заказа и выводит их в форме.
        """
        order = self.controller.find_order_by_id(self.order_id)
        if order:
            # Основные данные заказа
            customer = self.controller.find_customer_by_id(order.customer_id)
            self.label_customer_value.config(text=customer.name)
            self.label_date_value.config(text=order.date_created.strftime("%Y-%m-%d %H:%M:%S"))
            self.label_total_value.config(text=f"{order.total_amount:.2f}")
            self.combo_status.set(order.status)

            # ОЧИСТКА ДЕРЕВА ПЕРЕД ЗАГРУЗКОЙ
            self.order_items_treeview.delete(*self.order_items_treeview.get_children())

            # Загружаем товары в заказе
            items = self.controller.find_order_list_by_id(self.order_id)
            for item in items:
                product = self.controller.find_product_by_id(item.product_id)
                self.order_items_treeview.insert("", "end", values=(product.name, item.quantity))
                self.original_order_items[item.product_id] = item.quantity  # Запоминаем изначальное количество

            # Загружаем товары на складе
            products = self.controller.load_products()
            for product in products:
                self.stock_treeview.insert("", "end", values=(product.id, product.name, product.price, product.quantity))

    def close_window(self):
        """
        Закрывает окно без сохранения изменений.
        """
        self.destroy()

    def change_quantity(self):
        """
        Изменяет количество товара в заказе.
        """
        selected = self.order_items_treeview.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар в заказе!", parent=self)
            return

        # Проверка статуса заказа
        order = self.controller.find_order_by_id(self.order_id)
        if order.status != "Новый":
            messagebox.showwarning("Внимание", "Изменение количества товара возможно только для заказов со статусом 'Новый'", parent=self)
            return

        try:
            new_quantity = int(self.quantity_entry.get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректное целое число.", parent=self)
            return

        item = self.order_items_treeview.item(selected[0])
        product_name = item["values"][0]
        product = next((p for p in self.controller.load_products() if p.name == product_name), None)
        if not product:
            messagebox.showwarning("Ошибка", "Товар не найден.", parent=self)
            return

        # Берём исходное количество товара из оригиналов
        product_id = product.id
        old_quantity = self.original_order_items.get(product_id, 0)

        # Рассчитываем разницу между старым и новым значением
        diff = new_quantity - old_quantity

        # Максимальное разрешённое количество товара
        max_available = product.quantity + old_quantity
        min_allowed = 0

        # Проверка на минимальное и максимальное количество
        if new_quantity < min_allowed or new_quantity > max_available:
            messagebox.showwarning("Ошибка",
                                   f"Для товара '{product_name}' диапазон изменения количества от {min_allowed} до {max_available}.", parent=self)
            return

        # Обновляем дерево товаров в заказе
        self.order_items_treeview.set(selected[0], column="#2", value=new_quantity)

        # Обновляем количество товара на складе (до применения изменений)
        product.quantity -= diff  # Меняем количество товара на складе
        for child in self.stock_treeview.get_children():
            values = self.stock_treeview.item(child)["values"]
            if values[1] == product.name:
                self.stock_treeview.set(child, column="#4", value=product.quantity)

        # Обновляем итоговую сумму заказа
        self.update_total_amount()

        # Сообщаем пользователю об успешном изменении
        messagebox.showinfo("Информация", f"Количество товара '{product_name}' изменено на {new_quantity}.", parent=self)

    def add_to_order(self):
        """
        Добавляет товар из склада в заказ.
        """
        selected = self.stock_treeview.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар на складе!", parent=self)
            return

        item = self.stock_treeview.item(selected[0])
        product_id = int(item["values"][0])
        product_name = item["values"][1]
        product = self.controller.find_product_by_id(product_id)
        if product.quantity < 1:
            messagebox.showwarning("Ошибка", f"На данный момент товар '{product_name}' отсутствует на складе, добавление отменено.", parent=self)
            return

        # Проверка статуса заказа
        order = self.controller.find_order_by_id(self.order_id)
        if order.status != "Новый":
            messagebox.showwarning("Внимание", "Изменение списка товаров возможно только для заказов со статусом 'Новый'", parent=self)
            return

        # Добавляем товар в заказ
        self.order_items_treeview.insert("", "end", values=(product_name, 1))

        # Уменьшаем количество товара на складе (временно, до сохранения)
        product.quantity -= 1
        self.stock_treeview.set(selected[0], column="#4", value=product.quantity)

        # Обновляем итоговую сумму заказа
        self.update_total_amount()

        # Сообщаем пользователю об успешном добавлении
        messagebox.showinfo("Информация", f"Товар '{product_name}' добавлен в заказ.", parent=self)

    def update_total_amount(self):
        """
        Обновляет итоговую сумму заказа исходя из текущих товаров и их количеств.
        """
        total_amount = 0.0

        # Проходим по всем товарам в дереве товаров заказа
        for child in self.order_items_treeview.get_children():
            values = self.order_items_treeview.item(child)["values"]
            product_name = values[0]
            quantity = int(values[1])

            # Найти продукт по его названию
            product = next((p for p in self.controller.load_products() if p.name == product_name), None)
            if product:
                # Умножаем цену продукта на количество и добавляем к общей сумме
                total_amount += product.price * quantity

        # Обновляем метку итоговой суммы
        self.label_total_value.config(text=f"{total_amount:.2f}")
        return total_amount

    def apply_changes(self):
        """
        Применяет изменения в заказе, сохраняя их в базе данных.
        """
        # Проверка статуса заказа
        order = self.controller.find_order_by_id(self.order_id)
        current_status = order.status

        # Проверка на изменения в составе заказа
        changed = any([
            int(self.order_items_treeview.item(child)["values"][1]) != self.original_order_items.get(
                self.controller.find_product_id_by_name(self.order_items_treeview.item(child)["values"][0]), 0)
            for child in self.order_items_treeview.get_children()
        ])

        if changed and current_status != "Новый":
            # Произошли изменения в составе заказа, но статус отличен от "Новый"
            messagebox.showwarning("Внимание",
                                   "Изменения в составе заказа невозможны, так как статус заказа изменён. Верните статус на 'Новый' или отмените изменения.",
                                   parent=self)
            return

        # Обновляем состав заказа
        removed_items = []
        updated_items = []
        for child in self.order_items_treeview.get_children():
            values = self.order_items_treeview.item(child)["values"]
            product_name = values[0]
            quantity = int(values[1])
            product = next((p for p in self.controller.load_products() if p.name == product_name), None)
            if product:
                if quantity > 0:
                    updated_items.append({"product_id": product.id, "quantity": quantity})
                else:
                    removed_items.append(product_name)

        if removed_items:
            messagebox.showinfo("Информация",f"В заказе товары с нулевым количеством были удалены: {', '.join(removed_items)}.", parent=self)

        if not updated_items:
            messagebox.showwarning("Внимание", "В заказе количество всех товаров изменилось на 0, заказ отменяется.", parent=self)

        # Обновляем список товаров в заказе
        self.controller.delete_order_list(self.order_id)
        for item in updated_items:
            self.controller.add_order_item(self.order_id, item)

        # Обновляем статус заказа
        new_status = self.combo_status.get()
        if new_status:
            self.controller.update_order(self.order_id, {"status": new_status})

        # Обновляем основную информацию заказа
        total_amount = self.update_total_amount()
        self.controller.update_order(self.order_id, {"total_amount": total_amount})

        # Очищаем поле поиска вкладки заказов
        self.parent.clear_search_field(section="orders")
        self.load_order_data()
        messagebox.showinfo("Информация", "Изменения успешно применены.", parent=self)
        self.refresh_trees()
        self.destroy()  # Закрываем окно после успешного применения изменений

    def refresh_trees(self):
        """
        Обновляет данные таблиц в главном окне.
        """
        self.parent.load_orders()
        self.parent.load_products()
        self.parent.load_analysis()