import win32service


def get_services():
    scm = win32service.OpenSCManager(
        None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE
    )
    raw = win32service.EnumServicesStatusEx(
        scm,
        win32service.SERVICE_WIN32,
        win32service.SERVICE_STATE_ALL,
    )
    win32service.CloseServiceHandle(scm)

    status_map = {
        1: "Stopped",
        2: "Start Pending",
        3: "Stop Pending",
        4: "Running",
        5: "Continue Pending",
        6: "Pause Pending",
        7: "Paused",
    }

    services = []
    for svc in raw:
        services.append({
            "name": svc["ServiceName"],
            "display_name": svc["DisplayName"],
            "status": status_map.get(svc["CurrentState"], "Unknown"),
        })

    services.sort(key=lambda s: s["name"].lower())
    return services
