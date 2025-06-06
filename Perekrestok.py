import os
import random
import re

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import requests
from urllib.parse import urljoin

# Настройка опций для Chrome
chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Инициализация драйвера с настройками
driver = webdriver.Chrome(options=chrome_options)

# Список нужных категорий
target_categories = [
    "Молоко, сыр, яйца",
    "Овощи, фрукты, грибы",
    "Макароны, крупы, масло, специи",
    "Чипсы, снеки, попкорн",
    "Шоколад, конфеты, сладости",
    "Соки, воды, напитки",
    "Хлеб и выпечка",
    "Мясо и птица",
    "Колбасные изделия",
    "Рыба",
    "Замороженные продукты",
    "Морепродукты",
    "Товары для мам и детей",
    "Соусы, кетчупы, майонезы",
    "Кофе, чай, какао, сахар",
    "Сухие завтраки, мюсли",
    "Продукты быстрого приготовления",
    "Консервация",
    "Здоровье",
    "Орехи, семечки, сухофрукты",
    "Мёд, варенье, джемы, сиропы",
]

# Создаем папку для сохранения данных
if not os.path.exists('products_data'):
    os.makedirs('products_data')

# Создаем DataFrame для хранения данных
columns = [
    'ID',  # Новый столбец для идентификатора
    'Категория', 'Подкатегория', 'Наименование товара', 'Состав',
    'Калории', 'Белки', 'Жиры', 'Углеводы', 'Фотография'
]

# Проверяем существование временного файла и загружаем данные, если он есть
temp_file = 'products_data/temp_products_data.xlsx'
if os.path.exists(temp_file):
    df = pd.read_excel(temp_file)
    print(f"Загружены промежуточные данные из {temp_file}")
else:
    df = pd.DataFrame(columns=columns)


def random_delay(min_sec=1, max_sec=5):
    """Случайная задержка между запросами"""
    time.sleep(random.uniform(min_sec, max_sec))


def save_temp_data():
    """Сохраняет промежуточные данные во временный файл"""
    try:
        df.to_excel(temp_file, index=False)
        print(f"\nПромежуточные данные сохранены в {temp_file}")
    except Exception as e:
        print(f"\nОшибка при сохранении временных данных: {str(e)}")


def get_subcategories(main_category_url):
    """Функция для получения подкатегорий из основной категории"""
    driver.get(main_category_url)
    random_delay(2, 4)  # Задержка перед поиском элементов

    subcategories = []
    try:
        sub_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//a[contains(@class, "sc-fKFxtB") and contains(@class, "epJywq")]')
            ))

        for sub in sub_elements:
            try:
                href = sub.get_attribute("href")
                title = sub.find_element(By.XPATH, './/span[contains(@class, "category-text")]').text
                subcategories.append((title, href))
            except:
                continue

    except Exception as e:
        print(f"Не удалось получить подкатегории: {str(e)}")

    return subcategories


def get_product_links(category_url):
    """Функция для получения ссылок на товары в категории"""
    driver.get(category_url)
    random_delay(3, 6)  # Задержка после загрузки страницы

    product_links = []
    page = 1

    while True:
        print(f"Обрабатываем страницу {page}...")

        # Прокрутка страницы для загрузки всех товаров
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            random_delay(1, 3)  # Случайная задержка между прокрутками
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Сбор ссылок на товары
        try:
            product_elements = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//a[contains(@class, "product-card__link")]')
                ))

            for product in product_elements:
                try:
                    href = product.get_attribute("href")
                    if href and href not in product_links:
                        product_links.append(urljoin("https://www.perekrestok.ru", href))
                        random_delay(0.2, 0.8)  # Задержка между обработкой товаров
                except:
                    continue

            print(f"Найдено товаров: {len(product_links)}")

            # Проверяем наличие кнопки "Показать еще"
            try:
                next_button = driver.find_element(By.XPATH, '//button[contains(text(), "Показать еще")]')
                if next_button.is_enabled():
                    next_button.click()
                    random_delay(2, 4)  # Задержка после клика
                    page += 1
                else:
                    break
            except:
                break

        except Exception as e:
            print(f"Ошибка при получении товаров: {str(e)}")
            break

    return product_links


def get_product_data(product_url, category, subcategory, product_id, subcategory_counter=None):
    """Функция для получения данных о товаре"""
    print(f"\n[Начало обработки] Товар ID: {product_id}, URL: {product_url}")
    driver.get(product_url)
    random_delay(3, 6)

    # Определяем имя подкатегории для папки
    folder_subcategory = subcategory if subcategory else f"subcategory_{subcategory_counter if subcategory_counter else product_id}"

    product_data = {
        'ID': product_id,
        'Категория': category,
        'Подкатегория': subcategory if subcategory else f"Без названия_{subcategory_counter if subcategory_counter else product_id}",
        'Наименование товара': '',
        'Состав': '',
        'Калории': '',
        'Белки': '',
        'Жиры': '',
        'Углеводы': '',
        'Фотография': f'{product_id}.jpg'
    }

    try:
        # Наименование товара
        name = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, '//h1[@class="sc-fubCzh ibFUIH product__title"]')
            )).text
        product_data['Наименование товара'] = name
    except:
        pass

    try:
        # Состав
        composition = driver.find_element(
            By.XPATH, '//div[@class="sc-fXoxaI hPnUzk"]/p[@class="sc-bQdRvg fHAQgq"]').text
        product_data['Состав'] = composition
    except:
        pass

    # Пищевая ценность
    try:
        nutrition_items = driver.find_elements(
            By.XPATH, '//div[@class="product-calories-item"]')

        for item in nutrition_items:
            try:
                title = item.find_element(
                    By.XPATH, './/div[@class="product-calories-item__title"]').text
                value = item.find_element(
                    By.XPATH, './/div[@class="product-calories-item__value"]').text

                if 'Калории' in title:
                    product_data['Калории'] = value
                elif 'Белки' in title:
                    product_data['Белки'] = value
                elif 'Жиры' in title:
                    product_data['Жиры'] = value
                elif 'Углеводы' in title:
                    product_data['Углеводы'] = value
                random_delay(0.1, 0.5)  # Задержка между обработкой элементов
            except:
                continue
    except:
        pass

    # Скачиваем фотографию
    try:
        # Создаем папки для категории и подкатегории
        # Заменяем проблемные символы в названиях
        safe_category = category.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?',
                                                                                                                  '_').replace(
            '"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        safe_subcategory = folder_subcategory.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*',
                                                                                                             '_').replace(
            '?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')

        category_folder = os.path.join('products_data', safe_category)
        subcategory_folder = os.path.join(category_folder, safe_subcategory)

        if not os.path.exists(category_folder):
            os.makedirs(category_folder)
        if not os.path.exists(subcategory_folder):
            os.makedirs(subcategory_folder)

        # Пробуем несколько способов найти изображение
        img_url = None
        img_path = os.path.join(subcategory_folder, f'{product_id}.jpg')

        # Способ 1: Ищем в figure с классом iiz
        try:
            figure = driver.find_element(By.XPATH, '//figure[contains(@class, "iiz")]')
            img_element = figure.find_element(By.TAG_NAME, 'img')
            img_url = img_element.get_attribute('src')
        except:
            pass

        # Способ 2: Ищем по itemprop="image"
        if not img_url:
            try:
                img_element = driver.find_element(By.XPATH, '//img[@itemprop="image"]')
                img_url = img_element.get_attribute('src')
            except:
                pass

        # Способ 3: Ищем по классу product__image
        if not img_url:
            try:
                img_element = driver.find_element(By.XPATH, '//img[contains(@class, "product__image")]')
                img_url = img_element.get_attribute('src')
            except:
                pass

        # Если нашли URL изображения
        if img_url:
            # Если URL относительный, делаем его абсолютным
            if not img_url.startswith('http'):
                img_url = urljoin(product_url, img_url)

            # Загружаем изображение
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            # Пробуем несколько раз загрузить изображение
            for attempt in range(3):
                try:
                    response = requests.get(img_url, headers=headers, stream=True, timeout=10)
                    if response.status_code == 200:
                        with open(img_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        print(f"Изображение сохранено: {img_path}")
                        break
                    else:
                        print(
                            f"Попытка {attempt + 1}: Не удалось загрузить изображение. Код статуса: {response.status_code}")
                except Exception as e:
                    print(f"Попытка {attempt + 1}: Ошибка при загрузке изображения: {str(e)}")
                    driver.refresh()
                    random_delay(2, 5)  # Задержка перед повторной попыткой
        else:
            print("Не удалось найти URL изображения товара")

    except Exception as e:
        print(f"[Ошибка] Не удалось сохранить изображение: {str(e)}")

    print("[Результат] Собранные данные:", product_data)
    return product_data


try:
    # Переход на сайт
    print("Открываем сайт...")
    driver.get("https://www.perekrestok.ru/cat")
    random_delay(4, 7)  # Имитация поведения человека

    # Получаем все ссылки на основные категории сразу
    print("Ищем основные категории...")
    main_category_elements = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//a[contains(@class, "sc-fKFxtB") and contains(@class, "kdHtPw")]')
        ))

    # Собираем информацию о категориях перед обработкой
    categories_info = []
    for element in main_category_elements:
        try:
            title = element.find_element(By.XPATH, './/div[contains(@class, "category-card__title")]').text
            if title in target_categories:
                href = element.get_attribute("href")
                categories_info.append((title, href))
                random_delay(0.5, 2)  # Задержка между обработкой категорий
        except Exception as e:
            print(f"Ошибка при получении информации о категории: {str(e)}")
            continue

    # Собираем данные
    for title, href in categories_info:
        print(f"\nОбрабатываем категорию: {title}")
        subcategories = get_subcategories(href)

        # Счетчик для подкатегорий без названия
        unnamed_subcategory_counter = 1

        for sub_title, sub_href in subcategories:
            print(f"\n  Обрабатываем подкатегорию: {sub_title if sub_title else 'Без названия'}")
            product_links = get_product_links(sub_href)

            # Локальный счетчик ID для каждой подкатегории (начинаем с 1)
            subcategory_product_id = 1

            for product_link in product_links[:2]:  # Ограничиваем 2 товарами для теста
                print(f"    Обрабатываем товар: {subcategory_product_id}")

                # Если подкатегория без названия, передаем счетчик
                current_subcategory_counter = unnamed_subcategory_counter if not sub_title else None

                product_data = get_product_data(
                    product_link, title,
                    sub_title if sub_title else "",
                    subcategory_product_id,
                    current_subcategory_counter
                )

                df = pd.concat([df, pd.DataFrame([product_data])], ignore_index=True)
                subcategory_product_id += 1
                random_delay(1, 3)  # Задержка между товарами

            # Сохраняем промежуточные данные после обработки каждой подкатегории
            save_temp_data()

            # Увеличиваем счетчик только для подкатегорий без названия
            if not sub_title:
                unnamed_subcategory_counter += 1

    # Сохраняем финальные данные в Excel
    final_file = 'products_data/products.xlsx'
    df.to_excel(final_file, index=False)
    print(f"\nФинальные данные успешно сохранены в {final_file}")

    # Удаляем временный файл после успешного завершения
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print(f"Временный файл {temp_file} удален")

except Exception as e:
    print(f"Произошла ошибка: {str(e)}")
    driver.save_screenshot("error.png")

    # Сохраняем данные перед завершением в случае ошибки
    save_temp_data()

finally:
    driver.quit()