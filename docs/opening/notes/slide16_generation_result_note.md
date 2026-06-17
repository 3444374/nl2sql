【汇报讲稿】
这一页解释生成成本实验的结果表。实验样例仍然是同一批 30 条自建订单查询。每条样例使用同一个模型、同一套 schema 信息和相近的 prompt 框架，只改变目标输出形式：Direct SQL、SQL+、NatSQL-style proxy 和 SemQL-style proxy。模型输出后，先判断输出是否符合对应表示的格式要求，再尽量转换为 SQL 并在同一个 SQLite 数据库上执行，最后与 gold SQL 的执行结果比较。

表里的 Valid repr 表示模型输出是否满足对应 IR 的基本格式，例如 SQL+ 是否能被当前 parser 接受，proxy 表示是否能被实验脚本识别。Valid SQL 表示输出或转换结果能否成为可执行 SQL。Exec match 表示可执行 SQL 的结果是否与 gold SQL 一致。平均 token 直接来自模型 API 返回的 usage 字段，统计 input、output 或 total token；平均 latency 是脚本从发起请求到收到响应记录的耗时平均值，单位是秒。

结果说明，SQL+ 比 Direct SQL 多获得了少量 execution match，但 token 和 latency 都更高。因此这页不能被解读为 SQL+ 初次生成更省成本。更合理的解释是：SQL+ 在第一轮生成阶段引入了步骤化表达开销，是否值得使用，要看后续错误定位和局部修复收益能否抵消这部分额外开销。

【答辩备注】
如果老师问“为什么 SQL+ token 更高”，回答：因为 SQL+ 把查询拆成多行步骤，显式写出 JOIN、FILTER、AGG、ORDER 等中间过程，文本自然可能更长。这个结果反而帮助我们收敛研究定位：SQL+ 的核心价值不是初次生成更短，而是为后续 Critic、Router 和 Repair Skill 提供可定位的中间步骤。
