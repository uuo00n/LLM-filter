#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Security Service 本地工具

用途：替代 intelligentPerception/zabbixDataFrom 的采集与联调脚本，支持：
- Zabbix API → 采集 → 生成 JSON 文件
- JSON 文件 → 调用 Security Service REST API
- 保存 Dify 分析结果到文件（服务侧同时落库）
- 查询历史接口并保存结果
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


async def collect_zabbix_json(output_dir: Path) -> Dict[str, Path]:
    from services.zabbix_service import ZabbixService

    _ensure_dir(output_dir)

    zabbix_service = ZabbixService()
    status = zabbix_service.get_sync_status()
    if not status.get("collector_initialized"):
        raise RuntimeError("Zabbix collector 未初始化，请检查 ZABBIX_URL / ZABBIX_USERNAME / ZABBIX_PASSWORD")

    print("=" * 70)
    print("阶段1：Zabbix 数据采集 → 生成 JSON 文件")
    print("=" * 70)

    device_data = await zabbix_service.collect_device_data()
    cpu_data = await zabbix_service.collect_cpu_data()
    network_data = await zabbix_service.collect_network_data()

    analysis_input = {"devices": device_data.get("devices", [])}

    attack_target = "unknown"
    attack_logs = ""
    devices = device_data.get("devices", [])
    if devices:
        picked = next((d for d in devices if d.get("logs")), devices[0])
        attack_target = picked.get("name") or "unknown"
        logs = picked.get("logs") or []
        attack_logs = "\n".join(str(x) for x in logs[:10])

    attack_advice_input = {
        "attack_type": "Suspicious Activity",
        "target_device": attack_target,
        "severity": "high",
        "logs": attack_logs,
    }

    paths = {
        "zabbix_devices.json": output_dir / "zabbix_devices.json",
        "zabbix_cpu.json": output_dir / "zabbix_cpu.json",
        "zabbix_network.json": output_dir / "zabbix_network.json",
        "analysis_input.json": output_dir / "analysis_input.json",
        "attack_advice_input.json": output_dir / "attack_advice_input.json",
    }

    _write_json(paths["zabbix_devices.json"], device_data)
    _write_json(paths["zabbix_cpu.json"], cpu_data)
    _write_json(paths["zabbix_network.json"], network_data)
    _write_json(paths["analysis_input.json"], analysis_input)
    _write_json(paths["attack_advice_input.json"], attack_advice_input)

    print(f"✅ 已生成: {paths['analysis_input.json']}")
    print(f"✅ 已生成: {paths['attack_advice_input.json']}")
    print(f"✅ 设备数量: {len(analysis_input['devices'])}")

    return paths


def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


async def call_security_service_api(base_url: str, token: str, input_dir: Path, output_dir: Path) -> Dict[str, Path]:
    _ensure_dir(output_dir)

    print("\n" + "=" * 70)
    print("阶段2：JSON 文件 → Security Service REST API → 保存结果")
    print("=" * 70)

    analysis_input = _read_json(input_dir / "analysis_input.json")
    attack_input = _read_json(input_dir / "attack_advice_input.json")

    endpoints = {
        "analysis": f"{base_url.rstrip('/')}/api/v1/security/analysis",
        "attack_advice": f"{base_url.rstrip('/')}/api/v1/security/attack-advice",
        "monitor": f"{base_url.rstrip('/')}/api/v1/security/monitor",
        "report": f"{base_url.rstrip('/')}/api/v1/security/report",
        "analysis_history": f"{base_url.rstrip('/')}/api/v1/security/analysis/history?limit=20",
        "attack_history": f"{base_url.rstrip('/')}/api/v1/security/attack-advice/history?limit=20",
    }

    out_paths = {
        "analysis_result.json": output_dir / "analysis_result.json",
        "attack_advice_result.json": output_dir / "attack_advice_result.json",
        "monitor_result.json": output_dir / "monitor_result.json",
        "report_result.json": output_dir / "report_result.json",
        "analysis_history.json": output_dir / "analysis_history.json",
        "attack_advice_history.json": output_dir / "attack_advice_history.json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        r1 = await client.post(endpoints["analysis"], headers=_auth_headers(token), json=analysis_input)
        r1.raise_for_status()
        analysis_res = r1.json()
        _write_json(out_paths["analysis_result.json"], analysis_res)
        print(f"✅ /analysis 完成，risk_level={analysis_res.get('risk_level')}")

        r2 = await client.post(endpoints["attack_advice"], headers=_auth_headers(token), json=attack_input)
        r2.raise_for_status()
        attack_res = r2.json()
        _write_json(out_paths["attack_advice_result.json"], attack_res)
        print(f"✅ /attack-advice 完成，immediate_actions={len(attack_res.get('immediate_actions', []))}")

        r3 = await client.get(endpoints["monitor"], headers=_auth_headers(token))
        r3.raise_for_status()
        monitor_res = r3.json()
        _write_json(out_paths["monitor_result.json"], monitor_res)
        print(f"✅ /monitor 完成，detected={len(monitor_res.get('detected_vulnerabilities', []))}")

        r4 = await client.get(endpoints["report"], headers=_auth_headers(token))
        r4.raise_for_status()
        report_res = r4.json()
        _write_json(out_paths["report_result.json"], report_res)
        print(f"✅ /report 完成，date={report_res.get('date')}")

        r5 = await client.get(endpoints["analysis_history"], headers=_auth_headers(token))
        r5.raise_for_status()
        _write_json(out_paths["analysis_history.json"], r5.json())
        print("✅ /analysis/history 完成")

        r6 = await client.get(endpoints["attack_history"], headers=_auth_headers(token))
        r6.raise_for_status()
        _write_json(out_paths["attack_advice_history.json"], r6.json())
        print("✅ /attack-advice/history 完成")

    return out_paths


async def internal_smoke_test() -> bool:
    print("=" * 70)
    print("阶段0：内部冒烟（不经 REST，仅验证类可用）")
    print("=" * 70)

    try:
        from services.zabbix_service import ZabbixService
        from services.analysis import SecurityService
        from schemas.payloads import DeviceInfo

        zabbix_service = ZabbixService()
        status = zabbix_service.get_sync_status()
        print(f"Zabbix collector: {'✅ 已初始化' if status.get('collector_initialized') else '❌ 未初始化'}")

        security_service = SecurityService(zabbix_service=zabbix_service)
        res = await security_service.analyze_risks(
            [
                DeviceInfo(
                    id="smoke-1",
                    name="Smoke-Device",
                    type="server",
                    status="up",
                    logs=["CPU high", "Multiple failed login attempts"],
                )
            ]
        )
        print(f"Security analyze_risks: ✅ 返回 risk_level={res.risk_level}")
        return True
    except Exception as e:
        print(f"❌ 内部冒烟失败: {e}")
        return False


def _env_or_arg(value: Optional[str], env_key: str) -> Optional[str]:
    return value if value else os.getenv(env_key)


async def main() -> int:
    parser = argparse.ArgumentParser(prog="test_refactor.py")
    sub = parser.add_subparsers(dest="cmd", required=False)

    p_collect = sub.add_parser("collect", help="采集Zabbix并生成JSON文件")
    p_collect.add_argument("--out", default=".\\out", help="输出目录")

    p_call = sub.add_parser("call-api", help="读取JSON并调用Security Service REST API")
    p_call.add_argument("--base-url", default=None, help="服务地址，例如 http://localhost:8003 或 http://localhost:8080")
    p_call.add_argument("--token", default=None, help="管理员JWT，或使用环境变量 ADMIN_TOKEN")
    p_call.add_argument("--in", dest="in_dir", default=".\\out", help="输入目录（包含 analysis_input.json 等）")
    p_call.add_argument("--out", dest="out_dir", default=".\\out", help="输出目录")

    p_all = sub.add_parser("run-all", help="采集→生成JSON→调用REST→保存结果→查询历史")
    p_all.add_argument("--base-url", default=None, help="服务地址，例如 http://localhost:8003 或 http://localhost:8080")
    p_all.add_argument("--token", default=None, help="管理员JWT，或使用环境变量 ADMIN_TOKEN")
    p_all.add_argument("--out", default=".\\out", help="输出目录")

    sub.add_parser("smoke", help="内部冒烟测试")

    args = parser.parse_args()

    print("Security Service 一体化工具")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.cmd in (None, "smoke"):
        ok = await internal_smoke_test()
        return 0 if ok else 1

    if args.cmd == "collect":
        out_dir = Path(args.out).resolve()
        await collect_zabbix_json(out_dir)
        return 0

    if args.cmd == "call-api":
        base_url = _env_or_arg(args.base_url, "SECURITY_SERVICE_URL") or "http://localhost:8003"
        token = _env_or_arg(args.token, "ADMIN_TOKEN")
        if not token:
            raise RuntimeError("缺少管理员JWT：请传 --token 或设置环境变量 ADMIN_TOKEN")
        in_dir = Path(args.in_dir).resolve()
        out_dir = Path(args.out_dir).resolve()
        await call_security_service_api(base_url, token, in_dir, out_dir)
        return 0

    if args.cmd == "run-all":
        base_url = _env_or_arg(args.base_url, "SECURITY_SERVICE_URL") or "http://localhost:8003"
        token = _env_or_arg(args.token, "ADMIN_TOKEN")
        if not token:
            raise RuntimeError("缺少管理员JWT：请传 --token 或设置环境变量 ADMIN_TOKEN")
        out_dir = Path(args.out).resolve()
        await collect_zabbix_json(out_dir)
        await call_security_service_api(base_url, token, out_dir, out_dir)
        return 0

    raise RuntimeError(f"未知命令: {args.cmd}")


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        sys.exit(130)
