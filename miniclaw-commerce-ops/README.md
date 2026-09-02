# MiniClaw 电商运营数据分析多 Agent 工作台

## 项目定位

本项目面向电商运营负责人、内容运营、直播运营、渠道运营和销售转化团队，将短视频、直播、账号、渠道、线索、销售跟进和订单数据组织成可追溯、可评测的经营分析工作流。

目标业务链路：

`短视频曝光 → 互动点击 → 直播承接 → 线索进入 → 销售跟进 → 订单转化 → 经营复盘`

目标 Agent 结构为“一主四专”：

- `commerce_ops_supervisor`：规范目标、生成 run_id、调度专业 Agent、校验和汇总；不直接调用业务工具。
- `content_growth_analyst`：负责短视频、内容、账号和发布时段诊断。
- `live_conversion_analyst`：负责直播观看、互动、点击、留资、下单和成交漏斗诊断。
- `attribution_lead_analyst`：负责渠道、线索来源、负责人、跟进和订单关联分析。
- `commerce_review_strategist`：只读取通过门槛的诊断包，输出行动、责任岗位、时限和复验指标。

严格限制为五个只读工具：

- `inspect_commerce_data`
- `analyze_short_video_data`
- `analyze_live_commerce_data`
- `analyze_attribution_and_leads`
- `drilldown_commerce_metric`
