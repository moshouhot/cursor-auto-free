import os
import json
import uuid
import secrets
import platform
from pathlib import Path
from datetime import datetime
import shutil

def get_config_path():
    """获取storage.json的路径"""
    system = platform.system()
    home = str(Path.home())
    
    if system == "Darwin":  # MacOS
        return os.path.join(home, "Library", "Application Support", "Cursor", "User", "globalStorage", "storage.json")
    elif system == "Windows":
        app_data = os.getenv('APPDATA')
        return os.path.join(app_data, "Cursor", "User", "globalStorage", "storage.json")
    elif system == "Linux":
        return os.path.join(home, ".config", "Cursor", "User", "globalStorage", "storage.json")
    else:
        raise OSError(f"不支持的操作系统: {system}")

def get_machine_id_path():
    """获取machineid文件的路径"""
    system = platform.system()
    home = str(Path.home())
    
    if system == "Darwin":  # MacOS
        return os.path.join(home, "Library", "Application Support", "Cursor", "machineid")
    elif system == "Windows":
        app_data = os.getenv('APPDATA')
        return os.path.join(app_data, "Cursor", "machineid")
    elif system == "Linux":
        return os.path.join(home, ".config", "Cursor", "machineid")
    else:
        raise OSError(f"不支持的操作系统: {system}")

def generate_machine_id():
    """生成64位小写十六进制字符串"""
    return secrets.token_hex(32)

def generate_dev_device_id():
    """生成UUID字符串"""
    return str(uuid.uuid4())

def backup_file(file_path):
    """创建配置文件的备份"""
    try:
        if os.path.exists(file_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.backup_{timestamp}"
            shutil.copy2(file_path, backup_path)
            return backup_path
        return None
    except Exception as e:
        raise Exception(f"创建备份失败: {str(e)}")

def reset_cursor_ids():
    """重置Cursor ID"""
    try:
        config_path = get_config_path()
        machine_id_path = get_machine_id_path()
        
        # 检查配置文件
        if not os.path.exists(config_path):
            print(f"配置文件未找到: {config_path}")
            return False
            
        # 备份配置文件
        print("正在创建配置文件备份...")
        config_backup_path = backup_file(config_path)
        if config_backup_path:
            print(f"配置文件备份已创建: {config_backup_path}")
        
        # 如果存在machine id文件，则创建备份
        if os.path.exists(machine_id_path):
            print("正在创建Machine ID文件备份...")
            machine_id_backup_path = backup_file(machine_id_path)
            if machine_id_backup_path:
                print(f"Machine ID文件备份已创建: {machine_id_backup_path}")
        
        # 生成新的ID
        new_machine_id = generate_machine_id()
        new_mac_machine_id = generate_machine_id()
        new_dev_device_id = generate_dev_device_id()
        
        # 更新配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config["telemetry.macMachineId"] = new_mac_machine_id
        config["telemetry.machineId"] = new_machine_id
        config["telemetry.devDeviceId"] = new_dev_device_id
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        # 更新machine id文件
        with open(machine_id_path, 'w') as f:
            f.write(new_machine_id)
        
        print("\n重置成功！新的ID信息：")
        print(f"New Machine ID: {new_machine_id}")
        print(f"New Mac Machine ID: {new_mac_machine_id}")
        print(f"New Device ID: {new_dev_device_id}")
        
        return True
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        return False 