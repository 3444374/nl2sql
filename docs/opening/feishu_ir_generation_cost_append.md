## 十、IR 生成成本与执行效果对比实验

本节补充第二个中间表示对比实验，用来回答“为什么使用 SQL+，而不是直接 SQL、NatSQL 或 SemQL”这个问题。实验使用同一模型、同一批 30 条自建订单分析样例，比较 Direct SQL、SQL+、NatSQL-style proxy 和 SemQL-style proxy 的表示有效率、SQL 可执行率、执行一致率、token 成本和生成延迟。

| 方法 | 表示有效 | SQL 可执行 | 执行一致 | 平均输入 token | 平均输出 token | 平均总 token | 平均延迟 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct SQL | 30/30 | 30/30 | 12/30 | 287.6 | 311.5667 | 599.1667 | 6.5851s |
| SQL+ | 28/30 | 28/30 | 14/30 | 319.1333 | 493.9 | 813.0333 | 9.2197s |
| NatSQL-style proxy | 30/30 | 30/30 | 13/30 | 319.1333 | 421.6333 | 740.7667 | 6.2802s |
| SemQL-style proxy | 30/30 | 25/30 | 12/30 | 343.1333 | 685.8333 | 1028.9667 | 9.9684s |

实验边界：

- NatSQL-style 和 SemQL-style 是开题阶段的 controlled proxy，用于比较表达形态和生成成本，不代表完整复现 NatSQL 或 IRNet/SemQL 系统。
- 本实验中的 Direct SQL 是统一 IR 对比 prompt 下的结果，不替代此前 Direct NL2SQL baseline 的 16/30。
- SQL+ 两个无效样例主要来自模型生成了当前 SQL+ parser 尚不支持的 `LEFT` 步骤，说明 SQL+ 语法约束和 prompt 仍需继续收紧。

阶段性结论：

SQL+ 在这组样例上的执行一致率为 14/30，略高于 NatSQL-style proxy 的 13/30 和 Direct SQL、SemQL-style proxy 的 12/30，但差距很小，不能写成显著准确率优势。与此同时，SQL+ 的平均总 token 为 813.0333，平均延迟为 9.2197s，均高于 Direct SQL 和 NatSQL-style proxy。这说明 SQL+ 的步骤化表达确实带来生成成本。

因此，后续开题论证不应把 SQL+ 的价值简单写成“更短”或“初次生成更准”。更合理的研究假设是：SQL+ 通过额外的步骤边界，换取更清晰的错误定位、更小的局部 patch 范围和更稳定的 repair skill 路由。下一步实验需要继续比较 error localization accuracy、patch minimality、average repair rounds、repair token cost 和 repair latency，验证 SQL+ 的修复收益能否抵消生成阶段的额外开销。
