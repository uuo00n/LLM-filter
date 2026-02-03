import asyncio
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class ZabbixDataCollector:
    def __init__(self, zabbix_url: str, username: str, password: str):
        """
        初始化 Zabbix 数据采集器
        :param zabbix_url: Zabbix 服务器基础 URL，例如 "http://192.168.20.199"
        :param username: 用户名
        :param password: 密码
        """
        self.zabbix_url = zabbix_url.rstrip('/')
        self.username = username
        self.password = password
        self.auth_token = None
        self.login()

    def _get_api_url(self):
        """返回完整的 API 地址"""
        if self.zabbix_url.endswith("api_jsonrpc.php"):
            return self.zabbix_url
        if self.zabbix_url.endswith("/zabbix"):
            return f"{self.zabbix_url}/api_jsonrpc.php"
        return f"{self.zabbix_url}/zabbix/api_jsonrpc.php"

    def login(self):
        """智能登录：自动尝试新旧参数格式"""
        # 尝试顺序：先新版 (username)，再旧版 (user)
        payloads = [
            {
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {"username": self.username, "password": self.password},
                "id": 1
            },
            {
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {"user": self.username, "password": self.password},
                "id": 1
            }
        ]

        for i, payload in enumerate(payloads):
            try:
                logger.info(f"尝试登录方式 {'新版 (username)' if i == 0 else '旧版 (user)'}...")
                response = requests.post(
                    self._get_api_url(),
                    json=payload,
                    timeout=10,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code}: {response.reason}")
                    continue

                data = response.json()
                if "result" in data:
                    self.auth_token = data["result"]
                    version = "Zabbix 5.4+" if i == 0 else "Zabbix 5.2-"
                    logger.info(f"登录成功！检测到 {version} 格式。")
                    return
                elif "error" in data:
                    err = data["error"]
                    msg = f"[{err.get('code')}] {err.get('message')} - {err.get('data', '')}"
                    logger.warning(f"登录失败: {msg}")
                    if "unexpected parameter" in msg and ("username" in msg or "user" in msg):
                        continue  # 尝试下一个
                    else:
                        raise Exception(msg)
                else:
                    logger.warning("未知响应格式: {data}")
                    continue

            except requests.exceptions.RequestException as e:
                logger.error(f"网络错误: {e}")
                continue
            except json.JSONDecodeError:
                logger.warning("非 JSON 响应: {response.text[:200]}")
                continue

        raise Exception("所有登录方式均失败！请检查：\n1. Zabbix 地址是否正确\n2. 用户名/密码是否正确\n3. Zabbix 是否运行\n4. 是否允许 API 访问")

    def _call_api(self, method: str, params: dict):
        """通用 API 调用"""
        return self._call_api_with_retry(method, params, retry_count=1)

    def _call_api_with_retry(self, method: str, params: dict, retry_count: int = 0):
        """带重试机制的 API 调用"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "auth": self.auth_token,
            "id": 1
        }
        try:
            response = requests.post(
                self._get_api_url(),
                json=payload,
                timeout=15,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                err = data["error"]
                error_msg = err.get('message', '')
                error_data = err.get('data', '')
                
                # 检查是否是认证相关错误
                # Zabbix API 错误码: -32602 (Invalid params) 有时也用于 session 失效
                # 常见 Session 错误信息: "Session terminated", "Not authorized"
                if retry_count > 0 and ("Session" in error_data or "authorized" in error_data or "auth" in error_msg.lower()):
                    logger.warning(f"Zabbix API 认证失败 ({error_msg} - {error_data})，尝试重新登录...")
                    self.login()
                    # 更新 auth token 后重试
                    return self._call_api_with_retry(method, params, retry_count=retry_count - 1)
                
                raise Exception(f"[{err.get('code')}] {error_msg} - {error_data}")
            return data["result"]
        except Exception as e:
            raise Exception(f"API 调用失败 ({method}): {e}")

    def get_hosts(self):
        """获取主机列表"""
        return self._call_api("host.get", {
            "output": ["hostid", "name", "status"],
            "selectTags": ["tag", "value"]
        })

    def get_triggers(self):
        """获取活动触发器"""
        return self._call_api("trigger.get", {
            "output": ["triggerid", "description", "priority", "status"],
            "selectHosts": ["hostid", "name"],
            "filter": {"value": 1},
            "sortfield": "priority",
            "sortorder": "DESC"
        })

    def get_events(self, time_from: Optional[int] = None, time_till: Optional[int] = None, limit: int = 100):
        """获取事件"""
        params = {
            "output": ["eventid", "clock", "name", "severity"],
            "selectHosts": ["hostid", "name"],
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": limit
        }
        if time_from is not None:
            params["time_from"] = time_from
        if time_till is not None:
            params["time_till"] = time_till
        return self._call_api("event.get", params)

    def get_cpu_data(self):
        """获取CPU和硬件数据"""
        logger.info("获取CPU和硬件数据...")
        
        # 获取主机
        hosts = self.get_hosts()
        logger.info(f"获取到 {len(hosts)} 台主机")

        # 获取触发器
        triggers = self.get_triggers()
        logger.info(f"获取到 {len(triggers)} 个活动触发器")

        # 获取最近24小时事件
        time_from = int((datetime.now() - timedelta(hours=24)).timestamp())
        events = self.get_events(time_from=time_from, limit=200)
        logger.info(f"获取到 {len(events)} 条事件")

        # 构建CPU数据结构
        cpu_data = []
        for host in hosts:
            host_data = {
                "id": host["hostid"],
                "name": host["name"],
                "type": self._determine_device_type(host),
                "status": "up" if host["status"] == "0" else "down",
                "cpu_usage": self._get_mock_cpu_usage(),  # 实际项目中应该从items获取
                "memory_usage": self._get_mock_memory_usage(),
                "disk_usage": self._get_mock_disk_usage(),
                "logs": []
            }

            # 关联触发器日志
            for t in triggers:
                if any(h["hostid"] == host["hostid"] for h in t.get("hosts", [])):
                    host_data["logs"].append(f"{t['description']} - Priority: {t['priority']}")

            # 关联事件日志
            for e in events:
                if any(h["hostid"] == host["hostid"] for h in e.get("hosts", [])):
                    ts = datetime.fromtimestamp(int(e["clock"])).strftime("%Y-%m-%d %H:%M:%S")
                    host_data["logs"].append(f"{ts} - {e['name']} - Severity: {e['severity']}")

            cpu_data.append(host_data)

        return {"hosts": cpu_data}

    def get_network_data(self):
        """获取网络接口数据"""
        logger.info("获取网络接口数据...")
        
        # 获取主机
        hosts = self.get_hosts()
        logger.info(f"获取到 {len(hosts)} 台主机")

        # 获取触发器
        triggers = self.get_triggers()
        logger.info(f"获取到 {len(triggers)} 个活动触发器")

        # 获取最近24小时事件
        time_from = int((datetime.now() - timedelta(hours=24)).timestamp())
        events = self.get_events(time_from=time_from, limit=200)
        logger.info(f"获取到 {len(events)} 条事件")

        # 构建网络数据结构
        network_data = []
        for host in hosts:
            host_data = {
                "id": host["hostid"],
                "name": host["name"],
                "type": self._determine_device_type(host),
                "status": "up" if host["status"] == "0" else "down",
                "interfaces": self._get_mock_network_interfaces(),
                "logs": []
            }

            # 关联触发器日志
            for t in triggers:
                if any(h["hostid"] == host["hostid"] for h in t.get("hosts", [])):
                    host_data["logs"].append(f"{t['description']} - Priority: {t['priority']}")

            # 关联事件日志
            for e in events:
                if any(h["hostid"] == host["hostid"] for h in e.get("hosts", [])):
                    ts = datetime.fromtimestamp(int(e["clock"])).strftime("%Y-%m-%d %H:%M:%S")
                    host_data["logs"].append(f"{ts} - {e['name']} - Severity: {e['severity']}")

            network_data.append(host_data)

        return {"hosts": network_data}

    def get_security_data_for_analysis(self):
        """获取安全分析数据"""
        logger.info("获取安全分析数据...")
        
        # 获取主机
        hosts = self.get_hosts()
        logger.info(f"获取到 {len(hosts)} 台主机")

        # 获取活动触发器
        triggers = self.get_triggers()
        logger.info(f"获取到 {len(triggers)} 个活动触发器")

        # 获取最近24小时事件
        time_from = int((datetime.now() - timedelta(hours=24)).timestamp())
        events = self.get_events(time_from=time_from, limit=200)
        logger.info(f"获取到 {len(events)} 条事件")

        devices = []
        for host in hosts:
            device = {
                "id": host["hostid"],
                "name": host["name"],
                "type": self._determine_device_type(host),
                "status": "up" if host["status"] == "0" else "down",
                "logs": []
            }

            # 关联触发器
            for t in triggers:
                if any(h["hostid"] == host["hostid"] for h in t.get("hosts", [])):
                    device["logs"].append(f"{t['description']} - Priority: {t['priority']}")

            # 关联事件
            for e in events:
                if any(h["hostid"] == host["hostid"] for h in e.get("hosts", [])):
                    ts = datetime.fromtimestamp(int(e["clock"])).strftime("%Y-%m-%d %H:%M:%S")
                    device["logs"].append(f"{ts} - {e['name']} - Severity: {e['severity']}")

            devices.append(device)

        return {"devices": devices}

    def _determine_device_type(self, host):
        """智能识别设备类型"""
        tags = host.get("tags", [])
        for tag in tags:
            if tag["tag"] == "device_type":
                return tag["value"]
        
        name = host["name"].lower()
        if any(kw in name for kw in ["sw", "switch"]):
            return "switch"
        elif any(kw in name for kw in ["fw", "firewall"]):
            return "firewall"
        elif any(kw in name for kw in ["server", "web", "db", "srv"]):
            return "server"
        else:
            return "unknown"

    def _get_mock_cpu_usage(self):
        """模拟CPU使用率数据"""
        return {
            "usage": 45.2,  # 模拟使用率
            "cores": 4,     # 模拟核心数
            "load_average": [1.2, 1.1, 0.8]  # 模拟负载
        }

    def _get_mock_memory_usage(self):
        """模拟内存使用数据"""
        return {
            "total": 16384,  # MB
            "used": 8192,    # MB
            "free": 8192,    # MB
            "usage_percent": 50.0
        }

    def _get_mock_disk_usage(self):
        """模拟磁盘使用数据"""
        return [
            {
                "mount": "/",
                "total": 500000,  # MB
                "used": 250000,  # MB
                "free": 250000,  # MB
                "usage_percent": 50.0
            },
            {
                "mount": "/var",
                "total": 100000,  # MB
                "used": 60000,   # MB
                "free": 40000,   # MB
                "usage_percent": 60.0
            }
        ]

    def _get_mock_network_interfaces(self):
        """模拟网络接口数据"""
        return [
            {
                "name": "eth0",
                "ip_address": "192.168.1.100",
                "mac_address": "00:0C:29:12:34:56",
                "status": "up",
                "speed": "1000Mbps",
                "rx_bytes": 1234567890,
                "tx_bytes": 987654321,
                "errors": {"rx": 0, "tx": 0}
            },
            {
                "name": "eth1",
                "ip_address": "192.168.2.100",
                "mac_address": "00:0C:29:12:34:57",
                "status": "up",
                "speed": "1000Mbps",
                "rx_bytes": 2345678901,
                "tx_bytes": 1876543210,
                "errors": {"rx": 1, "tx": 0}
            }
        ]

class ZabbixService:
    def __init__(self):
        """初始化Zabbix服务"""
        self.collector = None
        self.last_sync_time = None
        self._initialize_collector()

    async def _run_blocking(self, func, *args, **kwargs):
        try:
            to_thread = asyncio.to_thread
        except AttributeError:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
        return await to_thread(func, *args, **kwargs)

    def _initialize_collector(self):
        """初始化数据采集器"""
        try:
            self.collector = ZabbixDataCollector(
                zabbix_url=settings.ZABBIX_URL,
                username=settings.ZABBIX_USERNAME,
                password=settings.ZABBIX_PASSWORD
            )
            logger.info("Zabbix服务初始化成功")
        except Exception as e:
            logger.error(f"Zabbix服务初始化失败: {e}")
            self.collector = None

    async def collect_device_data(self):
        """采集设备数据"""
        if not self.collector:
            raise Exception("Zabbix collector未初始化，请检查Zabbix配置")

        return await self._run_blocking(self.collector.get_security_data_for_analysis)

    async def collect_cpu_data(self):
        """采集CPU和硬件数据"""
        if not self.collector:
            raise Exception("Zabbix collector未初始化，请检查Zabbix配置")

        return await self._run_blocking(self.collector.get_cpu_data)

    async def collect_network_data(self):
        """采集网络接口数据"""
        if not self.collector:
            raise Exception("Zabbix collector未初始化，请检查Zabbix配置")

        return await self._run_blocking(self.collector.get_network_data)

    async def sync_data(self):
        """同步数据"""
        try:
            logger.info("开始同步Zabbix数据...")
            
            # 并发采集不同类型的数据
            device_task = self.collect_device_data()
            cpu_task = self.collect_cpu_data()
            network_task = self.collect_network_data()
            
            # 等待所有任务完成
            device_data, cpu_data, network_data = await asyncio.gather(
                device_task, cpu_task, network_task
            )
            
            self.last_sync_time = datetime.now()
            
            logger.info("Zabbix数据同步完成")
            return {
                "devices": len(device_data.get("devices", [])),
                "hosts_cpu": len(cpu_data.get("hosts", [])),
                "hosts_network": len(network_data.get("hosts", [])),
                "sync_time": self.last_sync_time.isoformat()
            }
        except Exception as e:
            logger.error(f"Zabbix数据同步失败: {e}")
            raise Exception(f"数据同步失败: {e}")

    def get_sync_status(self):
        """获取同步状态"""
        return {
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "collector_initialized": self.collector is not None
        }
