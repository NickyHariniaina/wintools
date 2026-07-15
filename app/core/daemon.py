import win32service
import win32serviceutil
import time

"""
A little bit of theory won't kill.
Service and Daemon are the same things.
They both run in background but the main diff is in the manager, the OS, and the naming convention.
Service use services.msc and linux use systemctl
It is harder to use manage service on windows. That's why this backend is here.
"""

TIMEOUT_IN_SECOND=50

STATUS_MAP = {
    1: "Stopped",
    2: "Start Pending",
    3: "Stop Pending",
    4: "Running",
    5: "Continue Pending",
    6: "Pause Pending",
    7: "Paused",
}

TYPES_MAP = {
    win32service.SERVICE_WIN32_OWN_PROCESS: "Own Process",
    win32service.SERVICE_WIN32_SHARE_PROCESS: "Share Process",
    win32service.SERVICE_KERNEL_DRIVER: "Kernel Driver",
    win32service.SERVICE_FILE_SYSTEM_DRIVER: "File System Driver"
}

def open_SCM_with_enumerate_service():
    return win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)

def query(scm, service_type, service_status):
    return win32service.EnumServicesStatusEx(scm, service_type, service_status)

def get_stopped_services():
    scm = open_SCM_with_enumerate_service()
    raw = query(scm, win32service.SERVICE_WIN32, win32service.SERVICE_STATE_ALL)
    win32service.CloseServiceHandle(scm)

    services = []
    for svc in raw:
        if svc["CurrentState"] != win32service.SERVICE_STOPPED:
            continue
        services.append({
            "name": svc["ServiceName"],
            "display_name": svc["DisplayName"],
            "service_type": TYPES_MAP.get(svc["ServiceType"], "Other"),
            "status": STATUS_MAP.get(svc["CurrentState"], "Unknown")
        })

    services.sort(key=lambda service: service["name"].lower())
    return services

def get_running_services():
    # SCM = Service Control Manager: central database that manages all services.
    # OpenSCManager usually takes three params (machine name, database name, persmission level)
    # The default if we put None for both are (local computer, SCM database, ...)
    # Later I want to give full access so I may need to refactor this win32Service so I can
    # use the SC_MANAGER_ALL_ACCESS. *DONE

    scm = open_SCM_with_enumerate_service()
    
    raw = query(scm, win32service.SERVICE_WIN32, win32service.SERVICE_ACTIVE)

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

    services = []
    for svc in raw:
        print(svc)
        services.append({
            "name": svc["ServiceName"],
            "display_name": svc["DisplayName"],
            "service_type": TYPES_MAP.get(svc["ServiceType"], "Other"),
            "status": STATUS_MAP.get(svc["CurrentState"], "Unknown")
        })

    services.sort(key=lambda service: service["name"].lower())
    return services

def start_service(service_name, machine=None, wait=True):
    try:
        status = win32serviceutil.QueryServiceStatus(service_name, machine)
        if status[1] == win32service.SERVICE_RUNNING:
            return {"success": True, "message": f"'{service_name}' is already running"}
        
        win32serviceutil.StartService(service_name, machine)
        
        if wait:
            start_time = time.time()
            while time.time() - start_time < TIMEOUT_IN_SECOND:
                status = win32serviceutil.QueryServiceStatus(service_name, machine)
                if status[1] == win32service.SERVICE_RUNNING:
                    return {"success": True, "message": f"'{service_name}' is already running"}
                time.sleep(1)
                return {"success": False, "message": "Timeout reached for starting service"}
        
        return {"success": True, "message": f"'{service_name}' start requested"}
        
    except Exception as e:
        return {"success": False, "message": str(e)}

# The only main diff between stop and start service is the StopService
# function calling. Is there a better way to refactor it?
def stop_service(service_name, machine=None, wait=True):
    try:
        status = win32serviceutil.QueryServiceStatus(service_name, machine)
        if status[1] == win32service.SERVICE_STOPPED:
            return {"success": True, "message": f"'{service_name}' is already stopped"}

        win32serviceutil.StopService(service_name, machine)

        if wait:
            start_time = time.time()
            while time.time() - start_time < TIMEOUT_IN_SECOND:
                status = win32serviceutil.QueryServiceStatus(service_name, machine)
                if status[1] == win32service.SERVICE_STOPPED:
                    return {"success": True, "message": f"'{service_name}' stopped"}
                time.sleep(1)
            return {"success": False, "message": "Timeout reached for stopping service"}

        return {"success": True, "message": f"'{service_name}' stop requested"}

    except Exception as e:
        return {"success": False, "message": str(e)}