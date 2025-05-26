from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

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


def get_subcategories(main_category_url):
    """Функция для получения подкатегорий из основной категории"""
    driver.get(main_category_url)
    time.sleep(3)

    subcategories = []
    try:
        sub_elements = WebDriverWait(driver, 10).until(
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
    time.sleep(3)

    product_links = []
    page = 1

    while True:
        print(f"Обрабатываем страницу {page}...")

        # Прокрутка страницы для загрузки всех товаров
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Сбор ссылок на товары
        try:
            product_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//a[contains(@class, "product-card__link")]')
                ))

            for product in product_elements:
                try:
                    href = product.get_attribute("href")
                    if href and href not in product_links:
                        product_links.append(href)
                except:
                    continue

            print(f"Найдено товаров: {len(product_links)}")

            # Проверяем наличие кнопки "Показать еще"
            try:
                next_button = driver.find_element(By.XPATH, '//button[contains(text(), "Показать еще")]')
                if next_button.is_enabled():
                    next_button.click()
                    time.sleep(3)
                    page += 1
                else:
                    break
            except:
                break

        except Exception as e:
            print(f"Ошибка при получении товаров: {str(e)}")
            break

    return product_links


try:
    # Переход на сайт
    print("Открываем сайт...")
    driver.get("https://www.perekrestok.ru/cat")
    time.sleep(5)

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
        except Exception as e:
            print(f"Ошибка при получении информации о категории: {str(e)}")
            continue

    # Собираем данные
    result = {}
    for title, href in categories_info:
        print(f"\nОбрабатываем категорию: {title}")
        subcategories = get_subcategories(href)

        category_data = {
            "url": href,
            "subcategories": {}
        }

        for sub_title, sub_href in subcategories:
            print(f"\n  Обрабатываем подкатегорию: {sub_title}")
            product_links = get_product_links(sub_href)
            category_data["subcategories"][sub_title] = {
                "url": sub_href,
                "products": product_links
            }
            print(f"  Найдено товаров: {len(product_links)}")
            for product in product_links:  # Печатаем первые 3 товара для примера
                print(f"    - {product}")

        result[title] = category_data

        # Возвращаемся на главную страницу категорий
        driver.get("https://www.perekrestok.ru/cat")
        time.sleep(3)

    # Вывод результатов
    print("\nРезультаты:")
    for category, data in result.items():
        print(f"\n{category} ({data['url']}):")
        for subcategory, sub_data in data["subcategories"].items():
            print(f"  - {subcategory} ({sub_data['url']}): {len(sub_data['products'])} товаров")

except Exception as e:
    print(f"Произошла ошибка: {str(e)}")
    driver.save_screenshot("error.png")

finally:
    driver.quit()