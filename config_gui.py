import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class ConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("네이버 플레이스 자동 답글 - 설정")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        # 설정 파일 경로
        self.config_file = "config.json"

        # 기존 설정 로드
        self.load_config()

        # UI 생성
        self.create_widgets()

    def create_widgets(self):
        """UI 위젯 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 제목
        title_label = ttk.Label(main_frame, text="네이버 플레이스 자동 답글 설정",
                               font=("맑은 고딕", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 네이버 아이디
        ttk.Label(main_frame, text="네이버 아이디:", font=("맑은 고딕", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=10
        )
        self.id_entry = ttk.Entry(main_frame, width=30, font=("맑은 고딕", 10))
        self.id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        self.id_entry.insert(0, self.config.get("naver_id", ""))

        # 네이버 비밀번호
        ttk.Label(main_frame, text="네이버 비밀번호:", font=("맑은 고딕", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=10
        )
        self.pw_entry = ttk.Entry(main_frame, width=30, show="*", font=("맑은 고딕", 10))
        self.pw_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        self.pw_entry.insert(0, self.config.get("naver_pw", ""))

        # 비밀번호 표시/숨김 체크박스
        self.show_pw_var = tk.BooleanVar()
        show_pw_check = ttk.Checkbutton(
            main_frame,
            text="비밀번호 표시",
            variable=self.show_pw_var,
            command=self.toggle_password
        )
        show_pw_check.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))

        # 업체명
        ttk.Label(main_frame, text="업체명:", font=("맑은 고딕", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=10
        )
        self.business_entry = ttk.Entry(main_frame, width=30, font=("맑은 고딕", 10))
        self.business_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        self.business_entry.insert(0, self.config.get("business_name", ""))

        # OpenAI API 키
        ttk.Label(main_frame, text="OpenAI API 키:", font=("맑은 고딕", 10)).grid(
            row=5, column=0, sticky=tk.W, pady=10
        )
        self.api_key_entry = ttk.Entry(main_frame, width=30, show="*", font=("맑은 고딕", 10))
        self.api_key_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        self.api_key_entry.insert(0, self.config.get("openai_api_key", ""))

        # API 키 표시/숨김 체크박스
        self.show_api_var = tk.BooleanVar()
        show_api_check = ttk.Checkbutton(
            main_frame,
            text="API 키 표시",
            variable=self.show_api_var,
            command=self.toggle_api_key
        )
        show_api_check.grid(row=6, column=1, sticky=tk.W, padx=(10, 0))

        # 구분선
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=(10, 0))

        # 저장 버튼
        save_btn = ttk.Button(
            button_frame,
            text="저장",
            command=self.save_config,
            width=15
        )
        save_btn.grid(row=0, column=0, padx=5)

        # 저장 후 실행 버튼
        save_run_btn = ttk.Button(
            button_frame,
            text="저장 후 실행",
            command=self.save_and_run,
            width=15
        )
        save_run_btn.grid(row=0, column=1, padx=5)

        # 취소 버튼
        cancel_btn = ttk.Button(
            button_frame,
            text="취소",
            command=self.root.quit,
            width=15
        )
        cancel_btn.grid(row=0, column=2, padx=5)

        # 상태 표시 레이블
        self.status_label = ttk.Label(main_frame, text="", foreground="green",
                                     font=("맑은 고딕", 9))
        self.status_label.grid(row=9, column=0, columnspan=2, pady=(15, 0))

    def toggle_password(self):
        """비밀번호 표시/숨김 토글"""
        if self.show_pw_var.get():
            self.pw_entry.config(show="")
        else:
            self.pw_entry.config(show="*")

    def toggle_api_key(self):
        """API 키 표시/숨김 토글"""
        if self.show_api_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")

    def load_config(self):
        """설정 파일 로드"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"설정 파일 로드 실패: {e}")
                self.config = {}
        else:
            self.config = {}

    def save_config(self):
        """설정 저장"""
        # 입력값 가져오기
        naver_id = self.id_entry.get().strip()
        naver_pw = self.pw_entry.get().strip()
        business_name = self.business_entry.get().strip()
        openai_api_key = self.api_key_entry.get().strip()

        # 유효성 검사
        if not naver_id:
            messagebox.showerror("입력 오류", "네이버 아이디를 입력해주세요.")
            self.id_entry.focus()
            return False

        if not naver_pw:
            messagebox.showerror("입력 오류", "네이버 비밀번호를 입력해주세요.")
            self.pw_entry.focus()
            return False

        if not business_name:
            messagebox.showerror("입력 오류", "업체명을 입력해주세요.")
            self.business_entry.focus()
            return False

        # OpenAI API 키는 선택 사항 (없으면 템플릿 답글 사용)
        if not openai_api_key:
            result = messagebox.askyesno(
                "API 키 없음",
                "OpenAI API 키가 입력되지 않았습니다.\n템플릿 기반 답글만 사용됩니다.\n계속하시겠습니까?"
            )
            if not result:
                self.api_key_entry.focus()
                return False

        # 설정 저장
        config_data = {
            "naver_id": naver_id,
            "naver_pw": naver_pw,
            "business_name": business_name,
            "openai_api_key": openai_api_key
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            self.status_label.config(text="✓ 설정이 저장되었습니다.", foreground="green")
            return True

        except Exception as e:
            messagebox.showerror("저장 오류", f"설정 저장 중 오류가 발생했습니다:\n{str(e)}")
            return False

    def save_and_run(self):
        """저장 후 메인 프로그램 실행"""
        if self.save_config():
            self.status_label.config(text="✓ 설정이 저장되었습니다. 프로그램을 시작합니다...",
                                    foreground="blue")
            self.root.after(1000, self.run_main_program)

    def run_main_program(self):
        """메인 프로그램 실행"""
        self.root.destroy()
        # 여기서 메인 자동화 스크립트를 실행
        import subprocess
        subprocess.Popen(["python", "naverplace-auto-login.py"])

def main():
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
