import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from controllers import AppController

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Интернет-магазин | Менеджмент клиентов и заказов")
        self.geometry("800x600")
        self.controller = AppController(self)
        self.create_menus()
        self.create_tabs()

    def create_menus(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Выход", command=self.quit)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="О программе", command=self.show_about_dialog)
        menu_bar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menu_bar)

    def show_about_dialog(self):
        messagebox.showinfo("О программе", "Программа для управления магазином\nВерсия 1.0\nАвтор: Фёдоров Алексей")

    def create_tabs(self):
        tab_control = ttk.Notebook(self)
        self.tab_customers = ttk.Frame(tab_control)
        self.tab_products = ttk.Frame(tab_control)
        self.tab_orders = ttk.Frame(tab_control)

        tab_control.add(self.tab_customers, text="Клиенты")
        tab_control.add(self.tab_products, text="Товары")
        tab_control.add(self.tab_orders, text="Заказы")
        tab_control.pack(expand=True, fill="both")
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Treeview.Heading', background='lightyellow')

        self.setup_customers_tab()
        self.setup_products_tab()
        self.setup_orders_tab()

    def setup_customers_tab(self):
        frame = ttk.LabelFrame(self.tab_customers, text="Управление клиентами")
        frame.pack(padx=10, pady=10)

        # Поиск клиента
        search_frame = ttk.Frame(frame)
        search_label = ttk.Label(search_frame, text="Поиск клиентов:")
        search_label.pack(side="left")
        clear_button = ttk.Button(search_frame, text="Очистить", command=lambda: clear_search_field())
        clear_button.pack(side="right", pady=5)
        search_button = ttk.Button(search_frame, text="Искать", command=self.search_customers)
        search_button.pack(side="right")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="right")
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

        # Функция для очистки поля поиска клиента
        def clear_search_field():
            search_entry.delete(0, tk.END)  # Очищаем поле ввода
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
        keyword = self.search_var.get().strip()
        print(f"keywrod={keyword}")
        filtered_customers = self.controller.search_customers(keyword)
        print(filtered_customers)
        self.customers_treeview.delete(*self.customers_treeview.get_children())
        for cust in filtered_customers:
            self.customers_treeview.insert("", "end", values=(cust.id, cust.name, cust.email, cust.phone))

    def open_add_customer_dialog(self):
        AddCustomerDialog(self)

    def edit_selected_customer(self):
        selected = self.customers_treeview.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите клиента перед редактированием!")
            return
        item = self.customers_treeview.item(selected[0])["values"]
        EditCustomerDialog(self, customer_id=int(item[0]))

    def delete_selected_customer(self):
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
            self.controller.delete_customer(int(item[0]))
            self.load_customers()

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
            else:
                messagebox.showerror("Ошибка импорта", f"Возникла ошибка при импорте: {error_msg}")

    def setup_products_tab(self):
        frame = ttk.LabelFrame(self.tab_products, text="Управление товарами")
        frame.pack(padx=10, pady=10)

        # Поиск товара
        search_frame = ttk.Frame(frame)
        search_label = ttk.Label(search_frame, text="Поиск товаров:")
        search_label.pack(side="left")
        clear_button = ttk.Button(search_frame, text="Очистить", command=lambda: clear_search_field())
        clear_button.pack(side="right", pady=5)
        search_button = ttk.Button(search_frame, text="Искать", command=self.search_products)
        search_button.pack(side="right")
        self.search_prod_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_prod_var)
        search_entry.pack(side="right")
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

        # Функция для очистки поля поиска товара
        def clear_search_field():
            search_entry.delete(0, tk.END)  # Очищаем поле ввода
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
        keyword = self.search_prod_var.get().strip()
        print(f"keyword={keyword}")
        filtered_products = self.controller.search_products(keyword)
        print(filtered_products)
        self.products_treeview.delete(*self.products_treeview.get_children())
        for prod in filtered_products:
            self.products_treeview.insert("", "end", values=(prod.id, prod.name, prod.price, prod.quantity))

    def open_add_product_dialog(self):
        AddProductDialog(self)

    def edit_selected_product(self):
        selected = self.products_treeview.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите товар перед редактированием!")
            return
        item = self.products_treeview.item(selected[0])["values"]
        EditProductDialog(self, product_id=int(item[0]))

    def delete_selected_product(self):
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
            self.controller.delete_product(int(item[0]))
            self.load_products()

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
            else:
                messagebox.showerror("Ошибка импорта", f"Возникла ошибка при импорте: {error_msg}")

    def setup_orders_tab(self):
        frame = ttk.LabelFrame(self.tab_orders, text="Управление заказами")
        frame.pack(padx=10, pady=10)

        # Поиск заказа
        search_frame = ttk.Frame(frame)
        search_label = ttk.Label(search_frame, text="Поиск заказов:")
        search_label.pack(side="left")
        clear_button = ttk.Button(search_frame, text="Очистить", command=lambda: clear_search_field())
        clear_button.pack(side="right", pady=5)
        search_button = ttk.Button(search_frame, text="Искать", command=self.search_orders)
        search_button.pack(side="right")
        self.search_ord_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_ord_var)
        search_entry.pack(side="right")
        search_frame.pack(fill="x", padx=5, pady=5)

        # Дерево результатов поиска
        tree_columns = ("ID", "Покупатель", "Дата создания", "Статус заказа", "Итоговая сумма")
        self.orders_treeview = ttk.Treeview(frame, columns=tree_columns, show="headings")
        for col in tree_columns:
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

        # Функция для очистки поля поиска заказа
        def clear_search_field():
            search_entry.delete(0, tk.END)  # Очищаем поле ввода
            self.load_orders()

    def load_orders(self):
        """
        Обновляет дерево заказов на основании данных, полученных от контроллера.
        """
        orders = self.controller.load_orders()
        self.orders_treeview.delete(*self.orders_treeview.get_children())
        for ord in orders:
            # Получаем имя покупателя по идентификатору
            customer = self.controller.find_customer_by_id(ord.customer_id)
            customer_name = customer.name if customer else "Покупатель не найден"

            # Вставляем данные в дерево заказов
            self.orders_treeview.insert("", "end",
                                        values=(ord.id, customer_name, ord.date_created, ord.status, ord.total_amount))

    def search_orders(self):
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
        AddOrderDialog(self, controller=self.controller)

    def edit_selected_order(self):
        selected = self.orders_treeview.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ перед редактированием!")
            return
        item = self.orders_treeview.item(selected[0])["values"]
        EditOrderDialog(self, order_id=int(item[0]), controller=self.controller)

    def delete_selected_order(self):
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
            else:
                messagebox.showerror("Ошибка импорта", f"Возникла ошибка при импорте: {error_msg}")

class AddCustomerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Добавить клиента")
        self.resizable(False, False)

        # Вспомогательные переменные для отслеживания меток с ошибками
        self.error_labels = []

        # Основной фрейм
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10)

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
                #Обновляем дерево клиентов
                self.parent.load_customers()
                # Закрываем окно только при успехе
                self.destroy()
            else:
                # Иначе показываем ошибки
                # self.display_errors(error_msg)
                messagebox.showerror("Ошибка", error_msg, parent=self)
        except Exception as err:
            messagebox.showerror("Ошибка", str(err), parent=self)

class EditCustomerDialog(tk.Toplevel):
    def __init__(self, parent, customer_id):
        super().__init__(parent)
        self.parent = parent
        self.customer_id = customer_id
        self.title("Редактировать клиента")
        self.resizable(False, False)
        self.build_form()
        self.load_customer_data()

    def build_form(self):
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
        customer = self.parent.controller.find_customer_by_id(self.customer_id)
        if customer:
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, customer.name)
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, customer.email)
            self.entry_phone.delete(0, tk.END)
            self.entry_phone.insert(0, customer.phone)

    def save_customer(self):
        name = self.entry_name.get().strip()
        email = self.entry_email.get().strip()
        phone = self.entry_phone.get().strip()

        # Отправляем данные контроллеру
        try:
            success, error_msg = self.parent.controller.edit_customer(self.customer_id, {"name": name, "email": email, "phone": phone})
            if success:
                self.parent.load_customers()
                self.destroy()
            else:
                messagebox.showerror("Ошибка", error_msg, parent=self)
        except Exception as err:
            messagebox.showerror("Ошибка", str(err), parent=self)

class AddProductDialog(tk.Toplevel):
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
                # Обновление дерева товаров
                self.parent.load_products()
                # Закрываем окно только при успехе
                self.destroy()
            else:
                # Иначе показываем ошибки
                # self.display_errors(error_msg)
                messagebox.showerror("Ошибка", error_msg, parent=self)
        except Exception as err:
            messagebox.showerror("Ошибка", str(err), parent=self)

class EditProductDialog(tk.Toplevel):
    def __init__(self, parent, product_id):
        super().__init__(parent)
        self.parent = parent
        self.product_id = product_id
        self.title("Редактировать товар")
        self.resizable(False, False)
        self.build_form()
        self.load_product_data()

    def build_form(self):
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
        product = self.parent.controller.find_product_by_id(self.product_id)
        if product:
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, product.name)
            self.entry_price.delete(0, tk.END)
            self.entry_price.insert(0, product.price)
            self.entry_quantity.delete(0, tk.END)
            self.entry_quantity.insert(0, product.quantity)

    def save_product(self):
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        quantity = self.entry_quantity.get().strip()

        # Отправляем данные контроллеру
        try:
            success, error_msg = self.parent.controller.edit_product(self.product_id, {"name": name, "price": price, "quantity": quantity})
            if success:
                self.parent.load_products()
                self.destroy()
            else:
                messagebox.showerror("Ошибка", error_msg, parent=self)
        except Exception as err:
            messagebox.showerror("Ошибка", str(err), parent=self)

class AddOrderDialog(tk.Toplevel):
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
        # Основные данные заказа
        # Загрузка списка покупателей
        customers = self.controller.load_customers()
        self.customer_map = {customer.name: customer.id for customer in customers}
        self.combo_customer['values'] = list(self.customer_map.keys())

        self.label_total_value.config(text="0.00 руб")

        # ОЧИСТКА ДЕРЕВА СКЛАДА ПЕРЕД ЗАГРУЗКОЙ
        self.stock_treeview.delete(*self.order_items_treeview.get_children())

        # # Загружаем товары в заказе
        # items = self.controller.find_order_list_by_id(self.order_id)
        # for item in items:
        #     product = self.controller.find_product_by_id(item.product_id)
        #     self.order_items_treeview.insert("", "end", values=(product.name, item.quantity))
        #     self.original_order_items[item.product_id] = item.quantity  # Запоминаем изначальное количество

        # Загружаем товары на складе
        products = self.controller.load_products()
        for product in products:
            self.stock_treeview.insert("", "end", values=(product.id, product.name, product.price, product.quantity))

    def close_window(self):
        """Закрытие окна без сохранения изменений"""
        self.destroy()

    def change_quantity(self):
        """Изменяет количество товара в заказе"""
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

        # # Берём исходное количество товара из оригиналов
        # product_id = product.id
        # old_quantity = self.original_order_items.get(product_id, 0)

        # Рассчитываем разницу между старым и новым значением
        # diff = new_quantity - old_quantity

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
        """Добавляет товар из склада в заказ"""
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
        """Обновляет итоговую сумму заказа"""
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
        """Оформляет заказ"""

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
            self.parent.load_orders()
        else:
            messagebox.showwarning("Внимание", message, parent=self)
        self.destroy()

        # Обновляем интерфейс
        self.refresh_trees()
        self.destroy()  # Закрываем окно после успешного создания заказа

    def refresh_trees(self):
        """Обновляет деревья в основном окне"""
        self.parent.load_orders()
        self.parent.load_products()

# class AddOrderDialog(tk.Toplevel):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.parent = parent
#         self.title("Добавить заказ")
#         self.resizable(False, False)
#         self.cart_items = []
#         self.total_amount = 0.0
#
#         # Основной фрейм
#         main_frame = ttk.Frame(self)
#         main_frame.pack(padx=10, pady=10)
#
#         # Выбор покупателя
#         self.label_customer = ttk.Label(main_frame, text="Покупатель:")
#         self.label_customer.grid(row=0, column=0, sticky="W")
#         self.combo_customer = ttk.Combobox(main_frame)
#         self.combo_customer.grid(row=0, column=1, sticky="WE")
#         self.load_customers()
#
#         # Список товаров
#         self.label_products = ttk.Label(main_frame, text="Товары:")
#         self.label_products.grid(row=1, column=0, sticky="W")
#         self.products_treeview = ttk.Treeview(main_frame, columns=("ID", "Название", "Цена", "Количество"), show="headings")
#         self.products_treeview.column("#1", anchor="center", width=50)
#         self.products_treeview.column("#2", anchor="w", width=200)
#         self.products_treeview.column("#3", anchor="e", width=100)
#         self.products_treeview.column("#4", anchor="e", width=100)
#         self.products_treeview.heading("ID", text="ID")
#         self.products_treeview.heading("Название", text="Название")
#         self.products_treeview.heading("Цена", text="Цена")
#         self.products_treeview.heading("Количество", text="Количество")
#         self.products_treeview.grid(row=1, column=1, sticky="NSEW")
#         self.load_products()
#
#         # Количество товаров в корзине
#         self.label_count = ttk.Label(main_frame, text="Количество товаров в заказе: 0")
#         self.label_count.grid(row=2, column=0, sticky="W")
#
#         # Общая сумма заказа
#         self.label_total = ttk.Label(main_frame, text="Общая сумма заказа: 0.00 руб.")
#         self.label_total.grid(row=2, column=1, sticky="E")
#
#         # Кнопка добавления товара в корзину
#         add_to_cart_btn = ttk.Button(main_frame, text="Добавить в корзину", command=self.add_to_cart)
#         add_to_cart_btn.grid(row=3, column=0, pady=10)
#
#         # Кнопка оформления заказа
#         proceed_to_checkout_btn = ttk.Button(main_frame, text="Оформить заказ", command=self.proceed_to_checkout)
#         proceed_to_checkout_btn.grid(row=4, column=0, pady=10)
#
#         # Кнопка отмены
#         cancel_btn = ttk.Button(main_frame, text="Отмена", command=self.destroy)
#         cancel_btn.grid(row=4, column=1, pady=10)
#
#     def load_customers(self):
#         """Загружает список покупателей через контроллер."""
#         customers = self.parent.controller.load_customers()
#         self.customer_map = {customer.name: customer.id for customer in customers}
#         self.combo_customer['values'] = list(self.customer_map.keys())
#
#     def load_products(self):
#         """Загружает список товаров через контроллер."""
#         products = self.parent.controller.load_products()
#         for product in products:
#             self.products_treeview.insert("", "end", values=(product.id, product.name, product.price, product.quantity))
#
#     def add_to_cart(self):
#         """Добавляет товар в корзину."""
#         selection = self.products_treeview.selection()
#         if not selection:
#             messagebox.showwarning("Внимание", "Выберите товар!", parent=self)
#             return
#
#         item = self.products_treeview.item(selection[0])
#         values = item['values']
#         product_id = values[0]
#         product_name = values[1]
#         product_price = float(values[2])
#         product_quantity = int(values[3])
#
#         # Проверяем наличие товара на складе
#         if product_quantity == 0:
#             messagebox.showwarning("Внимание", f"Невозможно добавить {product_name} в корзину. Товара нет в наличии.", parent=self)
#             return
#
#         # Проверяем, есть ли уже такой товар в корзине
#         existing_item = next((i for i in self.cart_items if i["product_id"] == product_id), None)
#         if existing_item:
#             # Если товар уже есть, увеличиваем его количество
#             existing_item["quantity"] += 1
#         else:
#             # Если товар новый, добавляем его в корзину
#             self.cart_items.append({
#                 "product_id": product_id,
#                 "name": product_name,
#                 "price": product_price,
#                 "quantity": 1
#             })
#         self.calculate_total()
#         messagebox.showinfo("Информация", f"Товар {product_name} добавлен в заказ.", parent=self)
#         # Возвращаем фокус на окно AddOrderDialog
#         self.lift()  # Установим фокус на окно
#         self.focus_force()  # Заставляем окно стать активным
#         self.grab_set()  # Блокируем доступ к главному окну до закрытия этого окна
#
#     def calculate_total(self):
#         """Рассчитывает общую сумму заказа и количество товаров."""
#         self.total_amount = sum(item["price"] * item["quantity"] for item in self.cart_items)
#         num_items = len(self.cart_items)
#         self.label_count.config(text=f"Количество товаров в заказе: {num_items}")
#         self.label_total.config(text=f"Общая сумма заказа: {self.total_amount:.2f} руб.")
#
#     def proceed_to_checkout(self):
#         """Переход в корзину для оформления заказа."""
#         if not self.cart_items:
#             messagebox.showwarning("Внимание", "Нет товаров в корзине!", parent=self)
#             return
#
#         if not self.combo_customer.current():
#             messagebox.showwarning("Внимание", "Выберите покупателя!", parent=self)
#             return
#
#         CheckoutCartWindow(self, self.cart_items, self.customer_map[self.combo_customer.get()])
#
#
# class CheckoutCartWindow(tk.Toplevel):
#     def __init__(self, parent, cart_items, customer_id):
#         super().__init__(parent)
#         self.parent = parent
#         self.cart_items = cart_items
#         self.customer_id = customer_id
#         self.title("Корзина")
#         self.resizable(False, False)
#
#         # Основной фрейм
#         main_frame = ttk.Frame(self)
#         main_frame.pack(padx=10, pady=10)
#
#         # Информация о покупателе
#         self.label_customer = ttk.Label(main_frame, text=f"Покупатель: {next((c.name for c in parent.parent.controller.load_customers() if c.id == customer_id), 'Не найден')}")
#         self.label_customer.grid(row=0, column=0, sticky="W")
#
#         # Суммарная стоимость заказа
#         self.label_total = ttk.Label(main_frame, text="Общая сумма заказа: ")
#         self.label_total.grid(row=0, column=1, sticky="E")
#         self.update_total()  # Сразу обновляем итоговую сумму
#
#         # Создаем отдельные фреймы для каждого товара и спиннеров
#         self.cart_frames = []
#         for idx, item in enumerate(cart_items):
#             # Получаем максимальную величину количества товара из базы данных
#             max_quantity = self.parent.parent.controller.find_product_by_id(item["product_id"]).quantity
#             item["max_quantity"] = max_quantity  # Добавляем max_quantity в cart_items
#
#             # Отдельный фрейм для каждого товара
#             frame = ttk.Frame(main_frame)
#             frame.grid(row=idx + 1, column=0, columnspan=2, sticky="EW")
#             self.cart_frames.append(frame)
#
#             # Название и цена товара
#             label_product = ttk.Label(frame, text=f"{item['name']} ({item['price']} руб.)")
#             label_product.pack(side="left", padx=5)
#
#             # Спиннер для изменения количества
#             spinbox = tk.Spinbox(frame, from_=0, to=max_quantity, increment=1, justify="right", width=5)
#             spinbox.delete(0, "end")
#             spinbox.insert(0, item["quantity"])
#             spinbox.bind("<KeyRelease>", lambda event, index=idx: self.on_spinbox_change(event, index))
#             spinbox.pack(side="right", padx=5)
#
#         # Кнопка оформления заказа
#         checkout_btn = ttk.Button(main_frame, text="Оформить заказ", command=self.checkout)
#         checkout_btn.grid(row=len(cart_items)+1, column=0, pady=10)
#
#         # Кнопка отмены
#         cancel_btn = ttk.Button(main_frame, text="Отмена", command=self.cancel)
#         cancel_btn.grid(row=len(cart_items)+1, column=1, pady=10)
#
#     def on_spinbox_change(self, event, index):
#         """Обрабатывает изменение количества товара в корзине."""
#         widget = event.widget
#         new_value = widget.get()
#         try:
#             quantity = int(new_value)
#             if quantity >= 0 and quantity <= self.cart_items[index]["max_quantity"]:
#                 self.cart_items[index]["quantity"] = quantity
#                 self.update_total()
#             else:
#                 messagebox.showwarning("Внимание", "Введённое количество выходит за допустимый диапазон.", parent=self)
#                 widget.delete(0, tk.END)
#                 widget.insert(0, self.cart_items[index]["quantity"])
#         except ValueError:
#             messagebox.showwarning("Внимание", "Введите корректное число.", parent=self)
#             widget.delete(0, tk.END)
#             widget.insert(0, self.cart_items[index]["quantity"])
#
#     def update_total(self):
#         """Обновляет итоговую сумму заказа."""
#         total_amount = sum(item["price"] * item["quantity"] for item in self.cart_items)
#         self.label_total.config(text=f"Общая сумма заказа: {total_amount:.2f} руб.")
#
#     def checkout(self):
#         """Обращается к контроллеру для оформления заказа и показывает сообщение пользователю."""
#         removed_items = []
#         updated_cart_items = []
#
#         # Исключение товаров с нулевым количеством и запоминание удалённых товаров
#         for item in self.cart_items:
#             if item["quantity"] > 0:
#                 updated_cart_items.append(item)
#             else:
#                 removed_items.append(item["name"])
#
#         if removed_items:
#             messagebox.showinfo("Информация",
#                                 f"В корзине товары с нулевым количеством были удалены: {', '.join(removed_items)}.",
#                                 parent=self)
#
#         if not updated_cart_items:
#             messagebox.showwarning("Внимание", "В корзине количество всех товаров изменилось на 0, заказ отменяется.",
#                                    parent=self)
#             self.parent.destroy()
#             self.destroy()
#             return
#
#         # Подготавливаем данные для отправки в контроллер
#         final_cart_items = [{
#             "product_id": item["product_id"],
#             "quantity": item["quantity"]
#         } for item in updated_cart_items]
#
#         success, message = self.parent.parent.controller.process_checkout(final_cart_items, self.customer_id)
#         if success:
#             messagebox.showinfo("Информация", message, parent=self)
#             self.parent.destroy()
#             self.parent.parent.load_orders()
#         else:
#             messagebox.showwarning("Внимание", message, parent=self)
#         self.destroy()
#
#     def cancel(self):
#         """Отменяет оформление заказа и закрывает окно корзины."""
#         self.destroy()

class EditOrderDialog(tk.Toplevel):
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
        """Закрытие окна без сохранения изменений"""
        self.destroy()

    def change_quantity(self):
        """Изменяет количество товара в заказе"""
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
        """Добавляет товар из склада в заказ"""
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
        """Обновляет итоговую сумму заказа"""
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
        """Применяет изменения в заказе"""
        # Проверка статуса заказа
        order = self.controller.find_order_by_id(self.order_id)
        current_status = order.status

        # Вспомогательная функция для получения идентификатора товара по его названию
        def find_product_id_by_name(name):
            product = next((p for p in self.controller.load_products() if p.name == name), None)
            return product.id if product else None

        # Проверка на изменения в составе заказа
        changed = any([
            int(self.order_items_treeview.item(child)["values"][1]) != self.original_order_items.get(
                find_product_id_by_name(self.order_items_treeview.item(child)["values"][0]), 0)
            for child in self.order_items_treeview.get_children()
        ])

        if changed and current_status != "Новый":
            # Произошли изменения в составе заказа, но статус отличен от "Новый"
            messagebox.showwarning("Внимание",
                                   "Изменения в составе заказа невозможны, так как статус заказа изменён. Верните статус на 'Новый' или отмените изменения.",
                                   parent=self)
            return

        # Обновляем состав заказа
        updated_items = []
        for child in self.order_items_treeview.get_children():
            values = self.order_items_treeview.item(child)["values"]
            product_name = values[0]
            quantity = int(values[1])
            product = next((p for p in self.controller.load_products() if p.name == product_name), None)
            if product:
                updated_items.append({"product_id": product.id, "quantity": quantity})

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

        # Обновляем интерфейс
        self.load_order_data()
        messagebox.showinfo("Информация", "Изменения успешно применены.", parent=self)
        self.refresh_trees()
        self.destroy()  # Закрываем окно после успешного применения изменений

    def refresh_trees(self):
        """Обновляет деревья в основном окне"""
        self.parent.load_orders()
        self.parent.load_products()

# class EditOrderDialog(tk.Toplevel):
#     def __init__(self, parent, order_id, controller):
#         super().__init__(parent)
#         self.parent = parent
#         self.order_id = order_id
#         self.controller = controller
#         self.title("Редактировать заказ")
#         self.resizable(False, False)
#         self.build_form()
#         self.original_order_items = {}  # Запоминаем первоначальный состав заказа
#         self.load_order_data()
#
#     def build_form(self):
#         form_frame = ttk.Frame(self)
#         form_frame.pack(padx=10, pady=10)
#
#         # Верхний фрейм с информацией о заказе
#         info_frame = ttk.Frame(form_frame)
#         info_frame.pack(pady=10)
#
#         # ID заказа
#         self.label_id = ttk.Label(info_frame, text=f"ID заказа: {self.order_id}")
#         self.label_id.pack(side="top", anchor="w")
#
#         # Покупатель
#         self.label_customer = ttk.Label(info_frame, text="Покупатель:")
#         self.label_customer_value = ttk.Label(info_frame, text="")
#         self.label_customer.pack(side="top", anchor="w")
#         self.label_customer_value.pack(side="top", anchor="w")
#
#         # Состав заказа
#         composition_frame = ttk.Frame(form_frame)
#         composition_frame.pack(pady=10)
#
#         self.label_composition = ttk.Label(composition_frame, text="Состав заказа:")
#         self.label_composition.pack(side="top", anchor="w")
#
#         # Дерево товаров в заказе
#         self.order_items_treeview = ttk.Treeview(composition_frame, columns=("Название", "Количество"), height=5, show="headings")
#         self.order_items_treeview.column("#1", anchor="w", width=200)
#         self.order_items_treeview.column("#2", anchor="e", width=100)
#         self.order_items_treeview.heading("Название", text="Название")
#         self.order_items_treeview.heading("Количество", text="Количество")
#         y_scrollbar = ttk.Scrollbar(composition_frame, orient="vertical", command=self.order_items_treeview.yview)
#         y_scrollbar.pack(side="right", fill="y")
#         self.order_items_treeview.configure(yscrollcommand=y_scrollbar.set)
#         self.order_items_treeview.pack(side="top", fill="both", expand=True)
#
#         # Входное поле для изменения количества
#         self.quantity_entry = ttk.Entry(composition_frame, width=10)
#         self.quantity_entry.pack(side="left", padx=5)
#         btn_change_qty = ttk.Button(composition_frame, text="Изменить количество", command=self.change_quantity)
#         btn_change_qty.pack(side="left", padx=5)
#
#         # Продукты на складе
#         stock_frame = ttk.Frame(form_frame)
#         stock_frame.pack(pady=10)
#
#         self.label_stock = ttk.Label(stock_frame, text="Продукты на складе:")
#         self.label_stock.pack(side="top", anchor="w")
#
#         # Дерево товаров на складе
#         self.stock_treeview = ttk.Treeview(stock_frame, columns=("ID", "Наименование", "Цена", "Кол-во на складе"), height=5, show="headings")
#         self.stock_treeview.column("#1", anchor="w", width=50)
#         self.stock_treeview.column("#2", anchor="w", width=200)
#         self.stock_treeview.column("#3", anchor="e", width=100)
#         self.stock_treeview.column("#4", anchor="e", width=100)
#         self.stock_treeview.heading("ID", text="ID")
#         self.stock_treeview.heading("Наименование", text="Наименование")
#         self.stock_treeview.heading("Цена", text="Цена")
#         self.stock_treeview.heading("Кол-во на складе", text="Кол-во на складе")
#         y_scrollbar_stock = ttk.Scrollbar(stock_frame, orient="vertical", command=self.stock_treeview.yview)
#         y_scrollbar_stock.pack(side="right", fill="y")
#         self.stock_treeview.configure(yscrollcommand=y_scrollbar_stock.set)
#         self.stock_treeview.pack(side="top", fill="both", expand=True)
#
#         # Кнопка добавления товара в заказ
#         btn_add_to_order = ttk.Button(stock_frame, text="Добавить в заказ", command=self.add_to_order)
#         btn_add_to_order.pack(side="top", pady=5)
#
#         # Дата создания заказа
#         self.label_date = ttk.Label(form_frame, text="Дата создания:")
#         self.label_date_value = ttk.Label(form_frame, text="")
#         self.label_date.pack(side="top", anchor="w")
#         self.label_date_value.pack(side="top", anchor="w")
#
#         # Статус заказа
#         self.label_status = ttk.Label(form_frame, text="Статус:")
#         self.combo_status = ttk.Combobox(form_frame, state="readonly", values=["Новый", "Оплачен", "Отправлен", "Исполнен"])
#         self.label_status.pack(side="top", anchor="w")
#         self.combo_status.pack(side="top", anchor="w")
#
#         # Итоговая стоимость
#         self.label_total = ttk.Label(form_frame, text="Итоговая стоимость:")
#         self.label_total_value = ttk.Label(form_frame, text="")
#         self.label_total.pack(side="top", anchor="w")
#         self.label_total_value.pack(side="top", anchor="w")
#
#         # Кнопки
#         apply_button = ttk.Button(form_frame, text="Применить изменения", command=self.apply_changes)
#         cancel_button = ttk.Button(form_frame, text="Отмена", command=self.close_window)
#         apply_button.pack(side="left", padx=5)
#         cancel_button.pack(side="right", padx=5)
#
#     def load_order_data(self):
#         order = self.controller.find_order_by_id(self.order_id)
#         if order:
#             # Основные данные заказа
#             customer = self.controller.find_customer_by_id(order.customer_id)
#             self.label_customer_value.config(text=customer.name)
#             self.label_date_value.config(text=order.date_created.strftime("%Y-%m-%d %H:%M:%S"))
#             self.label_total_value.config(text=f"{order.total_amount:.2f}")
#             self.combo_status.set(order.status)
#
#             # Загружаем товары в заказе
#             items = self.controller.find_order_list_by_id(self.order_id)
#             for item in items:
#                 product = self.controller.find_product_by_id(item.product_id)
#                 self.order_items_treeview.insert("", "end", values=(product.name, item.quantity))
#                 self.original_order_items[item.product_id] = item.quantity  # Запоминаем изначальное количество
#
#             # Загружаем товары на складе
#             products = self.controller.load_products()
#             for product in products:
#                 self.stock_treeview.insert("", "end", values=(product.id, product.name, product.price, product.quantity))
#
#     def close_window(self):
#         """Закрытие окна без сохранения изменений"""
#         self.destroy()
#
#     def change_quantity(self):
#         """Изменяет количество товара в заказе"""
#         selected = self.order_items_treeview.selection()
#         if not selected:
#             messagebox.showwarning("Внимание", "Выберите товар в заказе!", parent=self)
#             return
#
#         # Проверка статуса заказа
#         order = self.controller.find_order_by_id(self.order_id)
#         if order.status != "Новый":
#             messagebox.showwarning("Внимание",
#                                    "Изменение количества товара возможно только для заказов со статусом 'Новый'", parent=self)
#             return
#
#         try:
#             new_quantity = int(self.quantity_entry.get())
#         except ValueError:
#             messagebox.showwarning("Ошибка", "Введите корректное целое число.", parent=self)
#             return
#
#         item = self.order_items_treeview.item(selected[0])
#         product_name = item["values"][0]
#         product = next((p for p in self.controller.load_products() if p.name == product_name), None)
#         if not product:
#             messagebox.showwarning("Ошибка", "Товар не найден.", parent=self)
#             return
#
#         # Правильно берём исходное количество товара из оригинального словаря
#         product_id = product.id
#         old_quantity = self.original_order_items.get(product_id, 0)
#
#         # Рассчитываем разницу между старым и новым значением
#         diff = new_quantity - old_quantity
#
#         # Максимальное разрешённое количество товара
#         max_available = product.quantity + old_quantity
#         min_allowed = 0
#
#         # Проверка на минимальное и максимальное количество
#         if new_quantity < min_allowed or new_quantity > max_available:
#             messagebox.showwarning("Ошибка",
#                                    f"Для товара '{product_name}' диапазон изменения количества от {min_allowed} до {max_available}.", parent=self)
#             return
#
#         # Обновляем дерево товаров в заказе
#         self.order_items_treeview.set(selected[0], column="#2", value=new_quantity)
#
#         # Обновляем количество товара на складе (до применения изменений)
#         product.quantity -= diff  # Меняем количество товара на складе
#         for child in self.stock_treeview.get_children():
#             values = self.stock_treeview.item(child)["values"]
#             if values[1] == product.name:
#                 self.stock_treeview.set(child, column="#4", value=product.quantity)
#
#         # Обновляем итоговую сумму заказа
#         self.update_total_amount()
#
#         # Сообщаем пользователю об успешном изменении
#         messagebox.showinfo("Информация", f"Количество товара '{product_name}' изменено на {new_quantity}.", parent=self)
#
#     def add_to_order(self):
#         """Добавляет товар из склада в заказ"""
#         selected = self.stock_treeview.selection()
#         if not selected:
#             messagebox.showwarning("Внимание", "Выберите товар на складе!", parent=self)
#             return
#
#         item = self.stock_treeview.item(selected[0])
#         product_id = int(item["values"][0])
#         product_name = item["values"][1]
#         product = self.controller.find_product_by_id(product_id)
#         if product.quantity < 1:
#             messagebox.showwarning("Ошибка", f"На данный момент товар '{product_name}' отсутствует на складе, добавление отменено.", parent=self)
#             return
#
#         # Проверка статуса заказа
#         order = self.controller.find_order_by_id(self.order_id)
#         if order.status != "Новый":
#             messagebox.showwarning("Внимание", "Изменение списка товаров возможно только для заказов со статусом 'Новый'", parent=self)
#             return
#
#         # Добавляем товар в заказ
#         self.order_items_treeview.insert("", "end", values=(product_name, 1))
#
#         # Уменьшаем количество товара на складе (временно, до сохранения)
#         product.quantity -= 1
#         self.stock_treeview.set(selected[0], column="#4", value=product.quantity)
#
#         # Обновляем итоговую сумму заказа
#         self.update_total_amount()
#
#         # Сообщаем пользователю об успешном добавлении
#         messagebox.showinfo("Информация", f"Товар '{product_name}' добавлен в заказ.", parent=self)
#
#     def update_total_amount(self):
#         """Обновляет итоговую сумму заказа"""
#         total_amount = 0.0
#
#         # Проходим по всем товарам в дереве товаров заказа
#         for child in self.order_items_treeview.get_children():
#             values = self.order_items_treeview.item(child)["values"]
#             product_name = values[0]
#             quantity = int(values[1])
#
#             # Найти продукт по его названию
#             product = next((p for p in self.controller.load_products() if p.name == product_name), None)
#             if product:
#                 # Умножаем цену продукта на количество и добавляем к общей сумме
#                 total_amount += product.price * quantity
#
#         # Обновляем метку итоговой суммы
#         self.label_total_value.config(text=f"{total_amount:.2f}")
#
#     def apply_changes(self):
#         """Применяет изменения в заказе"""
#         # Проверка статуса заказа
#         order = self.controller.find_order_by_id(self.order_id)
#         current_status = order.status
#
#         # Вспомогательная функция для получения идентификатора товара по его названию
#         def find_product_id_by_name(name):
#             product = next((p for p in self.controller.load_products() if p.name == name), None)
#             return product.id if product else None
#
#         # Проверка на изменения в составе заказа
#         changed = any([
#             int(self.order_items_treeview.item(child)["values"][1]) != self.original_order_items.get(
#                 find_product_id_by_name(self.order_items_treeview.item(child)["values"][0]), 0)
#             for child in self.order_items_treeview.get_children()
#         ])
#
#         if changed and current_status != "Новый":
#             # Произошли изменения в составе заказа, но статус отличен от "Новый"
#             messagebox.showwarning("Внимание",
#                                    "Изменения в составе заказа невозможны, так как статус заказа изменён. Верните статус на 'Новый' или отмените изменения.", parent=self)
#             return
#
#         # Обновляем состав заказа
#         updated_items = []
#         for child in self.order_items_treeview.get_children():
#             values = self.order_items_treeview.item(child)["values"]
#             product_name = values[0]
#             quantity = int(values[1])
#             product = next((p for p in self.controller.load_products() if p.name == product_name), None)
#             if product:
#                 updated_items.append(OrderItem(product_id=product.id, quantity=quantity))
#
#         # Обновляем список товаров в заказе
#         self.controller.delete_order_list(self.order_id)
#         for item in updated_items:
#             self.controller.add_order_item(self.order_id, item)
#
#         # Обновляем статус заказа
#         new_status = self.combo_status.get()
#         if new_status:
#             self.controller.update_order(self.order_id, {"status": new_status})
#
#         # Обновляем основную информацию заказа
#         total_amount = sum(
#             item.quantity * self.controller.find_product_by_id(item.product_id).price for item in updated_items)
#         self.controller.update_order(self.order_id, {"total_amount": total_amount})
#
#         # Обновляем интерфейс
#         self.load_order_data()
#         messagebox.showinfo("Информация", "Изменения успешно применены.", parent=self)
#         self.refresh_trees()
#         self.destroy()  # Закрываем окно после успешного применения изменений
#
#     def refresh_trees(self):
#         """Обновляет деревья в основном окне"""
#         self.parent.load_orders()
#         self.parent.load_products()