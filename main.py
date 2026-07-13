import webview

def main():
    window = webview.create_window(
        "Wintools",
        url="app/ui/home.html",
        width=600,
        height=500,
        resizable=True,
        min_size=(400, 350),
    )
    webview.start()


if __name__ == "__main__":
    main()
