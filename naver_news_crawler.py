"""네이버 검색 결과에서 뉴스 기사를 검색하고 본문을 보는 PyQt6 GUI 앱.

네이버 검색 결과 페이지는 자바스크립트로 내용을 렌더링하므로
Selenium으로 페이지를 먼저 로딩한 뒤, BeautifulSoup4로 결과를 파싱한다.
개별 기사 본문(news.naver.com)은 서버에서 바로 렌더링되므로 requests로 가져온다.
검색과 본문 로딩은 각각 QThread에서 실행해 GUI가 멈추지 않도록 한다.
"""

import sys
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

DEFAULT_QUERY = "SK플라즈마"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def build_search_url(query):
    return f"https://search.naver.com/search.naver?where=nexearch&ssc=tab.nx.all&query={quote(query)}"


def render_search_page(search_url):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="n.news.naver.com"]'))
        )
        return driver.page_source
    finally:
        driver.quit()


def find_title(news_link_tag):
    """네이버뉴스 링크에서 상위로 올라가며 원문 기사 링크의 제목 텍스트를 찾는다."""
    node = news_link_tag
    for _ in range(8):
        node = node.parent
        if node is None:
            return None
        candidates = [
            a for a in node.find_all("a")
            if a.get("href") and "naver.com" not in a.get("href") and a.get("href") != "#"
        ]
        texts = [a.get_text(strip=True) for a in candidates]
        texts = [t.replace("새 창 열림", "").strip() for t in texts if t]
        texts = [t for t in texts if t]
        if texts:
            return texts[0]
    return None


def collect_news_items(search_url):
    html = render_search_page(search_url)
    soup = BeautifulSoup(html, "html.parser")

    items = []
    seen_urls = set()
    for a in soup.select('a[href*="n.news.naver.com/mnews/article"]'):
        url = a.get("href")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        items.append({"title": find_title(a) or "(제목 없음)", "url": url})
    return items


def extract_article_text(article_url):
    res = requests.get(article_url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    res.encoding = res.apparent_encoding

    soup = BeautifulSoup(res.text, "html.parser")
    body = soup.select_one("#dic_area")
    if not body:
        return "[본문을 찾을 수 없습니다]"

    for tag in body.select("script, style"):
        tag.decompose()
    return body.get_text("\n", strip=True)


class SearchWorker(QThread):
    succeeded = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            items = collect_news_items(build_search_url(self.query))
            self.succeeded.emit(items)
        except Exception as e:
            self.failed.emit(str(e))


class ArticleWorker(QThread):
    succeeded = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            text = extract_article_text(self.url)
            self.succeeded.emit(text)
        except Exception as e:
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("네이버 뉴스 크롤러")
        self.resize(1000, 640)

        self.search_worker = None
        self.article_worker = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        search_row = QHBoxLayout()
        self.query_edit = QLineEdit(DEFAULT_QUERY)
        self.query_edit.returnPressed.connect(self.start_search)
        self.search_btn = QPushButton("검색")
        self.search_btn.clicked.connect(self.start_search)
        search_row.addWidget(QLabel("검색어"))
        search_row.addWidget(self.query_edit)
        search_row.addWidget(self.search_btn)
        root.addLayout(search_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.load_article)
        splitter.addWidget(self.list_widget)

        self.body_edit = QTextEdit()
        self.body_edit.setReadOnly(True)
        splitter.addWidget(self.body_edit)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        root.addWidget(splitter, 1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("검색어를 입력하고 검색 버튼을 누르세요.")

    def start_search(self):
        query = self.query_edit.text().strip()
        if not query or (self.search_worker and self.search_worker.isRunning()):
            return

        self.search_btn.setEnabled(False)
        self.list_widget.clear()
        self.body_edit.clear()
        self.status.showMessage(f"'{query}' 뉴스 검색 중... (브라우저 렌더링에 몇 초 걸릴 수 있습니다)")

        self.search_worker = SearchWorker(query)
        self.search_worker.succeeded.connect(self.on_search_succeeded)
        self.search_worker.failed.connect(self.on_search_failed)
        self.search_worker.start()

    def on_search_succeeded(self, items):
        self.search_btn.setEnabled(True)

        if not items:
            self.status.showMessage("검색된 뉴스가 없습니다.")
            return

        for item in items:
            list_item = QListWidgetItem(item["title"])
            list_item.setData(Qt.ItemDataRole.UserRole, item["url"])
            self.list_widget.addItem(list_item)

        self.status.showMessage(f"{len(items)}개의 기사를 찾았습니다. 목록을 클릭해 본문을 확인하세요.")

    def on_search_failed(self, message):
        self.search_btn.setEnabled(True)
        self.status.showMessage(f"검색 실패: {message}")

    def load_article(self, list_item):
        if self.article_worker and self.article_worker.isRunning():
            return

        url = list_item.data(Qt.ItemDataRole.UserRole)
        self.body_edit.setPlainText("본문 불러오는 중...")
        self.status.showMessage("기사 본문을 불러오는 중...")

        self.article_worker = ArticleWorker(url)
        self.article_worker.succeeded.connect(self.on_article_succeeded)
        self.article_worker.failed.connect(self.on_article_failed)
        self.article_worker.start()

    def on_article_succeeded(self, text):
        self.body_edit.setPlainText(text)
        self.status.showMessage("본문을 불러왔습니다.")

    def on_article_failed(self, message):
        self.body_edit.setPlainText(f"[본문 로딩 실패: {message}]")
        self.status.showMessage("본문 로딩 실패")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
