import win32service

"""
A little bit of theory won't kill.
Service and Daemon are the same things.
They both run in background but the main diff is in the manager, the OS, and the naming convention.
Service use services.msc and linux use systemctl
It is harder to use manage service on windows. That's why this backend is here.
"""

def get_running_services():
    # SCM = Service Control Manager: central database that manages all services.
    # OpenSCManager usually takes three params (machine name, database name, persmission level)
    # The default if we put None for both are (local computer, SCM database, ...)
    # Later I want to give full access so I may need to refactor this win32Service so I can
    # use the SC_MANAGER_ALL_ACCESS.
    scm = win32service.OpenSCManager(
        None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE
    )
    
    # Main service query.
    raw = win32service.EnumServicesStatusEx(
        scm,
        win32service.SERVICE_WIN32,
        win32service.SERVICE_ACTIVE,
    )

    win32service.CloseServiceHandle(scm)

    # Those constant can be got from the winsvc.h header of a Windows API
    # constants. They basically match the hexadecimal value.
    # types_map ={
    #     16: "Own Process", #0x10
    #     32: "Shared Process", #0x20
    #     1: "Kernel Driver", #0x1
    #     2: "FS Driver" #0x2
    # }
    # I was thinking of not showing Kernel related daemon but whatever... for now let's put everything.
    # FYI: they are multiple of 2 to easily do bitwise operation on multiple service types?
    # Need to check a clear documentatino of this code for later
    # For a better approach, I'll use pywin32's built-in constant
    types_map = {
        win32service.SERVICE_WIN32_OWN_PROCESS: "Own Process",
        win32service.SERVICE_WIN32_SHARE_PROCESS: "Share Process",
        win32service.SERVICE_KERNEL_DRIVER: "Kernel Driver",
        # Showing kernel driver service is useless, since we cannot interact with it because it load and unload with the full system
        win32service.SERVICE_FILE_SYSTEM_DRIVER: "File System Driver"
    }

    services = []
    for svc in raw:
        services.append({
            "name": svc["ServiceName"],
            "display_name": svc["DisplayName"],
            "status": "Running", # we need this since the frontend needs it.
            "service_type": types_map.get(svc["ServiceType"], "Other")
        })

    services.sort(key=lambda service: service["name"].lower())
    return services
