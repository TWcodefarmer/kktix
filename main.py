import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import math

def kktix_login(driver, timeout, account, password):
    target_page = "https://kktix.com/users/sign_in?back_to=https://kktix.com/"
    driver.get(target_page)
    current_url = driver.current_url
    # 自動輸入帳號
    account_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user_login")))
    account_input.send_keys(account)
    # 自動輸入密碼
    password_input = driver.find_element(By.ID, "user_password")
    password_input.send_keys(password)
    # 點擊登入
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="new_user"]/input[3]')))
    login_button.click()
    # 登入後檢查 URL 是否變更
    try: 
        WebDriverWait(driver, timeout).until(EC.url_changes(current_url))
        return True
    except Exception:
        return False

def click_random_ticket(driver, timeout, START_PERCENTAGE, END_PERCENTAGE):
    # 使用 BeautifulSoup 解析頁面
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # 解析票種資訊
    ticket_divs = soup.find_all('div', class_='ticket-unit')
    data = []
    for idx, ticket in enumerate(ticket_divs):
        ticket_ID = soup.find_all('div', id=lambda x: x and 'ticket' in x)[idx]['id']
        ticket_price = ticket.find('span', class_='ticket-price').get_text(strip=True)
        ticket_name = ticket.find('span', class_='ticket-name').get_text(strip=True)
        # 獲取可用座位數
        try:
            available_seats = ticket.find('input', class_='ng-pristine ng-untouched ng-valid ng-not-empty').get('value')
        except:
            available_seats = ticket.find('span', class_='ticket-quantity ng-binding ng-scope').get_text(strip=True)
        data.append({'ID': ticket_ID, '票區': ticket_name, '票價': ticket_price, '空位': available_seats})
    data
    # 篩選可用票種
    filtered_data = [item for item in data if item['空位'] == '0']
    # filtered_data = [item for item in data if item['空位'] != '已售完']
    # filtered_data = [item for item in filtered_data if item['空位'] != '暫無票券']
    # filtered_data = [item for item in filtered_data if item['空位'] != '尚未開賣']
    filtered_data = [item for item in filtered_data if '身障' not in item['票區']]
    filtered_data = [item for item in filtered_data if '愛心' not in item['票區']]
    filtered_data = [item for item in filtered_data if '輪椅' not in item['票區']]

    if len(filtered_data) > 0:
        start_index = int(len(filtered_data) * START_PERCENTAGE)
        end_index = math.ceil(len(filtered_data) * END_PERCENTAGE)
        # 隨機選取一個票區
        selected_items = filtered_data[start_index:end_index]
        print(f'目標票種,共{len(selected_items)}種:',selected_items)
        random_row = random.choice(selected_items)
        target = random_row['ID']
        # 點擊隨機票區的按鈕
        try:   
            ticket_div = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, f"{target}")))
            input_element = ticket_div.find_element(By.XPATH, ".//input[@ng-model='ticketModel.quantity']")
            input_element.clear()  # 清空 input 元素
            input_element.send_keys("1")  # 輸入 1
            print('點擊票區成功,一張')
            return True
        except:
            print('點擊票區失敗')
            return False
    else:
        print('當前無票可刷')
        return False

def click_agree_term(driver):
    try:
        # 點擊同意條款的 checkbox
        checkbox = driver.find_element(By.ID, "person_agree_terms")
        checkbox.click()
        print('點擊同意條款成功')
        return True
    except:
        print('點擊同意條款失敗')
        return False

def click_auto_seat(driver, timeout):
    try:
        # 找到 電腦配位
        span_element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//span[text()='電腦配位']")))
        button = span_element.find_element(By.XPATH, "..")
        button.click()
        print(f"點擊電腦配位成功")
        return True
    except Exception as e:
        print(f"點擊電腦配位失敗")
        return False

def click_next_step(driver, timeout):
    try:
        # 找到 下一步
        span_element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//span[text()='下一步']")))
        button = span_element.find_element(By.XPATH, "..")
        button.click()
        print(f"點擊下一步成功")
        return True
    except Exception as e:
        print(f"點擊下一步失敗")
        return False
    
def keyin_answer(driver,answer):
    try:
        # 輸入訊息
        input_box = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='請填入答案']")))
        input_box.clear()  # 清空 input 元素
        input_box.send_keys(answer)  # 輸入內容
        print(f"輸入訊息成功")
        return True
    except Exception as e:
        print(f"輸入訊息失敗")
        return False

def check_alert(driver, timeout):
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print("捕捉到彈出視窗：", alert.text)
        alert.accept()
        return True
    except Exception as e:
        print("彈出視窗未出現")
        return False

def check_page_changed(driver, timeout, mystery_page_1):
    try: 
        WebDriverWait(driver, timeout).until(EC.url_changes(mystery_page_1))
        print('網站改變')
        return True
    except Exception:
        print('網站不變')
        return False


# 使用正確的參數名稱指定版本
service = Service(ChromeDriverManager(driver_version="129.0.6668.90").install())
# 設定 Chrome 的選項
chrome_options = Options()
chrome_options.add_argument("window-size=1500,1000")  # 設定視窗大小 (寬 x 高)
chrome_options.add_argument("window-position=0,0")  # 設定視窗位置 (x, y)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 執行登入
account = "abcsddd"
password = "abcdddss."
try_for = 4 # 重新嘗試登入次數(驗證碼或網路問題)
for i in range(try_for):
    if kktix_login(driver, timeout=60, account=account, password=password):
        print('登入成功')
        break
    print('登入失敗')
    raise ValueError('登入失敗')

# 選擇票區
START_PERCENTAGE = float(0) / 100 #不可改
END_PERCENTAGE = float(51) / 100
REFRESH_TIME = 1 # 多久刷一次
wait_for_confirm = 300
# mystery_page_1 = "https://kktix.com/events/osnctrlnkh2024/registrations/new" # 有提問
mystery_page_1 = "https://kktix.com/events/911lanpaliroad2024/registrations/new" # 
# mystery_page_1 = "https://kktix.com/events/oxswsr/registrations/new" # TEST
answer = '9'
status = False
while not status:
    if not click_random_ticket(driver=driver, timeout=1, START_PERCENTAGE=START_PERCENTAGE, END_PERCENTAGE=END_PERCENTAGE):
        # 重新整理
        driver.get(mystery_page_1)
        time.sleep(REFRESH_TIME)
    else:
        click_agree_term(driver=driver)
        if keyin_answer(driver=driver,answer=answer):
            print('b')
            if click_next_step(driver=driver, timeout=0.2):
                print('d')
                for i in range(wait_for_confirm//2):
                    # 檢查 點擊電腦配位 是否有跳轉到結帳頁面
                    if check_page_changed(driver=driver, timeout=1, mystery_page_1=mystery_page_1):
                        status = True # 成功訂票斷開迴圈
                        print('成功訂票斷開迴圈')
                        break
                    check_alert(driver=driver,timeout=1)
            elif click_auto_seat(driver=driver, timeout=0.2):
                print('c')
                for i in range(wait_for_confirm//2):
                    # 檢查 點擊電腦配位 是否有跳轉到結帳頁面
                    if check_page_changed(driver=driver, timeout=1, mystery_page_1=mystery_page_1):
                        status = True # 成功訂票斷開迴圈
                        print('成功訂票斷開迴圈')
                        break
                    check_alert(driver=driver,timeout=1)
        elif click_next_step(driver=driver, timeout=0.2):
            print('f')
            for i in range(wait_for_confirm//2):
                # 檢查 點擊電腦配位 是否有跳轉到結帳頁面
                if check_page_changed(driver=driver, timeout=1, mystery_page_1=mystery_page_1):
                    status = True # 成功訂票斷開迴圈
                    print('成功訂票斷開迴圈')
                    break
                check_alert(driver=driver,timeout=1)
        elif click_auto_seat(driver=driver, timeout=0.2):
            print('a')
            for i in range(wait_for_confirm//2):
                # 檢查 點擊電腦配位 是否有跳轉到結帳頁面
                if check_page_changed(driver=driver, timeout=1, mystery_page_1=mystery_page_1):
                    status = True # 成功訂票斷開迴圈
                    print('成功訂票斷開迴圈')
                    break
                check_alert(driver=driver,timeout=1)
        else:
            print('refresh4, try again')
            raise ValueError('error,無購票可點')
        
time.sleep(600000)




    




