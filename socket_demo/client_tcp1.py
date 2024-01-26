#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/11/20 19:46
# @Author  : GuQingJun
# @Site    :
# @File    : client_tcp1.py
# @Software: PyCharm

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/4/26 16:31
# @Author  : GuQingJun
# @Site    :
# @File    : client_tcp.py
# @Software: PyCharm
import random
import re
import socket
import threading
import time, datetime
from queue import Queue
from threading import Thread
import logging

# 任务配置项
task_code = "XS240125909"
task_patrol_id = f"""{task_code}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}"""
# task_patrol_id = "XS231108681_20231108191844"
task_name = "泽宇高科任务终止数据不全2024-01-25 16:14:14"
s_code = "robot001"
r_code = "patrol_host"
nest_code = "Nest01"
robot_code = "Robot01"
robot_name = "模拟机器人"
device_id = ["9530_00_01", "9530_00_02", "9530_01_01", "9530_00_04", "9530_01_02", "9540_00_01", "9540_00_02",
             "9540_00_03"]
# device_id = ["9530_00_01", "00_01_02"]
device_name = ["模拟机器人Ⅱ区RP_003组合电器本体本体外观", "模拟机器人Ⅱ区RP_003组合电器本体SF6密度压力表",
               "模拟机器人Ⅱ区RP_003组合电器套管B相套管外观", "模拟机器人Ⅱ区RP_003组合电器本体A相盆式绝缘子",
               "模拟机器人Ⅱ区RP_003组合电器套管套管外观", "模拟机器人Ⅱ区gap01办公区间隔9540组合电器其他A相基础构架",
               "模拟机器人Ⅱ区gap01办公区间隔9540组合电器套管B相套管外观",
               "模拟机器人Ⅱ区gap01办公区间隔9540组合电器套管C相套管外观"]
# device_name= ["模拟机器人Ⅱ区RP_003组合电器本体本体外观","模拟导入五区"]
file_path = ["/upload/BJ_HT02/40/X040_HT02热成像监视区HT02_01设备间隔PJ001避雷器本体表计_40_BJ_HT02_20231031135315.jpg",
             "/upload/0BDZ_HT01/11/X003_HT02_01设备间隔PJ001避雷器_201_0BDZ_HT01_20231101153320.jpg",
             "/upload/0BDZ_HT01/14/X004_HT02_01设备间隔PJ002隔离开关A相_122_0BDZ_HT01_20231101154141.jpg",
             "/upload/0BDZ_HK122/2/X021_HT02_01设备间隔SW001开关柜刀闸开关B相_122_0BDZ_HK122_20231101154208.jpg",
             "/upload/0BDZ_HT01/12/TO009_JD01接地装置接地线缆线缆形状_缺陷判别_0BDZ_HT01_20231101154151.jpg",
             "/upload/0BDZ_HT01/4/HOT01_HT02热成像监视区测温区域FDS01辅助设施_测温1_0BDZ_HT01_20231107215218.jpg",
             "/upload/0BDZ_HT01/5/HOT02_测温区域FDS01辅助设施测温_2_0BDZ_HT01_20231102022209.jpg",
             "/upload/0BDZ_HT01/5/HOT02_测温区域FDS01辅助设施测温_2_0BDZ_HT01_20231107123759.jpg"
             ]

# 注册巡视主机
msg_register = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>251</Type>
    <Code/>
    <Command>1</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items/>
</PatrolDevice>
"""
msg_beat_err = """<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>robot_host</SendCode>
    <ReceiveCode>patrol_host</ReceiveCode>
    <Type>251</Type>
    <Command>2</Command>
    <Code>4294967295</Code>
    <Time>2023-06-06 16:00:56</Time>
    <Items/>
</PatrolDevice>
"""
# 心跳发送
msg_beat = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>251</Type>
    <Code/>
    <Command>2</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items/>
</PatrolDevice>
"""
# 机器人控制响应
robot_control_res = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>robot_host</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>251</Type>
    <Code>200</Code>
    <Command>3</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items/>
</PatrolDevice>
"""
# 无人机控制响应
wireless_control_res = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>uav_host</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>251</Type>
    <Code>200</Code>
    <Command>3</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items/>
</PatrolDevice>
"""
# 任务控制响应
task_control_res = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>251</Type>
    <Code>200</Code>
    <Command>4</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item task_patrolled_id="{task_patrol_id}"/>
    </Items>
</PatrolDevice>
"""
# 模型同步指令响应 需确保设备点位模型上报成功后，才能发送响应消息。
model_sync_res = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>251</Type>
    <Code>200</Code>
    <Command>4</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item device_file_path="/upload/edge001/Robot01/0_device_model_robot.xml"/>
    </Items>
</PatrolDevice>
"""
# 任务下发指令响应
task_create_res = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>251</Type>
    <Code>200</Code>
    <Command>4</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items/>
</PatrolDevice>
"""
# 检修区域指令响应
patorl_area_res = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>251</Type>
    <Code>200</Code>
    <Command>3</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items/>
</PatrolDevice>
"""
# 机器人状态数据上报 1
robot_msg_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>1</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="1" value="1" value_unit="1" unit=""/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="2" value="1" value_unit="1" unit=""/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="3" value="1" value_unit="1" unit=""/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="4" value="1" value_unit="1" unit=""/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="21" value="1" value_unit="1" unit=""/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="41" value="2" value_unit="2" unit=""/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="61" value="1" value_unit="1" unit=""/>
    </Items>
</PatrolDevice>
"""
# 无人机数据上报 11
wireless_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>uav_host</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>1</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="1" value="0" value_unit="0" unit=""/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="2" value="0" value_unit="0" unit=""/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="4" value="0" value_unit="0" unit=""/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="21" value="0" value_unit="0" unit=""/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="41" value="0" value_unit="0" unit=""/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="61" value="0" value_unit="0" unit=""/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="81" value="0" value_unit="0" unit=""/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="201" value="3" value_unit="3" unit=""/>
    </Items>
</PatrolDevice>
"""
# 巡视设备运行数据(一定时间间隔定时、主动向巡视主机上报) 2
robot_patrol_status = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>2</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="1" value="1" value_unit="1m/s" unit="m/s"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="2" value="100" value_unit="100m" unit="m"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="3" value="800" value_unit="800mAh" unit="mAh"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="8" value="30" value_unit="30°" unit="°"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="9" value="5" value_unit="5°" unit="°"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="10" value="3" value_unit="3°" unit="°"/>

    </Items>
</PatrolDevice>
"""
# 无人机运行数据(一定时间间隔定时、主动向巡视主机上报) 12
wireless_patrol_status = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>uav_host</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>2</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        # <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="1" value="1.8" value_unit="1.8m/s" unit="m/s"/>
        # <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="2" value="100" value_unit="100m" unit="m"/>
        # <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="3" value="812" value_unit="812mAh" unit="mAh"/>
        # <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="4" value="0.2" value_unit="0.2m/s" unit="m/s"/>
        # <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="5" value="888" value_unit="888m" unit="m"/>
        # <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="6" value="876" value_unit="876m" unit="m"/>
        # <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="7" value="800" value_unit="800h" unit="h"/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="8" value="30" value_unit="30°" unit="°"/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="9" value="3" value_unit="3°" unit="°"/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="10" value="-3" value_unit="-3°" unit="°"/>
        <Item patroldevice_name="蹦迪" patroldevice_code="drone_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="11" value="800" value_unit="800mA" unit="mA"/>
    </Items>
</PatrolDevice>
"""
# 无人机机巢状态数据 3
wireless_home_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>uav_host</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>20001</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="1" value="1" value_unit="1" unit=""/>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="2" value="1" value_unit="1" unit=""/>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="3" value="1" value_unit="1" unit=""/>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="4" value="1" value_unit="1" unit=""/>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="5" value="1" value_unit="1" unit=""/>
    </Items>
</PatrolDevice>
"""
# 无人机机巢运行数据 4
wireless_home_patrolData = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>uav_host</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>10004</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="1" value="98" value_unit="98%" unit="%"/>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="2" value="2" value_unit="2" unit=""/>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="3" value="1" value_unit="1" unit=""/>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="4" value="220" value_unit="220v" unit="v"/>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="5" value="30" value_unit="30℃" unit="℃"/>
        <Item nest_name="EVA" nest_code="{nest_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="6" value="30" value_unit="30%rh" unit="%rh"/>
    </Items>
</PatrolDevice>
"""
# 巡视坐标上报 5
patrol_position = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>3</Type>
    <Code>test1#</Code>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="walle" patroldevice_code="robot_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" coordinate_pixel="0,0,0,30" coordinate_geography="116,39"/>
    </Items>
</PatrolDevice>
"""
# 巡视路线上报 6
patrol_line = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>4</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="walle" patroldevice_code="robot_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" coordinate_pixel="0,0,0,30" coordinate_geography="116,39"/>
    </Items>
</PatrolDevice>
"""
# 巡视设备告警上报(产生异常告警时，主动向巡视主机上报)  <Item patroldevice_name="walle" patroldevice_code="robot_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" content="220kV保护小室起火"/>7
patrol_alarm = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>robot002</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>5</Type>
    <Code/>
    <Command>1</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="walle" patroldevice_code="robot_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" content="220kV保护小室起火"/>7
    </Items>
</PatrolDevice>
"""
# 环境数据上报 8
env_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>21</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="1" value="31.2" value_unit="31.2℃" unit="℃"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="2" value="32.1" value_unit="32.1RH" unit="RH"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="3" value="2.8" value_unit="2.8m/s" unit="m/s"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="4" value="60" value_unit="60mm" unit="mm"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="5" value="东南" value_unit="东南" unit=""/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="6" value="120" value_unit="120kpa" unit="kpa"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="7" value="22" value_unit="22%" unit="%"/>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="8" value="88" value_unit="88%" unit="%"/>
    </Items>
</PatrolDevice>
"""
# 环境数据上报-气温 81
temperature = round(random.uniform(20.0, 50.0), 2)
env_data_temperature = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>21</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="1" value="{temperature}" value_unit="{temperature}℃" unit="℃"/>
    </Items>
</PatrolDevice>
"""
# 环境数据上报-湿度 82
humidity = round(random.uniform(20.0, 50.0), 2)
env_data_humidity = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>21</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="2" value="{humidity}" value_unit="{humidity}RH" unit="RH"/>
    </Items>
</PatrolDevice>
"""
# 环境数据上报-风速 83
wind = round(random.uniform(0.0, 30.0), 2)
env_data_wind = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>21</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="3" value="{wind}" value_unit="{wind}m/s" unit="m/s"/>
    </Items>
</PatrolDevice>
"""
# 环境数据上报-降雨 84
rain = round(random.uniform(0.0, 150.0), 2)
env_data_rain = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>21</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="4" value="{rain}" value_unit="{rain}mm" unit="mm"/>
    </Items>
</PatrolDevice>
"""
# 环境数据上报-风向 85
trend = random.choices(["东南", "西北", "东北", "西南"])[0]
env_data_trend = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>21</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="5" value="{trend}" value_unit="{trend}" unit=""/>
    </Items>
</PatrolDevice>
"""
# 环境数据上报-气压 86
pressure = random.randint(90, 120)
env_data_pressure = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>21</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="6" value="{pressure}" value_unit="{pressure}kPa" unit="kPa"/>
    </Items>
</PatrolDevice>
"""
# 环境数据上报-氧气含量 87
oxygen = random.randint(18, 22)
env_data_oxygen = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>21</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="7" value="{oxygen}" value_unit="{oxygen}%" unit="%"/>
    </Items>
</PatrolDevice>
"""
# 环境数据上报-SF6含量 88
SF6 = round(random.randint(0, 1), 1)
env_data_sf = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>21</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{robot_code}" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" type="8" value="{SF6}" value_unit="{SF6}%" unit="%"/>
    </Items>
</PatrolDevice>
"""
# 任务状态 9-5
task_status_start = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>41</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item task_patrolled_id="{task_patrol_id}" task_name="{task_code}" task_code="{task_code}" task_state="5" plan_start_time="2023-10-18 19:56:20" start_time="" task_progress="0" task_estimated_time="10" description="test"/>
    </Items>
</PatrolDevice>
"""
# 任务状态 9-2
task_status_proceed = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>41</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item task_patrolled_id="{task_patrol_id}" task_name="{task_code}" task_code="{task_code}" task_state="2" plan_start_time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" start_time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" task_progress="70" task_estimated_time="55" description="test"/>
    </Items>
</PatrolDevice>
"""
# 任务状态 9-1
task_status_complete = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>41</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item task_patrolled_id="{task_patrol_id}" task_name="{task_code}" task_code="{task_code}" task_state="1" plan_start_time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" start_time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" task_progress="100" task_estimated_time="0" description="test"/>
    </Items>
</PatrolDevice>
"""
# 巡视结果上报 10
task_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>61</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_name}" task_code="{task_code}" device_name="{device_name[0]}" device_id="{device_id[0]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="1" file_path="{file_path[0]}" file_type="2" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
        <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_name}" task_code="{task_code}" device_name="{device_name[1]}" device_id="{device_id[1]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="1" file_path="{file_path[1]}" file_type="2" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
        <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_name}" task_code="{task_code}" device_name="{device_name[2]}" device_id="{device_id[2]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="2" file_path="{file_path[2]}" file_type="2" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
        <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_name}" task_code="{task_code}" device_name="{device_name[3]}" device_id="{device_id[3]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="2" file_path="{file_path[3]}" file_type="2" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
        <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_name}" task_code="{task_code}" device_name="{device_name[4]}" device_id="{device_id[4]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="3" file_path="{file_path[4]}" file_type="2" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
        <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_name}" task_code="{task_code}" device_name="{device_name[5]}" device_id="{device_id[5]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="4" file_path="{file_path[5]}" file_type="1" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
        <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_name}" task_code="{task_code}" device_name="{device_name[6]}" device_id="{device_id[6]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="4" file_path="{file_path[6]}" file_type="1" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
        <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_name}" task_code="{task_code}" device_name="{device_name[7]}" device_id="{device_id[7]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="4" file_path="{file_path[7]}" file_type="1" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
    </Items>
</PatrolDevice>
"""
# task_data = f"""<?xml version="1.0" encoding="UTF-8"?>
# <PatrolDevice>
#     <SendCode>{s_code}</SendCode>
#     <ReceiveCode>{r_code}</ReceiveCode>
#     <Type>61</Type>
#     <Code/>
#     <Command/>
#     <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
#     <Items>
#         <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_name}" task_code="{task_code}" device_name="{device_name[0]}" device_id="{device_id[0]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="1" file_path="{file_path[0]}" file_type="2" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
#         <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_name}" task_code="{task_code}" device_name="{device_name[1]}" device_id="{device_id[1]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="1" file_path="{file_path[1]}" file_type="2" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
#     </Items>
# </PatrolDevice>
# """
# task_data = f"""<?xml version="1.0" encoding="UTF-8"?>
# <PatrolDevice>
#     <SendCode>{s_code}</SendCode>
#     <ReceiveCode>{r_code}</ReceiveCode>
#     <Type>61</Type>
#     <Code/>
#     <Command/>
#     <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
#     <Items>
#         <Item patroldevice_name="{s_code}" patroldevice_code="{s_code}" task_name="{task_code}" task_code="{task_code}" device_name="{device_name[0]}" device_id="{device_id[0]}" unit="" valid="1" value="3" value_type="0" value_unit="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" recognition_type="1" file_path="{file_path[0]}" file_type="2" material_id=""  rectangle="" task_patrolled_id="{task_patrol_id}" />
#     </Items>
# </PatrolDevice>
# """
# 固件升级结果上报101
firmware_result = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>50000</Type>
    <Code>200</Code>
    <Command>1</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item firmwareVersion="v2.00" result="1" taskCode="20230915091243085953" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"/>
    </Items>
</PatrolDevice>
"""
# 控制状态上报201
control_msg = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>80000</Type>
    <Code/>
    <Command>1</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="1" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="1" value_unit="1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="2" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="1" value_unit="1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="4" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="5" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="1" value_unit="1" unit="" />
    </Items>
</PatrolDevice>
"""
# 通信状态上报 301
communicate_msg = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>90000</Type>
    <Code/>
    <Command>1</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="1" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="1" value_unit="1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="2" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="1" value_unit="1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="4" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="5" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="1" value_unit="1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="6" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
    </Items>
</PatrolDevice>
"""
# 模块状态上报401
battery = random.randint(1, 100)
milage = random.randint(100, 9999)
model_msg = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>100000</Type>
    <Code/>
    <Command>1</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="1" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="1" value_unit="1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="2" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="3" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="1" value_unit="1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="4" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="5" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="1" value_unit="1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="6" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="7" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="8" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="9" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="10" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="-1" value_unit="-1" unit="" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="11" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="{battery}" value_unit="{battery}%" unit="%" />
        <Item patroldevice_name="{robot_name}" patroldevice_code="{s_code}" type="12" time="{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}" value="{milage}" value_unit="{milage}m" unit="m" />
    </Items>
</PatrolDevice>
"""
# 路径规划 61
line_plan = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>60001</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="模拟机器人" patroldevice_code="Robot01" task_code="任务id" sort="1" position="x,y,z,θ" />
        <Item patroldevice_name="模拟机器人" patroldevice_code="Robot01" task_code="任务id" sort="2" position="x,y,z,θ" />
        <Item patroldevice_name="模拟机器人" patroldevice_code="Robot01" task_code="任务id" sort="3" position="x,y,z,θ" />
    </Items>
</PatrolDevice>
"""
# 实时坐标 62
coordinate = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>3</Type>
    <Code/>
    <Command/>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items>
        <Item patroldevice_name="模拟机器人" patroldevice_code="Robot01" time="时间" coordinate_pixel="1，2，3，4" coordinate_geography="x,y,z,θ" />
    </Items>
</PatrolDevice>
"""
# 临时消息
tmp_msg = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>61000</Type>
    <Command/>
    <Code/>
    <Time>2023-11-17 11:19:44</Time>
    <Items>
        <Item patroldevice_code="robot_203" patroldevice_name="robot_203" radar_point="6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.626991,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,1.555763,1.519768,1.535766,1.547764,6.900000,6.900000,1.707740,1.583759,1.555763,1.526170,1.537889,1.533895,1.567761,1.516611,1.536462,1.544402,1.556312,1.556312,1.572193,1.633759,1.491773,1.562033,1.572400,1.571761,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,6.900000,0.961995,0.983738,0.963984,0.980636,0.976665,0.972286,0.976271,0.966673,0.987850,1.219814,1.039842,0.975851,0.971852,0.963853,6.900000" time="20231117111944"/></Items>
</PatrolDevice>
"""
start_flag = b'\xeb\x90'
# 发送会话序列号?
send_flag = b'\x01\x00\x00\x00\x00\x00\x00\x00'
# 接收会话序列号 会话序号带回
rcv_flag = b'\x00\x00\x00\x00\x00\x00\x00\x00'
# 0x00标识会话请求，0x01标识会话响应，其它异常会话
send_session_flag = b'\x00'
rcv_session_flag = b'\x01'
xml_flag = b'\xf1\x00\x00\x00'
end_flag = b'\xeb\x90'

logging.basicConfig(level=logging.INFO)


def send_msg(sock, msg: str, num):
    sock.sendall(package_msg2bytes(msg, num))
    time.sleep(60)


def int2bytes_msg(msg: str):
    return len(bytes(msg, encoding="utf8")).to_bytes(4, "little")


def bytes2int_msg(msg: bytes):
    return int.from_bytes(msg, byteorder='little')


def parser_msg(msg: bytes):
    # bytes_len = msg[20:24]
    # tmp = msg.split(end_flag)
    msg_dict = {}
    logging.info("获取完整缓冲区批量数据：↓")
    logging.info(msg)
    for item in msg.split(b'\xeb\x90'):
        if item != b'':
            msg_dict.update({item[0:17]: item[21::]})
    # return str(b''.join(item[23:-2] for item in msg.split(b'\xeb\x90') if item != b''), encoding="utf8")
    return msg_dict


def heat_beat():
    global count
    while True:
        msg_beat = f"""<?xml version="1.0" encoding="UTF-8"?>
<PatrolDevice>
    <SendCode>{s_code}</SendCode>
    <ReceiveCode>{r_code}</ReceiveCode>
    <Type>251</Type>
    <Code/>
    <Command>2</Command>
    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
    <Items/>
</PatrolDevice>
"""
        sock.sendall(package_msg2bytes(msg_beat, count))
        count += 1
        time.sleep(5)


def rcv_msg(socket):
    msg = b''
    while True:
        msg += sock.recv(1024)
        if msg.endswith(end_flag):
            return parser_msg(msg)


def send_position():
    while True:
        patrol_position = f"""<?xml version="1.0" encoding="UTF-8"?>
        <PatrolDevice>
            <SendCode>{s_code}</SendCode>
            <ReceiveCode>{r_code}</ReceiveCode>
            <Type>3</Type>
            <Code>{s_code}</Code>
            <Command/>
            <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
            <Items>
                <Item patroldevice_name="模拟机器人" patroldevice_code="robot001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" coordinate_pixel="{random.randint(1, 2500)},{random.randint(1, 2500)},0,30" coordinate_geography="116,39"/>
            </Items>
        </PatrolDevice>
        """
        sock.sendall(package_msg2bytes(patrol_position, 0))
        time.sleep(30)


def send_lidar():
    while True:
        # time.sleep(10)
        sock.sendall(package_msg2bytes(tmp_msg, 0))
        time.sleep(10)


def package_msg2bytes(msg: str, send_count: int, tag=True, rcv_num=rcv_flag):
    if tag:
        return start_flag + send_count.to_bytes(8, 'little') + (0).to_bytes(8,
                                                                            'little') + send_session_flag + int2bytes_msg(
            msg) + bytes(msg, encoding="utf8") + end_flag
    else:
        return start_flag + send_count.to_bytes(8, 'little') + rcv_num + rcv_session_flag + int2bytes_msg(
            msg) + bytes(msg, encoding="utf8") + end_flag


def upload_msg(q: Queue):
    global count
    while True:
        if q.empty():
            time.sleep(1)
        else:
            cmd = q.get()
            if cmd == "1":
                logging.info("上送机器人状态")
                sock.sendall(package_msg2bytes(robot_msg_data, count))
                count += 1
            elif cmd == "11":
                logging.info("上送无人机状态数据")
                sock.sendall(package_msg2bytes(wireless_data, count))
                count += 1
            elif cmd == "2":
                logging.info("上送机器人运行数据")
                sock.sendall(package_msg2bytes(robot_patrol_status, count))
                count += 1
            elif cmd == "12":
                logging.info("上送无人机运行数据")
                sock.sendall(package_msg2bytes(wireless_patrol_status, count))
                count += 1
            elif cmd == "3":
                logging.info("上送无人机机巢状态")
                sock.sendall(package_msg2bytes(wireless_home_data, count))
                count += 1
            elif cmd == "4":
                logging.info("上送无人机机巢运行状态")
                sock.sendall(package_msg2bytes(wireless_home_patrolData, count))
                count += 1
            elif cmd == "5":
                logging.info("上送巡视坐标数据")
                sock.sendall(package_msg2bytes(patrol_position, count))
                count += 1
            elif cmd == "6":
                logging.info("上送巡视路线数据")
                sock.sendall(package_msg2bytes(patrol_line, count))
                count += 1
            elif cmd == "61":
                logging.info("上送巡视路线数据")
                sock.sendall(package_msg2bytes(line_plan, count))
                count += 1
            elif cmd == "62":
                logging.info("上送巡视路线数据")
                sock.sendall(package_msg2bytes(coordinate, count))
                count += 1
            elif cmd == "7":
                patrol_alarm = f"""<?xml version="1.0" encoding="UTF-8"?>
                <PatrolDevice>
                    <SendCode>{s_code}</SendCode>
                    <ReceiveCode>{r_code}</ReceiveCode>
                    <Type>5</Type>
                    <Code/>
                    <Command>1</Command>
                    <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
                    <Items>
                        <Item patroldevice_name="walle" patroldevice_code="robot_001" time="{(datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")}" content="220kV保护小室起火"/>7
                    </Items>
                </PatrolDevice>
                """
                logging.info("上送巡视报警数据")
                sock.sendall(package_msg2bytes(patrol_alarm, count))
                count += 1
                patrol_alarm1 = f"""<?xml version="1.0" encoding="UTF-8"?>
                        <PatrolDevice>
                            <SendCode>{s_code}</SendCode>
                            <ReceiveCode>{r_code}</ReceiveCode>
                            <Type>60000</Type>
                            <Code/>
                            <Command>1</Command>
                            <Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>
                            <Items>
                                <Item warn_type="170464" alarm_sub="绝对值编码器角度初始化警告" alarm_type="2" time="{(datetime.datetime.now() + datetime.timedelta(minutes=-1)).strftime("%Y-%m-%d %H:%M:%S")}" device_module="170" message="-"/>
                            </Items>
                        </PatrolDevice>
                        """
                logging.info("上送巡视报警数据")
                sock.sendall(package_msg2bytes(patrol_alarm1, count))
                count += 1
            elif cmd == "8":
                logging.info("上送环境数据信息")
                temperature = round(random.uniform(20.0, 50.0), 2)
                humidity = round(random.uniform(20.0, 50.0), 2)
                wind = round(random.uniform(0.0, 30.0), 2)
                rain = round(random.uniform(0.0, 150.0), 2)
                trend = random.choices(["东南", "西北", "东北", "西南"])[0]
                for item in random.choices(
                        [env_data_temperature, env_data_humidity, env_data_wind, env_data_rain, env_data_trend,
                         env_data_pressure, env_data_oxygen, env_data_sf]):
                    print(item)
                    sock.sendall(package_msg2bytes(item, count))
                    count += 1
                # sock.sendall(package_msg2bytes(env_data, count))
                # count += 1
            elif cmd == "95":
                logging.info("上送任务状态变更")
                sock.sendall(package_msg2bytes(task_status_start, count))
                count += 1
            elif cmd == "92":
                logging.info("上送任务状态变更")
                sock.sendall(package_msg2bytes(task_status_proceed, count))
                count += 1
            elif cmd == "91":
                logging.info("上送任务状态变更")
                sock.sendall(package_msg2bytes(task_status_complete, count))
                count += 1
            elif cmd == "10":
                logging.info("上送任务结果")
                sock.sendall(package_msg2bytes(task_data, count))
                count += 1
            elif cmd == "101":
                logging.info("上送升级结果")
                sock.sendall(package_msg2bytes(firmware_result, count))
                count += 1
            elif cmd == "201":
                logging.info("上送控制状态结果")
                sock.sendall(package_msg2bytes(control_msg, count))
                count += 1
            elif cmd == "301":
                logging.info("上送通信状态结果")
                sock.sendall(package_msg2bytes(communicate_msg, count))
                count += 1
            elif cmd == "401":
                logging.info("上送模块状态结果")
                sock.sendall(package_msg2bytes(model_msg, count))
                count += 1
            elif cmd == "501":
                logging.info("上送设备巡视路线")
                sock.sendall(package_msg2bytes(tmp_msg, count))
                count += 1
            q.task_done()
            # sock.sendall(package_msg2bytes(msg_beat, count))


def get_user_input(q: Queue):
    while True:
        option = input("请输入想要上报的消息:")
        q.put(option)
        q.join()


# class REC_MESSAGE(threading.Thread):
#     def __init__(self, socket):
#         threading.Thread.__init__(self)
#         self.socket = socket
#
#      def run(self):
#          while True:
#              msg = self.socket.recv(1024)


if __name__ == '__main__':
    # for i in range(1024):
    option_queue = Queue()
    sock = socket.socket()
    sock.connect(('192.168.60.100', 10011))
    count = 0
    if count == 0:
        # msg = package_msg2bytes(msg_register, count)
        print(package_msg2bytes(msg_register, count))
        sock.sendall(package_msg2bytes(msg_register, count))
        count += 1
    heat_task = threading.Thread(target=heat_beat, args=())
    input_task = threading.Thread(target=get_user_input, args=(option_queue,))
    input_task.daemon = True
    interactive_task = threading.Thread(target=upload_msg, args=(option_queue,))
    # position_task = threading.Thread(target=send_position)
    # lidar_task = threading.Thread(target=send_lidar)
    heat_task.start()
    input_task.start()
    interactive_task.start()
    # position_task.start()
    # lidar_task.start()
    while True:
        # print("准备获取msg")
        server_msg = rcv_msg(socket)
        # print(f"获取到{server_msg}")
        for item in server_msg:
            print(item, item[16::], send_flag)
            if item[16::] == send_session_flag:
                logging.info("响应平台消息：")
                normal_msg = f"""<?xml version="1.0" encoding="UTF-8"?>\n<PatrolDevice>\n\t<SendCode>{s_code}</SendCode>\n\t<ReceiveCode>{r_code}</ReceiveCode>\n\t<Type>251</Type>\n\t<Code>200</Code>\n\t<Command>3</Command>\n\t<Time>{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</Time>\n\t<Items/>\n</PatrolDevice>"""
                sock.send(package_msg2bytes(normal_msg, count, tag=False, rcv_num=item[0:8]))
                count += 1
    sock.close()
