import webview

from app.core.daemon import get_running_services, get_stopped_services, start_service, stop_service


class Api:
    def get_running_services(self):
        return get_running_services()

    def get_stopped_services(self):
        return get_stopped_services()
    
    def start_service(self, service_name):
        return start_service(service_name)

    def stop_service(self, service_name):
        return stop_service(service_name)


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
