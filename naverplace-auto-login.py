from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pyperclip
import time
import random
import json
import os
import sys
from ai_reply_generator import AIReplyGenerator

# 설정 파일에서 계정 정보 로드
def load_config():
    """config.json에서 설정 로드"""
    config_file = "config.json"

    if not os.path.exists(config_file):
        print(f"오류: {config_file} 파일이 없습니다.")
        print("먼저 config_gui.py를 실행하여 설정을 저장해주세요.")
        sys.exit(1)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 필수 설정 값 확인
        required_keys = ["naver_id", "naver_pw", "business_name"]
        for key in required_keys:
            if key not in config or not config[key]:
                print(f"오류: {config_file}에 '{key}' 값이 없습니다.")
                print("config_gui.py를 실행하여 올바른 설정을 저장해주세요.")
                sys.exit(1)

        return config
    except json.JSONDecodeError as e:
        print(f"오류: {config_file} 파일이 올바른 JSON 형식이 아닙니다: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"오류: 설정 파일 로드 실패: {e}")
        sys.exit(1)

# 설정 로드
config = load_config()
NAVER_ID = config["naver_id"]
NAVER_PW = config["naver_pw"]
BUSINESS_NAME = config["business_name"]
OPENAI_API_KEY = config.get("openai_api_key", "")

print(f"설정 로드 완료: 업체명 = {BUSINESS_NAME}")

# AI 답글 생성기 초기화
ai_generator = None
if OPENAI_API_KEY:
    try:
        ai_generator = AIReplyGenerator(OPENAI_API_KEY)
        print("AI 답글 생성기 초기화 완료 (OpenAI API 사용)")
    except Exception as e:
        print(f"AI 답글 생성기 초기화 실패: {e}")
        print("템플릿 기반 답글을 사용합니다.")
else:
    print("OpenAI API 키가 없습니다. 템플릿 기반 답글을 사용합니다.")

def setup_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    # 필요시 headless 모드 해제
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # WebDriver 자동 다운로드 및 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 브라우저 창 크기 고정 (데스크톱 사이즈)
    driver.set_window_size(1920, 1080)
    driver.maximize_window()

    return driver

def debug_page_structure(driver):
    """페이지 구조 디버깅 - iframe 및 요소 확인"""
    print("\n=== 페이지 구조 디버깅 ===")

    # 현재 URL 확인
    print(f"현재 URL: {driver.current_url}")

    # 메인 프레임으로 이동
    driver.switch_to.default_content()

    # iframe 확인
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"\n발견된 iframe 개수: {len(iframes)}")
    for i, iframe in enumerate(iframes):
        iframe_id = iframe.get_attribute('id') or "없음"
        iframe_name = iframe.get_attribute('name') or "없음"
        iframe_src = (iframe.get_attribute('src') or "")[:100]
        print(f"  iframe {i+1}: id={iframe_id}, name={iframe_name}, src={iframe_src}")

    # HTML 저장
    try:
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("\n페이지 소스를 debug_page.html에 저장했습니다.")
    except Exception as e:
        print(f"HTML 저장 실패: {e}")

def login_to_naver_place(driver):
    """네이버 플레이스에 로그인"""
    try:
        # 1. 네이버 로그인 페이지로 직접 접속
        print("네이버 로그인 페이지 접속 중...")
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(2)

        # 2. 네이버 로그인 페이지에서 로그인 처리
        print("네이버 로그인 중...")
        
        # 아이디 입력 필드 찾기
        id_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "id"))
        )
        
        # 비밀번호 입력 필드 찾기
        pw_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pw"))
        )
        
        # pyperclip을 사용하여 아이디 입력
        print("아이디 입력 중...")
        pyperclip.copy(NAVER_ID)
        id_input.click()
        time.sleep(0.5)
        id_input.send_keys(Keys.CONTROL, 'v')
        time.sleep(0.5)
        
        # pyperclip을 사용하여 비밀번호 입력
        print("비밀번호 입력 중...")
        pyperclip.copy(NAVER_PW)
        pw_input.click()
        time.sleep(0.5)
        pw_input.send_keys(Keys.CONTROL, 'v')
        time.sleep(0.5)
        
        # 로그인 버튼 클릭 (여러 방법 시도)
        print("로그인 버튼 클릭 중...")
        try:
            # 방법 1: ID로 찾기
            login_submit = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "log.login"))
            )
            login_submit.click()
        except:
            try:
                # 방법 2: type="submit" 버튼 찾기
                login_submit = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                login_submit.click()
            except:
                # 방법 3: Enter 키로 로그인
                pw_input.send_keys(Keys.RETURN)
        
        # 로그인 완료 대기
        print("로그인 완료 대기 중...")
        time.sleep(2)

        # 3. 네이버 플레이스로 이동
        print("네이버 플레이스 사이트로 이동 중...")
        driver.get("https://new.smartplace.naver.com/")
        time.sleep(3)

        # 4. 내 업체 찾기에서 업체명 클릭
        print(f"'{BUSINESS_NAME}' 업체 찾는 중...")
        time.sleep(3)

        # 업체명으로 링크 찾기 (여러 방법 시도)
        try:
            # 방법 1: data-testid로 업체 카드 찾고 업체명 매칭
            print("업체 카드 목록 검색 중...")
            business_cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.Main_card_item__bTDIT[data-testid="main-biz-card"]'))
            )
            print(f"발견된 업체 카드 수: {len(business_cards)}")

            found = False
            for idx, card in enumerate(business_cards):
                try:
                    # 업체명 찾기 (Main_title__P_c6n 클래스의 strong 태그)
                    title_element = card.find_element(By.CSS_SELECTOR, 'strong.Main_title__P_c6n')
                    card_name = title_element.text.strip()
                    print(f"업체 {idx+1}: {card_name}")

                    if card_name == BUSINESS_NAME:
                        print(f"'{BUSINESS_NAME}' 업체 찾음! 클릭 시도...")
                        # 업체 카드 내의 링크 클릭
                        link = card.find_element(By.CSS_SELECTOR, 'a.Main_business_card__Q8DjV')
                        driver.execute_script("arguments[0].click();", link)
                        print(f"'{BUSINESS_NAME}' 업체 클릭 완료!")
                        found = True
                        break
                except Exception as e:
                    print(f"카드 {idx+1} 처리 중 오류: {e}")
                    continue

            if not found:
                print(f"'{BUSINESS_NAME}' 업체를 찾을 수 없습니다.")

        except Exception as e:
            print(f"업체 목록을 찾을 수 없습니다: {e}")
            # 방법 2: XPath로 직접 찾기
            try:
                print("XPath 방식으로 재시도 중...")
                business_link = driver.find_element(By.XPATH, f"//strong[contains(@class, 'Main_title__P_c6n') and text()='{BUSINESS_NAME}']/ancestor::a")
                driver.execute_script("arguments[0].click();", business_link)
                print(f"'{BUSINESS_NAME}' 업체 클릭 완료!")
            except Exception as e2:
                print(f"XPath 방식도 실패: {e2}")
        
        time.sleep(2)
        print("로그인 및 업체 선택 완료!")

        # 5. 팝업 닫기
        print("팝업 닫기 시도 중...")
        time.sleep(2)
        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.fn-booking.fn-booking-close1'))
            )
            close_button.click()
            print("팝업 닫기 완료!")
            time.sleep(1)
        except Exception as e:
            print(f"팝업이 없거나 닫기 실패: {e}")

        # 6. 리뷰 페이지로 이동
        print("리뷰 페이지로 이동 중...")

        # 디버깅: 페이지 구조 확인
        debug_page_structure(driver)

        try:
            # 여러 방법으로 리뷰 버튼 찾기 시도
            review_button = None

            # 방법 1: id="REVIEWS"를 가진 li 태그 내부의 a 태그 찾기 (가장 정확)
            try:
                review_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'li#REVIEWS a.link'))
                )
                print("방법 1로 리뷰 버튼 찾음 (li#REVIEWS)")
            except Exception as e:
                print(f"방법 1 실패: {e}")

            # 방법 2: data-area-code 속성으로 찾기
            if not review_button:
                try:
                    review_button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-area-code="gnb.review"]'))
                    )
                    print("방법 2로 리뷰 버튼 찾음 (data-area-code)")
                except Exception as e:
                    print(f"방법 2 실패: {e}")

            # 방법 3: data-ssr-action 속성으로 찾기
            if not review_button:
                try:
                    review_button = driver.find_element(By.CSS_SELECTOR, 'a[data-ssr-action*="reviews"]')
                    print("방법 3으로 리뷰 버튼 찾음 (data-ssr-action)")
                except Exception as e:
                    print(f"방법 3 실패: {e}")

            # 방법 4: XPath로 id="REVIEWS" 기반 찾기
            if not review_button:
                try:
                    review_button = driver.find_element(By.XPATH, "//li[@id='REVIEWS']//a")
                    print("방법 4로 리뷰 버튼 찾음 (XPath - id REVIEWS)")
                except Exception as e:
                    print(f"방법 4 실패: {e}")

            # 방법 5: 모든 a 태그 검색하여 "리뷰" 텍스트 포함 찾기
            if not review_button:
                try:
                    print("방법 5 시도: 전체 링크 검색 중...")
                    all_links = driver.find_elements(By.TAG_NAME, "a")
                    print(f"총 {len(all_links)}개의 링크 발견")
                    for link in all_links:
                        link_text = link.text.strip()
                        link_class = link.get_attribute("class") or ""
                        link_href = link.get_attribute("href") or ""
                        # 리뷰 텍스트 또는 reviews URL 포함
                        if (link_text == "리뷰" or "review" in link_href.lower()) and link.is_displayed():
                            review_button = link
                            print(f"방법 5로 리뷰 버튼 찾음 (텍스트: '{link_text}', href: '{link_href[:50]}')")
                            break
                except Exception as e:
                    print(f"방법 5 실패: {e}")

            if review_button:
                print(f"리뷰 버튼 찾음! href: {review_button.get_attribute('href')}")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", review_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", review_button)
                print("리뷰 페이지 이동 완료!")
                time.sleep(3)
            else:
                print("리뷰 버튼을 찾을 수 없습니다.")
                print("현재 페이지 URL:", driver.current_url)
                print("페이지 스크린샷을 저장합니다...")
                driver.save_screenshot("review_button_not_found.png")
                return

        except Exception as e:
            print(f"리뷰 버튼 클릭 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return

        # 7. 리뷰 답글 자동 작성
        process_reviews(driver)

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

def generate_ai_reply(review_text):
    """AI를 사용하여 리뷰 답글 생성"""
    global ai_generator

    if ai_generator:
        # AI 답글 생성기 사용
        try:
            result = ai_generator.generate_reply(
                review_content=review_text,
                brand_context=BUSINESS_NAME
            )
            print(f"  - AI 모델: {result['model_used']}, 토큰: {result['tokens_used']}")
            return result['reply']
        except Exception as e:
            print(f"  - AI 답글 생성 실패, 템플릿 사용: {e}")
            # 폴백: 템플릿 답글
            return _generate_template_reply()
    else:
        # 템플릿 답글 사용
        return _generate_template_reply()

def _generate_template_reply():
    """템플릿 기반 답글 생성"""
    replies = [
        "소중한 리뷰 감사드립니다! 좋은 경험을 하셨다니 정말 기쁩니다. 앞으로도 더 나은 서비스로 보답하겠습니다. 다음 방문도 기다리겠습니다!",
        "따뜻한 리뷰 남겨주셔서 감사합니다. 고객님의 만족이 저희의 가장 큰 보람입니다. 항상 최선을 다하겠습니다!",
        "방문해 주시고 좋은 평가 남겨주셔서 진심으로 감사드립니다. 더욱 노력하는 모습 보여드리겠습니다. 감사합니다!",
    ]
    return random.choice(replies)

def process_reviews(driver):
    """리뷰 답글 작성 프로세스"""
    try:
        print("\n=== 리뷰 답글 작성 시작 ===")

        # 리뷰 목록 찾기
        reviews = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.Review_pui_review__zhZdn'))
        )
        print(f"총 {len(reviews)} 개의 리뷰를 찾았습니다.")

        replied_count = 0

        for idx, review in enumerate(reviews):
            try:
                # 답글 쓰기 버튼이 있는지 확인 (답글이 없는 리뷰만 처리)
                reply_buttons = review.find_elements(By.CSS_SELECTOR, 'button.Review_btn_write__pFgSj[data-area-code="rv.replywrite"]')

                if not reply_buttons:
                    print(f"리뷰 {idx+1}: 이미 답글이 있습니다. 건너뜁니다.")
                    continue

                print(f"\n--- 리뷰 {idx+1} 처리 중 ---")

                # 1. 리뷰 내용 추출
                try:
                    review_text_element = review.find_element(By.CSS_SELECTOR, 'a[data-pui-click-code="text"]')
                    review_text = review_text_element.text.strip()
                    print(f"리뷰 내용: {review_text[:50]}...")
                except Exception as e:
                    print(f"리뷰 내용을 찾을 수 없습니다: {e}")
                    continue

                # 2. AI 답글 생성
                print("AI 답글 생성 중...")
                ai_reply = generate_ai_reply(review_text)
                print(f"생성된 답글: {ai_reply[:50]}...")

                # 3. 답글 쓰기 버튼 클릭
                print("답글 쓰기 버튼 클릭 중...")
                reply_button = reply_buttons[0]
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reply_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", reply_button)
                time.sleep(2)

                # 4. 답글 입력창 찾기 및 입력
                print("답글 입력 중...")
                try:
                    # 답글 입력창 (textarea 또는 contenteditable)
                    reply_input = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea, [contenteditable="true"]'))
                    )

                    # pyperclip 사용하여 답글 입력
                    pyperclip.copy(ai_reply)
                    reply_input.click()
                    time.sleep(0.5)
                    reply_input.send_keys(Keys.CONTROL, 'v')
                    time.sleep(1)

                    print("답글 입력 완료!")

                except Exception as e:
                    print(f"답글 입력창을 찾을 수 없습니다: {e}")
                    # ESC 키로 답글창 닫기
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    continue

                # 5. 등록 버튼 클릭
                print("등록 버튼 클릭 중...")
                try:
                    register_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.Review_btn_enter__az8i7[data-area-code="rv.replydone"]'))
                    )
                    driver.execute_script("arguments[0].click();", register_button)
                    print("답글 등록 완료!")
                    replied_count += 1

                    # 등록 후 대기
                    time.sleep(2)

                except Exception as e:
                    print(f"등록 버튼을 찾을 수 없습니다: {e}")
                    # ESC 키로 답글창 닫기
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(1)
                    continue

                # 6. 스크래핑 감지 방지를 위한 랜덤 대기 (5~10초)
                wait_time = random.randint(5, 10)
                print(f"스크래핑 감지 방지 대기 중... ({wait_time}초)")
                time.sleep(wait_time)

            except Exception as e:
                print(f"리뷰 {idx+1} 처리 중 오류 발생: {e}")
                continue

        print(f"\n=== 리뷰 답글 작성 완료 ===")
        print(f"총 {replied_count}개의 답글을 작성했습니다.")

    except Exception as e:
        print(f"리뷰 처리 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def main():
    """메인 함수"""
    driver = None
    try:
        driver = setup_driver()
        login_to_naver_place(driver)
        
        # 작업 완료 후 브라우저 유지 (필요시 주석 처리)
        print("작업 완료. 브라우저를 30초간 유지합니다...")
        time.sleep(30)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("브라우저 종료")

if __name__ == "__main__":
    main()

