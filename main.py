import webview

from app.core.daemon import get_running_services


class Api:
    def get_services(self):
        return get_running_services()


def main():
    api = Api()
    window = webview.create_window(
        "Wintools",
        url="app/ui/home.html",
        width=600,
        height=500,
        resizable=True,
        min_size=(400, 350),
        js_api=api,
    )
    webview.start()


if __name__ == "__main__":
    main()
