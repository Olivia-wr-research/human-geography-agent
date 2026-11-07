# 阶段契约

所有阶段以真实输入、执行产物、审阅记录和研究者决定为闭环。文件存在检查只是技术条件。每个阶段目录另有 `review.md`，记录检查对象、发现、严重程度、未解决事项和审阅者。不得只写 PASS。

| 阶段 | 输入 | 核心产物 | 验收问题 |
|---|---|---|---|
| question | 研究动机、可获得资料 | brief.md：问题、机制、范围、替代解释 | 空间为什么重要？研究的是人、地方还是关系？ |
| literature | 问题与检索边界 | literature.csv：检索式、来源、定位、判断 | 贡献是否经过比较？未读全文是否标注？ |
| measurement | 授权原始资料、实体与边界 | data_dictionary.csv；匹配和排除日志 | 人、机构、城市、事件、年份是否可追溯？ |
| design | 样本与变量规格 | design.md；冻结规格与哈希 | 时间顺序、估计对象、支持范围、识别假设是否一致？ |
| analysis | 冻结设计与数据 | analysis.md；脚本、结果表、诊断 | 是否收敛？有效样本与文章是否一致？ |
| robustness | 主模型与事前威胁清单 | robustness.csv | 每项检验对应什么威胁？是否完整报告负结果？ |
| mapping | 经核验的地理数据和图表清单 | map_review.md；QGIS 项目、图件、导出记录 | 投影、尺度、边界、图例、缺失、来源是否正确？ |
| writing | 权威结果与文献 | claims.csv；稿件和表图 | 每条结论是否有证据定位？语言有无超出设计？ |
| release | 全部产物及权利清单 | release_review.md；公开白名单 | 能否重跑？哪些可公开？敏感和受限材料是否排除？ |

## 运行和续接

在仓库根目录执行 `python scripts/workflow.py init --project work/study`。
工具将阶段置为 pending。研究者完成首阶段产物及审阅后，可自行执行：

```bash
python scripts/workflow.py decide --project work/study --decision approved --by researcher --note '已核对研究问题和空间单元'
python scripts/workflow.py status --project work/study
```

`revision_required` 保留当前阶段等待修改；`rejected` 阻断后续阶段。工具不是身份认证或不可篡改审计系统；`--by` 只是审计记录，Agent 不得冒充研究者填写。批准时保存文件哈希，后续状态检查发现已批准文件变化则停止，要求新建修订研究目录并说明版本关系，避免静默沿用旧批准。

## 人文地理补充

每次改变分析尺度、边界版本、空间权重或地理编码方案，都写明受影响的样本与解释。考虑 MAUP、生态谬误、空间溢出、位置不确定性、历史边界变化，以及弱势群体/敏感地点的披露风险。定性研究用访谈/档案采样和编码审计替代模型诊断，保留反例、反思性与来源语境；相应阶段文件记录适用性理由，而不是伪造量化结果。
