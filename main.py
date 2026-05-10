import os
import threading
import tkinter as tk
from tkinter import font

from dotenv import load_dotenv

from src.qiita_client import QiitaAPIError, fetch_all_articles

load_dotenv()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Qiita 記事タイトル取得ツール")
        self.resizable(False, False)
        self._articles: list[dict] = []
        # .env からトークンを取得（なければ None）
        self._env_token: str | None = os.environ.get("QIITA_TOKEN")
        self._build_ui()

    def _build_ui(self):
        # --- トークン入力（.env 未設定時のみ表示） ---
        if self._env_token:
            self._token_var = None
            tk.Label(self, text="トークン: .env から読み込み済み", fg="green").pack(
                padx=16, pady=(16, 4)
            )
        else:
            token_frame = tk.Frame(self)
            token_frame.pack(fill="x", padx=16, pady=(16, 4))
            tk.Label(token_frame, text="Qiita Token:").pack(side="left")
            self._token_var = tk.StringVar()
            tk.Entry(token_frame, textvariable=self._token_var, show="*", width=40).pack(
                side="left", padx=(8, 0)
            )

        # --- 取得ボタン ---
        self._fetch_btn = tk.Button(self, text="  取得する  ", command=self._on_fetch)
        self._fetch_btn.pack(pady=8)

        # --- ステータスラベル ---
        initial_status = (
            "「取得する」を押してください"
            if self._env_token
            else "トークンを入力して「取得する」を押してください"
        )
        self._status_var = tk.StringVar(value=initial_status)
        self._status_label = tk.Label(self, textvariable=self._status_var, fg="gray")
        self._status_label.pack()

        # --- タイトル一覧（スクロール付き） ---
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=16, pady=8)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self._listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            width=60,
            height=20,
            selectmode="extended",
            font=font.Font(size=11),
        )
        self._listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self._listbox.yview)

        # --- コピーボタン ---
        self._copy_btn = tk.Button(
            self, text="  コピーする  ", command=self._on_copy, state="disabled"
        )
        self._copy_btn.pack(pady=(0, 16))

    # -------------------------------------------------------
    def _on_fetch(self):
        token = self._env_token or (self._token_var and self._token_var.get().strip())
        if not token:
            self._set_status("トークンを入力してください", color="red")
            return

        self._fetch_btn.config(state="disabled")
        self._copy_btn.config(state="disabled")
        self._listbox.delete(0, "end")
        self._set_status("取得中...", color="gray")

        threading.Thread(target=self._fetch_worker, args=(token,), daemon=True).start()

    def _fetch_worker(self, token: str):
        try:
            articles = fetch_all_articles(token)
            self.after(0, self._on_fetch_done, articles)
        except QiitaAPIError as e:
            self.after(0, self._on_fetch_error, str(e))
        except Exception as e:
            self.after(0, self._on_fetch_error, f"予期しないエラー: {e}")

    def _on_fetch_done(self, articles: list[dict]):
        self._articles = articles
        for article in articles:
            self._listbox.insert("end", article["title"])

        count = len(articles)
        self._set_status(f"{count} 件取得しました", color="green")
        self._fetch_btn.config(state="normal")
        if count:
            self._copy_btn.config(state="normal")

    def _on_fetch_error(self, message: str):
        self._set_status(message, color="red")
        self._fetch_btn.config(state="normal")

    # -------------------------------------------------------
    def _on_copy(self):
        if not self._articles:
            return
        titles = "\n".join(a["title"] for a in self._articles)
        self.clipboard_clear()
        self.clipboard_append(titles)
        self._set_status("コピーしました！", color="blue")

    def _set_status(self, message: str, color: str = "gray"):
        self._status_var.set(message)
        self._status_label.config(fg=color)


if __name__ == "__main__":
    app = App()
    app.mainloop()
