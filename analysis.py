import pandas as pd
import numpy as np

def top5(res):
    """
    Анализирует входящие данные и выбирает топ-5 клиентов по количеству сделанных ими заказов.

    Parameters
    ----------
    res : list
        Входящие данные из базы данных. Представляют собой список кортежей с двумя частями:
        - res[0]: кортеж (список клиентов, список заголовков);
        - res[1]: кортеж (список заказов, список заголовков).

    Returns
    -------
    pd.DataFrame
        DataFrame с именем клиента и числом заказов, упорядоченный по количеству заказов в обратном порядке.

    Notes
    -----
    Используется объединение двух датафреймов (клиентов и заказов) для определения частоты заказов.
    """
    # Формируем датафреймы из полученных данных
    df_customers = pd.DataFrame(res[0][0], columns=res[0][1])
    df_orders = pd.DataFrame(res[1][0], columns=res[1][1])

    # Объединяем заказы и клиентов по внешнему ключу
    df = df_orders.merge(df_customers, left_on='customer_id', right_on='id', how='left')

    # Группа по имени клиента и подсчёт числа заказов
    top_customers = df.groupby('name')['id_x'].count().reset_index().rename(columns={'id_x': 'number_of_orders'})

    # Отбираем пять лучших клиентов и сортируем по количеству заказов
    top_customers = top_customers.nlargest(5, 'number_of_orders')
    top_customers.sort_values(by='number_of_orders', ascending=False, inplace=True)

    return top_customers


def orders_per_day(res):
    """
    Обрабатывает поступающие данные и формирует отчет по количеству заказов в разные дни.

    Parameters
    ----------
    res : tuple
        Входящий кортеж с одним элементом: список заказов и список заголовков.

    Returns
    -------
    pd.DataFrame
        DataFrame с двумя колонками: дата и количество заказов за день.

    Notes
    -----
    Данные объединяются по нормированной дате (без учета времени суток), что позволяет считать общее количество заказов по дням.
    """
    # Формируем датафрейм из входящих данных
    df_orders = pd.DataFrame(res[0], columns=res[1])

    # Преобразуем даты в нужный формат
    df_orders['date_created'] = df_orders['date_created'].apply(lambda x: x.split('.')[0])
    df_orders['date_created'] = pd.to_datetime(df_orders['date_created'], format='%Y-%m-%d %H:%M:%S')

    # Группируем по нормализованной дате и считаем количество заказов
    orders_p_day = df_orders.groupby(df_orders['date_created'].dt.normalize()).size().reset_index(name='counts')

    # Преобразуем формат даты для удобочитаемости
    orders_p_day['date_created'] = orders_p_day['date_created'].dt.strftime('%d-%m-%Y')

    # Чистим данные от возможных пустых значений
    orders_p_day = orders_p_day.query('counts.notnull() & counts != ""')

    return orders_p_day


def client_connections(res):
    """
    Анализирует данные о клиентах и продуктах, формируя рёбра графа для визуализации взаимодействия клиентов по общим товарам.

    Parameters
    ----------
    res : list
        Входящие данные из базы данных в виде четырёх кортежей:
        - res[0]: кортеж (список клиентов, список заголовков);
        - res[1]: кортеж (список продуктов, список заголовков);
        - res[2]: кортеж (список заказов, список заголовков);
        - res[3]: кортеж (список позиций заказов, список заголовков).

    Returns
    -------
    list
        Список рёбер графа в виде кортежей (node1, node2, weight), где:
        - node1 и node2 — имена клиентов;
        - weight — количество общих товаров.

    Notes
    -----
    Данный метод объединяет различные сущности (клиенты, продукты, позиции заказов) и создаёт матрицу сходства клиентов по общим покупкам.
    """
    # Создаём датафреймы из входящих данных
    df_customers = pd.DataFrame(res[0][0], columns=res[0][1])
    df_products = pd.DataFrame(res[1][0], columns=res[1][1])
    df_orders = pd.DataFrame(res[2][0], columns=res[2][1])
    df_order_items = pd.DataFrame(res[3][0], columns=res[3][1])

    # Последовательное соединение данных для анализа общих товаров
    merged_df = df_orders.merge(df_customers, left_on='customer_id', right_on='id', how='left',
                               suffixes=('_orders', '_customers'))
    merged_df2 = merged_df.merge(df_order_items, left_on='id_orders', right_on='order_id', how='inner')
    final_df = merged_df2.merge(df_products, left_on='product_id', right_on='id', how='inner',
                              suffixes=('_customer', '_product'))[['name_customer', 'name_product']]

    # Определяем частоту совместного приобретения товаров разными клиентами
    client_conn = final_df.groupby(['name_customer', 'name_product']).size().reset_index(name='common_orders')
    client_pairs = client_conn.pivot(index='name_customer', columns='name_product', values='common_orders').fillna(0)

    # Матрица смежности для графического представления связей
    adjacency_matrix = client_pairs.dot(client_pairs.T)
    np.fill_diagonal(adjacency_matrix.values, 0)  # Убираем само-связи

    # Генерируем рёбра графа
    clients = adjacency_matrix.index
    edges = []
    for src in clients:
        for dest in clients:
            if adjacency_matrix.loc[src, dest] > 0:
                edges.append((src, dest, adjacency_matrix.loc[src, dest]))

    return edges