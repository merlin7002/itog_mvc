import pandas as pd
import numpy as np

def top5(res):
    """
    Обрабатывает полученные из БД (через контроллер) данные, анализирует и возвращает в gui (через контроллер)
     для построения графика топ5 клиентов по числу заказов.
    """
    # Формируем датафреймы из полученных данных
    df_customers = pd.DataFrame(res[0][0], columns=res[0][1])
    df_orders = pd.DataFrame(res[1][0], columns=res[1][1])

    # Обработка данных для анализа
    df = df_orders.merge(df_customers, left_on='customer_id', right_on='id', how='left')
    top_customers = df.groupby('name')['id_x'].count().reset_index().rename(
        columns={'id_x': 'number_of_orders'})

    # Сортировка данных по числу заказов
    top_customers = top_customers.nlargest(5, 'number_of_orders')
    top_customers.sort_values(by='number_of_orders', ascending=False, inplace=True)

    return top_customers

def orders_per_day(res):
    """
    Обрабатывает полученные из БД (через контроллер) данные, анализирует и возвращает в gui (через контроллер)
    для построения линейного графика отображения динамики количества заказов по датам
    """
    # Подготовим данные
    df_orders = pd.DataFrame(res[0], columns=res[1])
    df_orders['date_created'] = df_orders['date_created'].apply(lambda x: x.split('.')[0])
    df_orders['date_created'] = pd.to_datetime(df_orders['date_created'], format='%Y-%m-%d %H:%M:%S')
    orders_p_day = df_orders.groupby(df_orders['date_created'].dt.normalize()).size().reset_index(name='counts')

    # Форматирование дат
    orders_p_day['date_created'] = orders_p_day['date_created'].dt.strftime('%d-%m-%Y')

    # Чистка неполных или недействительных записей
    orders_p_day = orders_p_day.query('counts.notnull() & counts != ""')

    return orders_p_day


def client_connections(res):
    """
    Обрабатывает полученные из БД (через контроллер) данные, анализирует и возвращает в gui (через контроллер)
    для построения графа связей покупателей (по общим товарам)
    """
    df_customers = pd.DataFrame(res[0][0], columns=res[0][1])
    df_products = pd.DataFrame(res[1][0], columns=res[1][1])
    df_orders = pd.DataFrame(res[2][0], columns=res[2][1])
    df_order_items = pd.DataFrame(res[3][0], columns=res[3][1])

    # Анализ общих товаров между клиентами

    # Проводим полное слияние
    merged_df = df_orders.merge(df_customers, left_on='customer_id', right_on='id', how='left',
                                suffixes=('_orders', '_customers'))
    merged_df2 = merged_df.merge(df_order_items, left_on='id_orders', right_on='order_id', how='inner')
    final_df = merged_df2.merge(df_products, left_on='product_id', right_on='id', how='inner', suffixes=('_customer', '_product'))[['name_customer', 'name_product']]  # Оставляем только нужное

    client_conn = final_df.groupby(['name_customer', 'name_product']).size().reset_index(name='common_orders')
    client_pairs = client_conn.pivot(index='name_customer', columns='name_product', values='common_orders').fillna(0)

    # Формирование матрицы смежности
    adjacency_matrix = client_pairs.dot(client_pairs.T)
    np.fill_diagonal(adjacency_matrix.values, 0)  # Исключаем диагональные элементы (самосвязи)

    # Список клиентов
    clients = adjacency_matrix.index

    # Генерируем рёбра с весом (вес равен количеству общих товаров)
    edges = [
        (src, dest, adjacency_matrix.loc[src, dest])  # Берём вес из матрицы
        for src in clients
        for dest in clients
        if adjacency_matrix.loc[src, dest] > 0
    ]
    return edges