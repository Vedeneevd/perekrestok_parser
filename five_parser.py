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

# Список нужных категорий (из вашего вывода)
target_categories = [
    "Готовая еда",
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

try:
    # Переход на сайт Пятёрочки
    print("Открываем сайт...")
    driver.get("https://www.perekrestok.ru/cat")

    # Ожидание загрузки страницы
    print("Ожидаем загрузки...")
    time.sleep(5)

    # Ожидание появления категорий
    print("Ищем категории...")
    wait = WebDriverWait(driver, 20)
    categories = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, '//a[contains(@class, "sc-fKFxtB") and contains(@class, "kdHtPw")]')
    ))

    # Сбор только нужных ссылок
    category_links = []
    for category in categories:
        try:
            # Ищем заголовок категории разными способами
            title_element = category.find_element(By.XPATH, './/div[contains(@class, "category-card__title")]')
            title = title_element.text
            if title in target_categories:
                href = category.get_attribute("href")
                category_links.append((title, href))
                print(f"Найдена нужная категория: {title} - {href}")
        except Exception as e:
            # Пропускаем категории, которые не удалось распарсить
            continue

    # Вывод результатов
    print(f"\nИтого найдено {len(category_links)} нужных категорий из {len(target_categories)}:")
    for i, (title, href) in enumerate(category_links, 1):
        print(f"{i}. {title}: {href}")

except Exception as e:
    print(f"Произошла ошибка: {str(e)}")
    driver.save_screenshot("error.png")
    print("Скриншот ошибки сохранен как error.png")

finally:
    # Закрытие браузера
    driver.quit()
    print("Браузер закрыт.")