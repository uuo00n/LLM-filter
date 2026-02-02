#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Service 重构测试脚本
测试新的Zabbix集成功能
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_zabbix_service():
    """测试Zabbix服务"""
    print("="*70)
    print("测试 Zabbix Service")
    print("="*70)
    
    try:
        from services.zabbix_service import ZabbixService
        
        # 创建Zabbix服务实例
        zabbix_service = ZabbixService()
        
        # 测试获取同步状态
        print("1. 检查Zabbix服务状态...")
        status = zabbix_service.get_sync_status()
        print(f"   初始化状态: {'✅ 成功' if status['collector_initialized'] else '❌ 失败'}")
        print(f"   最后同步时间: {status['last_sync_time']}")
        
        # 测试同步数据
        print("\n2. 测试Zabbix数据同步...")
        sync_result = await zabbix_service.sync_data()
        print(f"   同步状态: ✅ 成功")
        print(f"   同步结果: {json.dumps(sync_result, indent=2, ensure_ascii=False)}")
        
        # 测试获取设备数据
        print("\n3. 测试获取设备数据...")
        device_data = await zabbix_service.collect_device_data()
        devices = device_data.get("devices", [])
        print(f"   设备数量: {len(devices)}")
        
        # 显示前3个设备
        for i, device in enumerate(devices[:3]):
            print(f"   设备 {i+1}: {device['name']} ({device['type']}) - {device['status']}")
            print(f"      日志数量: {len(device['logs'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Zabbix Service测试失败: {e}")
        return False

async def test_security_service():
    """测试安全服务"""
    print("\n" + "="*70)
    print("测试 Security Service")
    print("="*70)
    
    try:
        from services.zabbix_service import ZabbixService
        from services.analysis import SecurityService
        
        # 创建服务实例
        zabbix_service = ZabbixService()
        security_service = SecurityService(zabbix_service=zabbix_service)
        
        # 测试风险分析
        print("1. 测试风险分析功能...")
        analysis_result = await security_service.analyze_risks()
        print(f"   分析状态: ✅ 成功")
        print(f"   风险级别: {analysis_result.risk_level}")
        print(f"   漏洞数量: {len(analysis_result.vulnerabilities)}")
        print(f"   建议数量: {len(analysis_result.suggestions)}")
        
        # 测试监控功能
        print("\n2. 测试风险监控功能...")
        monitor_result = await security_service.monitor_risks()
        print(f"   监控状态: ✅ 成功")
        print(f"   检测漏洞: {len(monitor_result.detected_vulnerabilities)}")
        print(f"   合规风险: {len(monitor_result.compliance_risks)}")
        
        # 测试报告生成
        print("\n3. 测试报告生成功能...")
        report_result = await security_service.generate_report()
        print(f"   报告状态: ✅ 成功")
        print(f"   报告日期: {report_result.date}")
        print(f"   整体状态: {report_result.overall_status}")
        
        # 测试攻击建议
        print("\n4. 测试攻击建议功能...")
        advice_result = await security_service.get_attack_advice(
            attack_type="Port Scan",
            target="Web Server",
            logs="Port scan detected from external IP"
        )
        print(f"   建议状态: ✅ 成功")
        print(f"   即时行动: {len(advice_result.immediate_actions)}")
        print(f"   分析结果: {advice_result.analysis[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Security Service测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("Security Service 重构验证测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("此脚本测试新的Zabbix集成功能...")
    
    # 测试结果
    results = {
        "zabbix_service": False,
        "security_service": False,
        "overall": False
    }
    
    # 测试Zabbix服务
    results["zabbix_service"] = await test_zabbix_service()
    
    # 测试安全服务
    results["security_service"] = await test_security_service()
    
    # 总体结果
    results["overall"] = results["zabbix_service"] and results["security_service"]
    
    # 输出测试总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    print(f"Zabbix Service: {'✅ 通过' if results['zabbix_service'] else '❌ 失败'}")
    print(f"Security Service: {'✅ 通过' if results['security_service'] else '❌ 失败'}")
    print(f"总体结果: {'✅ 全部通过' if results['overall'] else '❌ 有失败项'}")
    
    if results['overall']:
        print("\n🎉 重构成功！所有功能正常工作。")
        print("现在可以使用以下API端点:")
        print("  POST /api/v1/security/zabbix/sync      - 手动同步Zabbix数据")
        print("  GET  /api/v1/security/zabbix/status    - 获取Zabbix服务状态")
        print("  POST /api/v1/security/zabbix/devices    - 获取设备列表")
        print("  POST /api/v1/security/analysis          - 安全分析")
        print("  GET  /api/v1/security/monitor          - 风险监控")
        print("  GET  /api/v1/security/report            - 生成报告")
    else:
        print("\n⚠️ 测试失败，请检查:")
        print("  1. Zabbix服务器配置")
        print("  2. 环境变量设置")
        print("  3. 网络连接")
        print("  4. 依赖安装")
    
    return results["overall"]

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    sys.exit(0 if success else 1)