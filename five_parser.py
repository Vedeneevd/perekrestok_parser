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
    time.sleep(3)  # Ожидание загрузки

    subcategories = []
    try:
        # Ищем все элементы подкатегорий
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
        result[title] = {
            "url": href,
            "subcategories": subcategories
        }
        print(f"Найдено подкатегорий: {len(subcategories)}")
        for sub in subcategories:
            print(f"  - {sub[0]}: {sub[1]}")

        # Возвращаемся на главную страницу категорий
        driver.get("https://www.perekrestok.ru/cat")
        time.sleep(3)  # Даем странице время для загрузки

    # Вывод результатов
    print("\nРезультаты:")
    for category, data in result.items():
        print(f"\n{category} ({data['url']}):")
        for sub in data["subcategories"]:
            print(f"  - {sub[0]}: {sub[1]}")

except Exception as e:
    print(f"Произошла ошибка: {str(e)}")
    driver.save_screenshot("error.png")

finally:
    driver.quit()