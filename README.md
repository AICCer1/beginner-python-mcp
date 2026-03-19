# beginner-python-mcp

一个给新手准备的 **Python MCP（Model Context Protocol）** 示例仓库。

> 用 Python 写一个可以本地部署的 MCP Server，让 AI Agent 能像调用函数一样使用你的工具。

## 适合谁？

这个仓库适合：
- 第一次接触 MCP 的人
- 想自己做一个本地工具给 AI 用的人
- 想学 Python + MCP 最小可用项目的人

## 这个项目现在能做什么？

### 基础示例工具
- `hello(name)`：返回问候语
- `add(a, b)`：两个数字相加
- `now(mode)`：返回当前 UTC 时间
- `save_note(filename, content)`：把内容保存到本地 `data/` 目录

### 真实一点的本地工具：SQLite 笔记库
- `init_notes_db()`：初始化本地 SQLite 数据库
- `insert_note(title, content)`：插入一条笔记
- `list_notes(limit)`：列出最近的笔记
- `search_notes(keyword, limit)`：按关键词搜索笔记

### 其他 MCP 能力示例
- `resource: guide://intro`
- `prompt: teaching_prompt(goal)`

---

## 项目结构

```text
beginner-python-mcp/
├─ docs/
│  └─ MCP_FULL_CHAIN.md
├─ pyproject.toml
├─ README.md
├─ .gitignore
└─ src/
   └─ beginner_python_mcp/
      ├─ __init__.py
      └─ server.py
```

核心文件：
- `src/beginner_python_mcp/server.py`
- `docs/MCP_FULL_CHAIN.md`：详细解释 MCP 的定义、加载方式、工具选择逻辑和完整调用链

---

## 一分钟理解 MCP

你可以把 MCP 理解成：

> **AI 调用外部工具的标准接口。**

角色大概是这样：
- **MCP Server**：提供工具
- **MCP Client**：让 AI 连接这些工具
- **Tool**：执行动作，比如查数据、写文件、访问数据库
- **Resource**：提供可读取内容
- **Prompt**：提供可复用提示模板

这个仓库就是一个：

> **本地运行的 Python MCP Server**

---

## 快速开始

### 1）进入项目目录

```bash
cd beginner-python-mcp
```

### 2）创建虚拟环境

```bash
python3 -m venv .venv
```

### 3）激活虚拟环境

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4）安装依赖

```bash
pip install -e .
```

### 5）启动 MCP Server

```bash
python -m beginner_python_mcp.server
```

或者：

```bash
beginner-python-mcp
```

> 说明：很多 MCP Server 默认通过 **stdio** 和客户端通信，不会像 Web 服务一样给你打印一个访问地址。这是正常现象。

---

## 如何接到 AI Agent / MCP Client

不同客户端配置格式略有区别，但核心都一样：

告诉客户端启动这个命令，把它当作一个 MCP Server。

### 通用配置示例

```json
{
  "mcpServers": {
    "beginner-python-mcp": {
      "command": "/absolute/path/to/beginner-python-mcp/.venv/bin/python",
      "args": ["-m", "beginner_python_mcp.server"]
    }
  }
}
```

或者：

```json
{
  "mcpServers": {
    "beginner-python-mcp": {
      "command": "/absolute/path/to/beginner-python-mcp/.venv/bin/beginner-python-mcp"
    }
  }
}
```

### 新手最容易踩的坑

1. **尽量用绝对路径**
2. **尽量用虚拟环境里的 Python**
3. **客户端连接的是命令，不是目录**
4. **确认客户端本身真的支持 MCP**

---

## SQLite 版工具教学

这部分是这个仓库里最接近“真实可用”的示例。

为什么我推荐新手先学 SQLite 版？
- 本地就能跑
- 不依赖 API key
- 不需要联网
- 数据能真实保存下来
- 很像 AI Agent 实际调用工具的场景

### 它做了什么？

这个项目会把数据写到：

```text
./data/notes.db
```

也就是项目目录下的 SQLite 数据库文件。

### 你可以这样理解这几个工具

#### `init_notes_db()`
初始化数据库和表。

#### `insert_note(title, content)`
插入一条笔记，比如：
- 标题：`学习 MCP`
- 内容：`今天先学会怎么让 AI 调本地工具`

#### `list_notes(limit)`
列出最近几条笔记。

#### `search_notes(keyword, limit)`
按关键词搜索笔记内容。

---

## 一个最小学习流程

如果你是第一次接触 MCP，我建议你按这个顺序走。

### 第一步：先把服务跑起来
先确认它能启动，别一开始就纠结所有细节。

### 第二步：让 AI 调一次 `hello()`
感受一下“工具被调用”的感觉。

### 第三步：初始化 SQLite
让 AI 调：
- `init_notes_db()`

### 第四步：插入几条数据
让 AI 调：
- `insert_note("学习计划", "先会跑，再会改，再会扩展")`
- `insert_note("MCP 理解", "MCP 就是让 AI 用标准方式调用工具")`

### 第五步：查询结果
让 AI 调：
- `list_notes()`
- `search_notes("MCP")`

到这一步，你就已经不是在看概念，而是在真正用一个 MCP 工具了。

---

## server.py 代码怎么理解？

### 1）创建 MCP 实例

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("beginner-python-mcp")
```

这表示你创建了一个 MCP Server，并给它取了名字。

### 2）暴露工具

```python
@mcp.tool()
def add(a: float, b: float) -> float:
    return a + b
```

这表示：
- 这是一个工具
- AI 可以看到它
- AI 可以按参数调用它

### 3）用 SQLite 做真实持久化

这个项目里新增了 SQLite 逻辑：
- 先连接 `data/notes.db`
- 如果表不存在就创建
- 然后可以插入、列出、搜索数据

这比只返回一句 `hello world` 更像真实业务。

---

## 怎么新增你自己的工具？

比如你要加一个乘法工具：

```python
@mcp.tool()
def multiply(a: float, b: float) -> float:
    return a * b
```

如果你要加一个删笔记工具，也完全可以照着 SQLite 示例继续写。

---

## 为什么 `save_note` 和 SQLite 都写到 `data/`？

因为这是新手项目，我故意做了一个相对安全的收口：
- 文件和数据库都在本项目目录内
- 不让工具乱写系统里的别的地方
- 更容易观察、调试、清理

这种设计对新手很友好，也更安全。

---

## 常见问题

### Q1：为什么启动后像“卡住了”？
不是卡住。很多 MCP Server 默认走 stdio，没有 Web 地址和欢迎页面。

### Q2：AI 客户端连不上怎么办？
先检查：
1. 路径是不是绝对路径
2. 是否用的是虚拟环境 Python
3. 模块名是不是 `beginner_python_mcp.server`
4. 客户端是否支持 MCP

### Q3：创建虚拟环境时报 `ensurepip is not available` 怎么办？
Debian / Ubuntu 常见原因是没装 `python3-venv`。

可尝试：

```bash
sudo apt install python3-venv
```

或者特定版本：

```bash
sudo apt install python3.12-venv
```

### Q4：我能不能做成 HTTP / SSE 版本？
能，但新手先把 stdio 跑通，别一上来给自己上强度。

### Q5：MCP 和普通 Python 脚本到底差在哪？
普通脚本是你手动运行。
MCP Server 是 AI 客户端按协议来调用。

---

## 后续建议

你把这个仓库跑通以后，可以继续往这几个方向升级：

### 方向 1：接外部 API
比如天气、翻译、企业内部接口。

### 方向 2：读本地知识库
比如 Markdown、PDF、SQLite。

### 方向 3：做安全控制
比如：
- 目录白名单
- 参数校验
- 审计日志
- 读写权限拆分

### 方向 4：补客户端专用配置
比如：
- Claude Desktop
- Cursor
- Cline
- Cherry Studio
- OpenClaw

---

## 一句话总结

这个仓库做的事就是：

> **用 Python 写一个本地 MCP Server，并给它接上真正能用的 SQLite 工具，让 AI Agent 可以直接调用。**

不神秘，本质上就是：
- 写函数
- 用 MCP 暴露出去
- 让 AI 客户端来调

---

## 深入理解 MCP 的完整链路

如果你想认真弄明白下面这些问题：
- MCP 是怎么定义工具的
- 客户端是怎么加载 MCP Server 的
- AI 模型为什么知道该选哪个工具
- 一次工具调用完整经历了什么流程

直接看：

- `docs/MCP_FULL_CHAIN.md`

这份文档是给新手写的，讲的是“从概念到调用链”的完整过程，不只是贴几个名词糊弄你。

---

## 下一步你可以怎么学

如果你想继续，我建议下一步做这三件事中的一个：

1. 给这个仓库补 **Claude / Cursor / OpenClaw 的配置示例**
2. 再加一个 **SQLite 删除 / 更新工具**
3. 加一个 **GitHub Actions 自动检查**

你一句话，我继续往上搭。