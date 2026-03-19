# MCP 完整链路说明：它是怎么定义的、怎么加载的、AI 又怎么知道该用哪个工具？

这份文档是给新手看的。

目标不是把你淹死在协议细节里，而是让你真正搞明白这几件事：

1. **MCP 到底是什么**
2. **MCP Server 是怎么把工具“定义”出来的**
3. **MCP Client 是怎么“加载”这些工具的**
4. **AI 模型为什么会知道该调用哪个工具**
5. **一次完整调用到底经历了什么链路**

如果你以前总觉得 MCP 很玄，放心，本质上它没有那么神秘。

---

## 1. 一句话先讲明白

MCP（Model Context Protocol）本质上是：

> **让 AI 客户端用统一方式发现、读取、调用外部能力的一套标准协议。**

这里有几个关键词：
- **统一方式**：别每家客户端都搞一套完全不一样的插件协议
- **发现**：客户端先知道你有哪些工具
- **读取**：客户端能拿到资源、提示模板等内容
- **调用**：客户端真的可以执行工具

所以你可以把 MCP 理解成 AI 世界里的“标准化工具插座”。

---

## 2. MCP 里到底有哪些角色？

最重要的是这三个：

### 2.1 MCP Server
你写的那个 Python 项目，就是 MCP Server。

它负责：
- 对外声明“我有哪些工具”
- 告诉客户端每个工具叫什么、参数是什么
- 在客户端请求时真正执行工具逻辑
- 返回结果

比如你这个仓库里的：
- `hello`
- `add`
- `init_notes_db`
- `insert_note`
- `list_notes`
- `search_notes`

这些都是 MCP Server 暴露出来的能力。

---

### 2.2 MCP Client
MCP Client 是“接入工具的那一侧”。

它通常是：
- 桌面 AI 应用
- IDE 插件
- Agent 框架
- 聊天客户端里的 Agent 容器

它负责：
- 启动 MCP Server
- 读取 MCP Server 提供的工具列表
- 把工具信息告诉底层模型
- 在模型决定“要调用工具”时，真的去调用
- 把结果再交还给模型继续生成回答

所以：
- **Server 提供能力**
- **Client 管理连接和转发**
- **Model 负责推理要不要用、用哪个**

---

### 2.3 Model（大模型）
模型本身通常不直接启动你的 Python 进程。

模型更像“大脑”，但手脚通常在客户端手里。

模型会看到一份“可用工具说明书”，然后根据用户问题推断：
- 要不要用工具
- 用哪个工具
- 传什么参数

然后客户端替它执行。

这一点很关键：

> **真正执行工具的，通常不是模型本体，而是 MCP Client / Agent Runtime。**

模型负责“做决定”，客户端负责“跑流程”。

---

## 3. MCP 是怎么“定义”工具的？

你在 Python 里写：

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("beginner-python-mcp")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b
```

你眼里这只是一个 Python 函数。

但从 MCP 的角度看，这件事做了两层事情：

### 第一层：你写了真正的业务逻辑
也就是：
- 输入两个数
- 返回和

### 第二层：你给这个函数加了“协议层元数据”
`@mcp.tool()` 这个装饰器相当于告诉 MCP 框架：

> “这个函数不是普通内部函数，它是要对外暴露给客户端调用的工具。”

于是框架会把它登记起来。

---

## 4. 客户端看到的“工具定义”到底长什么样？

客户端真正关心的，不是你内部怎么写的，而是这些信息：

- 工具名：`add`
- 说明：`Add two numbers.`
- 参数：
  - `a`: number
  - `b`: number
- 返回值：number

也就是说，客户端需要的是一种“机器可读的函数说明书”。

### 4.1 在这个 Python 示例里，`name` 和 `description` 到底写在哪里？

拿这个例子说：

```python
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b
```

这里通常是这样映射的：

- **tool name**：默认来自函数名，也就是 `add`
- **tool description**：通常来自函数 docstring，也就是 `Add two numbers.`
- **参数 schema**：通常来自函数签名和类型注解
  - `a: float`
  - `b: float`
- **返回类型信息**：通常来自返回类型注解 `-> float`

所以对新手来说，可以先粗暴记成：

> **函数名 = 工具名，docstring = 工具说明，类型注解 = 参数说明的基础来源。**

当然，不同 SDK 允许的自定义程度会不同，但在 FastMCP 这种写法里，你最先需要关心的就是这三样。

### 4.2 为什么 `name` 和 `description` 这么重要？

因为模型多数时候并不是读你的源码细节，而是读这份“工具说明书”。

如果你把名字起成：
- `x1`
- `do_it`
- `final_tool_v2`

模型就很容易懵。

而如果你写成：
- `search_notes`
- `insert_note`
- `list_notes`

再配上清楚的 docstring，模型选对工具的概率会明显更高。

你可以把这理解成：

> **工具给模型看的第一层 UI，其实就是 name + description + schema。**

你可以把它想成类似：

```json
{
  "name": "add",
  "description": "Add two numbers.",
  "input_schema": {
    "type": "object",
    "properties": {
      "a": {"type": "number"},
      "b": {"type": "number"}
    },
    "required": ["a", "b"]
  }
}
```

是不是很像 OpenAI function calling / tool calling 里那种 schema？

没错，思路非常像。

差别在于：
- OpenAI 风格通常是客户端自己组织工具 schema
- MCP 是通过标准协议从外部 Server 动态发现这些定义

---

## 5. MCP Client 是怎么“加载”你的 Server 的？

通常不是“导入 Python 包”这么简单，而是：

> **启动一个独立进程，然后通过协议通信。**

比如客户端配置里写：

```json
{
  "mcpServers": {
    "beginner-python-mcp": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "beginner_python_mcp.server"]
    }
  }
}
```

这表示客户端会：
1. 启动这个命令
2. 跟这个进程建立 MCP 通信
3. 询问它支持哪些能力
4. 把工具清单纳入当前会话可用工具集合

---

## 6. 为什么很多 MCP Server 看起来“启动后没反应”？

因为很多 MCP Server 默认不是 HTTP 服务，而是 **stdio 模式**。

也就是说：
- 不是开一个网页端口给你访问
- 而是通过标准输入/输出和客户端通信

所以你手动运行：

```bash
python -m beginner_python_mcp.server
```

看起来像“没反应”，其实它是在等客户端连它。

这很像一个电话已经拨通，但还没人说话。

---

## 7. MCP 的“加载”过程，实际发生了什么？

下面给你按顺序拆开。

### 第 1 步：用户打开支持 MCP 的 AI 客户端
比如某个桌面客户端、IDE、Agent 平台。

### 第 2 步：客户端读取配置
它会看到类似：
- 有一个 MCP Server 叫 `beginner-python-mcp`
- 启动命令是什么
- 参数是什么

### 第 3 步：客户端启动 Server 进程
比如执行：

```bash
/absolute/path/to/.venv/bin/python -m beginner_python_mcp.server
```

### 第 4 步：客户端和 Server 做协议握手
此时会发生类似这些事情：
- 初始化连接
- 确认支持的能力
- 查询 tools/resources/prompts

### 第 5 步：客户端拿到工具清单
客户端会得到：
- `hello`
- `add`
- `init_notes_db`
- `insert_note`
- `list_notes`
- `search_notes`

以及每个工具的：
- 名称
- 描述
- 参数 schema

### 第 6 步：客户端把这些工具“展示给模型”
注意，这里通常不是把 Python 代码给模型看。

给模型看的通常是：
- 工具名
- 工具说明
- 参数结构

这一步很关键。

模型知道工具，不是因为它“读懂了你的源码”，而是因为：

> **客户端把 MCP Server 返回的工具描述，整理成模型可理解的工具列表，交给模型。**

---

## 8. 模型到底是怎么知道“该用哪个工具”的？

这是大家最容易神化的一步，其实本质上是：

> **模型根据用户问题 + 工具描述 + 当前上下文，做一次选择。**

举个例子。

用户说：

> 帮我查一下最近的笔记里有没有提到 MCP

此时模型会看到可用工具里有：
- `search_notes(keyword, limit)`：Search notes by keyword in title or content.
- `list_notes(limit)`：List recent notes from the local SQLite database.
- `add(a, b)`：Add two numbers.

那它大概率会想：
- 这个需求和“搜索笔记”最相关
- `add` 明显不对路
- `search_notes` 描述最匹配

于是模型会输出一种类似“我想调用这个工具”的结构化请求：

```json
{
  "tool_name": "search_notes",
  "arguments": {
    "keyword": "MCP",
    "limit": 10
  }
}
```

注意：
- 这不是模型真的自己在操作 SQLite
- 这是模型在**建议 / 请求**客户端去调这个工具

然后客户端才会真去执行。

---

## 9. 完整调用链路：从用户一句话到工具执行完成

下面是最关键的一部分。

假设用户说：

> 帮我记一条笔记：标题叫“学习 MCP”，内容是“今天终于搞明白完整链路了”

完整链路大致是这样：

### 阶段 A：用户发出请求
用户 -> AI 客户端

用户输入自然语言。

---

### 阶段 B：客户端整理上下文
客户端会把这些东西准备给模型：
- 用户当前问题
- 聊天历史
- 系统提示词
- 可用工具列表（来自 MCP Server）

这里的工具列表会包含类似：

- `insert_note(title, content)`
- 描述：Insert one note into the local SQLite database.
- 参数：`title`、`content`

---

### 阶段 C：模型做推理
模型读完以后，会判断：
- 用户不是在闲聊
- 用户是在要求“记录一条笔记”
- 可用工具中 `insert_note` 最匹配

于是模型输出一个工具调用意图：

```json
{
  "tool_name": "insert_note",
  "arguments": {
    "title": "学习 MCP",
    "content": "今天终于搞明白完整链路了"
  }
}
```

---

### 阶段 D：客户端执行工具调用
客户端收到这个结构化请求后，会：
1. 找到对应的 MCP Server
2. 向 Server 发起工具调用请求
3. 把参数传过去

也就是等价于让你的 Python 代码执行：

```python
insert_note(
    title="学习 MCP",
    content="今天终于搞明白完整链路了"
)
```

---

### 阶段 E：Server 执行真实逻辑
你的 Server 里这个函数会：
- 连接 SQLite
- 写入 `notes` 表
- 提交事务
- 返回结果

例如：

```text
Inserted note: 学习 MCP
```

---

### 阶段 F：客户端把结果交回模型
客户端拿到工具返回值后，不会就此结束。

通常它还会把这条工具结果再次提供给模型，让模型继续生成自然语言回复。

于是模型再基于工具结果生成类似回答：

> 好了，已经记下来了：学习 MCP。

---

### 阶段 G：最终回复给用户
客户端把模型最终自然语言输出显示给用户。

所以完整流向是：

```text
用户 -> 客户端 -> 模型（决定用工具）
   -> 客户端 -> MCP Server（执行工具）
   -> 客户端 -> 模型（整理结果）
   -> 用户
```

这就是 MCP 的完整调用链。

---

## 10. 那资源（resources）和提示模板（prompts）怎么参与链路？

工具不是 MCP 的全部。

### 10.1 Resource
Resource 更像“可读内容”。

比如：
- 文档
- 配置
- 指南
- 知识片段

客户端可以读取 resource，然后把内容交给模型当上下文。

它更像：
- “给模型补资料”
而不是
- “让模型执行动作”

---

### 10.2 Prompt
Prompt 是可复用模板。

比如：
- 教学模板
- 审查模板
- 结构化分析模板

客户端可以拿 prompt 模板生成一段标准化提示，再交给模型。

它更像“帮助组织提问方式”。

---

## 11. AI 模型是不是“自己学会”工具的？

不是严格意义上的“学会源码”。

更准确地说：

> 模型在当前会话里，临时获得了一组工具说明，并基于这些说明做决策。

所以模型知道怎么用工具，通常依赖这几个因素：

### 11.1 工具名是否清晰
比如：
- `search_notes` 就很清晰
- `do_task_v2_final` 就很迷惑

### 11.2 描述是否清晰
如果描述写得准确，模型更容易选对。

比如：
- `Search notes by keyword in title or content.`
这就非常明确。

### 11.3 参数是否清晰
参数名、类型、是否必填，都影响模型能不能正确构造调用。

### 11.4 当前上下文是否足够
如果用户说得很含糊，模型也可能选错工具，或者先追问。

---

## 12. 为什么有时模型不用工具？

因为它会先判断“有没有必要”。

比如用户问：

> MCP 是什么？

这类问题模型可能直接回答，不一定需要调工具。

但如果用户问：

> 你帮我查下数据库里有没有我昨天写的学习笔记

那大概率就需要工具。

所以：

> **工具不是每次都会用，而是在模型判断有必要时才用。**

---

## 13. 为什么有时模型会用错工具？

常见原因有：

### 13.1 工具命名太烂
名字起得不清楚。

### 13.2 描述太模糊
模型分不清每个工具的边界。

### 13.3 工具职责重叠
比如同时存在：
- `search_notes`
- `find_notes`
- `query_notes`

但三者描述差不多，模型就容易摇摆。

### 13.4 参数设计不好
参数名太抽象，模型不容易正确填。

### 13.5 客户端没有把工具信息传好
有些客户端对工具调用支持没那么成熟，也会影响效果。

---

## 14. 从工程角度看，MCP 最核心的价值是什么？

我觉得是这三个：

### 14.1 解耦
- 工具开发者写 Server
- 客户端开发者做 Client
- 模型只负责推理和决策

### 14.2 标准化
同一个 MCP Server，理论上可以被多个支持 MCP 的客户端接入。

### 14.3 动态扩展
客户端不需要把所有工具都内置死，可以运行时动态加载外部能力。

这就是为什么 MCP 这套东西越来越多人在用。

---

## 15. 用你这个仓库举个“完整现实例子”

比如一个支持 MCP 的 AI 客户端接入了本项目。

用户说：

> 帮我保存一条笔记，标题是“明天计划”，内容是“继续学 MCP 和 Agent”

这时候：

### 客户端已知可用工具
- `save_note`
- `init_notes_db`
- `insert_note`
- `list_notes`
- `search_notes`

### 模型推理
- 用户是在“保存结构化笔记”
- `insert_note` 比 `save_note` 更适合
- 因为 `insert_note` 明显对应 SQLite 笔记库

### 工具调用
客户端向 MCP Server 发起：

```json
{
  "tool_name": "insert_note",
  "arguments": {
    "title": "明天计划",
    "content": "继续学 MCP 和 Agent"
  }
}
```

### Server 执行
Python 函数插入 SQLite 数据库。

### 返回结果
```text
Inserted note: 明天计划
```

### 模型组织自然语言
> 好，已经帮你存进本地笔记库了：明天计划。

这就是一个从自然语言到结构化工具调用，再回到自然语言回复的闭环。

---

## 16. 你可以把 MCP 粗暴类比成什么？

给你几个不那么严谨但很好懂的类比：

### 类比 1：USB 接口
- 设备很多种
- 但插口标准化
- 客户端接不同工具不用每次重新发明轮子

### 类比 2：函数调用的远程版说明书
- 工具像函数
- MCP 像函数说明书 + 调用协议
- 客户端负责转发调用

### 类比 3：AI 的插件总线
- 模型像大脑
- 客户端像神经系统
- MCP Server 像外接器官

虽然类比都不完美，但够你抓住核心了。

---

## 17. 新手最容易误解的点

### 误解 1：MCP = 大模型自己会调用系统命令
不对。
通常是客户端/运行时代表模型执行。

### 误解 2：模型直接读 Python 源码来决定调用
不对。
模型通常看到的是“工具描述和参数 schema”，不是你的源码细节。

### 误解 3：MCP 一定是 HTTP API
不对。
很多最常见的是 stdio 模式。

### 误解 4：只要暴露工具，模型就一定会调用
不对。
模型会先判断有没有必要。

### 误解 5：MCP 很复杂，所以必须先懂协议全文档
也不对。
新手完全可以先：
- 跑一个最小 server
- 加一个工具
- 接一个客户端
- 看一次真实调用

先会用，再慢慢往协议底层钻。

---

## 18. 站在你现在这个项目上，真正要记住的核心

如果你只想记住最重要的几句话，记这几句就够了：

### 核心 1
**你在 Python 里写的函数，通过 MCP 被包装成“AI 可调用工具”。**

### 核心 2
**AI 模型并不是直接执行代码，而是先根据工具说明做选择。**

### 核心 3
**MCP Client 负责启动 Server、发现工具、转发调用、回传结果。**

### 核心 4
**完整链路是：用户提需求 → 模型决定用工具 → 客户端代为调用 → Server 执行 → 结果回给模型 → 模型回复用户。**

把这 4 句吃透，MCP 你就已经不是门外汉了。

---

## 19. 如果你想把这个 MCP 接到 OpenCode，该怎么做？

你问的这个很实际。

如果目标是把本项目接到 **OpenCode**，核心不是改 MCP 协议本身，而是：

1. 让你的 Python MCP Server 能本地启动
2. 在 OpenCode 配置里把它注册成一个 `local` MCP server
3. 让 OpenCode 启动它、发现工具、再把工具提供给模型

### 19.1 OpenCode 官方文档里怎么定义 MCP 配置？

根据 OpenCode 官方文档，MCP server 是放在配置文件里的 `mcp` 字段下。

官方文档：
- OpenCode MCP servers: <https://opencode.ai/docs/mcp-servers/>
- OpenCode Config: <https://opencode.ai/docs/config/>
- OpenCode CLI: <https://opencode.ai/docs/cli/>

OpenCode 文档说明了：
- 可以配置 **local** MCP server
- 也可以配置 **remote** MCP server
- 配好后，MCP tools 会自动和内建工具一起提供给 LLM

官方文档里有一句很关键的话，意思基本是：

> **一旦加入，MCP tools 会自动和内建工具一起提供给 LLM。**

这句话直接回答了一个核心问题：

> 在 OpenCode 里，模型之所以“知道有这个工具”，不是因为模型读了你的仓库，而是因为 OpenCode 把 MCP Server 发现到的工具清单提供给了模型。

### 19.2 OpenCode 配置文件一般放在哪里？

根据 OpenCode Config 文档，常见位置有：

- 全局配置：`~/.config/opencode/opencode.json`
- 项目配置：项目根目录下的 `opencode.json`

而且文档说配置是按优先级合并的，不是简单替换。

对新手来说，最简单的做法一般是：
- 先用项目级 `opencode.json`
- 这样最直观，也不容易把全局环境搞乱

### 19.3 一个接入本项目的本地 OpenCode 配置例子

假设你的项目路径是：

```text
/absolute/path/to/beginner-python-mcp
```

并且你已经装好了虚拟环境，那么一个很直白的 OpenCode 配置示例可以写成：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "beginner-python-mcp": {
      "type": "local",
      "command": [
        "/absolute/path/to/beginner-python-mcp/.venv/bin/python",
        "-m",
        "beginner_python_mcp.server"
      ],
      "enabled": true
    }
  }
}
```

这段配置的意思是：
- 在 OpenCode 里注册一个 MCP server
- 名字叫 `beginner-python-mcp`
- 它是本地类型 `local`
- 启动方式是运行你的 Python 模块
- OpenCode 启动时会尝试连接它并拉取工具定义

### 19.4 也可以用 OpenCode 自带命令添加

OpenCode CLI 文档里也提供了：

```bash
opencode mcp add
```

以及：

```bash
opencode mcp list
```

这两个命令分别适合：
- 添加 MCP server
- 检查当前 MCP server 是否配置成功、连接是否正常

### 19.5 在 OpenCode 里模型怎么知道要用哪个工具？

结合 OpenCode 的 MCP 文档，可以把链路理解成：

1. OpenCode 读取 `opencode.json`
2. 发现你配置了 `beginner-python-mcp`
3. OpenCode 启动这个本地命令
4. OpenCode 通过 MCP 拿到工具列表
5. OpenCode 把这些工具和内建工具一起交给 LLM
6. 模型根据用户问题，决定是否要调用某个工具
7. 如果模型决定调用，OpenCode 再去执行 MCP tool
8. 工具结果返回后，OpenCode 再把结果交给模型组织最终回答

所以在 OpenCode 语境下：

> **模型“知道要用哪个工具”，本质上还是因为 OpenCode 已经把工具列表、描述、参数 schema 提供给它了。**

### 19.6 一个比较完整的 OpenCode 使用案例

下面给你一个“完整但不花哨”的案例。

#### 步骤 1：先确保你的 MCP server 可以本地运行

```bash
cd beginner-python-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m beginner_python_mcp.server
```

如果系统缺少 `venv`，先安装 `python3-venv`。

#### 步骤 2：在项目里写 `opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "beginner-python-mcp": {
      "type": "local",
      "command": [
        "/absolute/path/to/beginner-python-mcp/.venv/bin/python",
        "-m",
        "beginner_python_mcp.server"
      ],
      "enabled": true
    }
  }
}
```

#### 步骤 3：检查 OpenCode 是否识别到它

可以参考官方 CLI：

```bash
opencode mcp list
```

如果配置没问题，你应该能看到这个 MCP server 在列表里。

#### 步骤 4：实际给模型一个任务

比如你在 OpenCode 里问：

> 帮我初始化笔记库，然后记一条标题为“学习 MCP”、内容为“今天把 OpenCode 接上了”的笔记

此时，一个理想链路大概会是：
- 模型先决定调用 `init_notes_db`
- 再调用 `insert_note`
- OpenCode 执行这两个 MCP tool
- 模型最后告诉你已经完成

这就是“本地 Python MCP 接入 OpenCode”的一个完整闭环。

### 19.7 一个额外提示：在提示词里显式提 MCP 名称，往往更稳

OpenCode 的 MCP 文档里多次用了这种写法：

- `use context7`
- `use the gh_grep tool`

这说明在 OpenCode 里，**你可以在 prompt 里显式点名某个 MCP / tool**，帮助模型更稳定地选择工具。

所以如果你接了自己的 MCP，有时可以这样提示：

> use the beginner-python-mcp tools to store and search notes

或者更自然一点：

> 用 beginner-python-mcp 里的 SQLite 笔记工具来完成这个任务

这不是强制要求，但在工具比较多时，会更稳一些。

---

## 20. 你接下来最值得做的实验

建议你亲手做下面这几个实验，理解会飞快上来：

### 实验 1：改工具描述
把 `insert_note` 的描述改得更清晰，再观察模型选工具是否更稳定。

### 实验 2：故意设计两个很像的工具
比如：
- `search_notes`
- `find_notes`

然后观察模型会不会选错。

### 实验 3：新增一个 `delete_note(id)`
看看模型在“删除一条笔记”这种任务里会不会正确使用它。

### 实验 4：接入一个真实客户端
亲眼看一次“用户自然语言 -> 工具被调用 -> 结果返回”的完整链。

这比看十篇概念文章都强。

---

## 20. 最后一句大白话总结

MCP 这玩意儿，说到底就是：

> **你把程序能力按标准方式暴露出来，客户端把这些能力介绍给模型，模型决定什么时候用，客户端替它执行，然后再把结果还给模型。**

所以它不是魔法。

它只是把“AI 调工具”这件事，做成了标准件。
