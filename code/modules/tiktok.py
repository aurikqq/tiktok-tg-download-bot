import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pickle
import os
import tiktok_send

cookie_path = "tiktok_cookies.pkl"


async def main():
    print(0)
    driver = webdriver.Chrome()
    print(3)

    if os.path.exists(cookie_path):
        print(1)
        driver.get("https://www.tiktok.com")
        with open("tiktok_cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
        print(2)
        driver.get("https://www.tiktok.com/login")
        print("Войдите в аккаунт TikTok вручную.")
        time.sleep(60)

        cookies = driver.get_cookies()
        with open(cookie_path, "wb") as file:
            pickle.dump(cookies, file)

    # Открываем раздел личных сообщений
    driver.get("https://www.tiktok.com/messages")
    time.sleep(10)

    video_elements = []

    while True:
        previous_elements = video_elements if video_elements else video_elements
        video_elements = driver.find_elements(By.CSS_SELECTOR, f"[class*='{"DivVideoContainer"}']")
        new_video_elements = video_elements[len(previous_elements):]

        video_links = []

        for video_element in new_video_elements:
            try:
                video_element.click()
                time.sleep(4)

                video_url = driver.current_url
                video_links.append(video_url)

                driver.back()
                time.sleep(6)

            except Exception as e:
                print(e)
                continue

        if video_links:
            for link in video_links:
                # Вместо синхронного вызова используем await
                await tiktok_send.send_tiktok(link)
        time.sleep(10)


# Запускаем асинхронный главный блок
asyncio.run(main())
