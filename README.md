# Paper-assistance-tools
前端：http://localhost:5173/

swagger: http://localhost:5173/swagger

数据库:mysql+pymysql://root:123456@localhost:3306/paper_system

    一、后端（Flask）分层解析（backend 目录）

遵循分层架构（或类 MVC 后端拆分），各目录职责：

models：定义数据模型（如 SQLAlchemy 模型类 ），对应 MVC 中 Model，描述数据库表结构、数据关联。

dao（Data Access Object）：数据访问层，封装数据库操作（如增删改查 SQL 执行 ），解耦业务逻辑与数据库细节，让 service 无需关心底层存储实现。

service：业务逻辑层，处理核心业务规则（如数据校验、复杂计算、调用 dao 交互数据库 ），是后端 “大脑”，对应 MVC 中 Controller 的部分逻辑（但更聚焦业务 ）。

controller：路由 / 控制层，定义 API 路由（如 /api/user ），接收前端请求、解析参数，调用 service 处理，返回 JSON 数据，对应 MVC 中 Controller 接收请求、调度业务的职责。

config：存放配置（如数据库连接、环境变量 ），统一管理环境相关参数。
app.py：Flask 应用入口，初始化 Flask 实例、加载配置、注册路由（或蓝图 ），串联后端各层。

    二、前端（Vue + Vite + TypeScript）分层解析（frontend 目录）

遵循Vue 生态的组件化 + 路由分层架构，各目录职责：

views：存放页面级组件（如 HomeView.vue、UserView.vue ），对应 MVC 中 View，负责页面整体布局与逻辑，通过 Vue Router 配置路由，实现多页面（路由）跳转。

components：通用 UI 组件（如 Button.vue、Table.vue ），复用性强，被 views 或其他组件嵌套调用，是构成 View 的 “原子部件”。

router：配置 Vue Router，定义页面路由规则（如 /home 对应 HomeView ），实现前端路由跳转，让单页应用（SPA）可模拟多页体验。

src：一般存放前端业务代码（若有进一步拆分，如 store 用于状态管理、api 封装接口请求 ），当前目录结构里虽未展开，但属于 Vue 项目标准扩展目录。

App.vue：根组件，定义前端应用整体布局（如导航栏、页脚、路由出口 ），是所有页面组件的 “容器”。

main.ts/main.js：前端入口文件，初始化 Vue 实例、加载全局配置（如插件、样式 ）、挂载根组件到 DOM，启动前端应用。


第一版迭代已经实现了基本的论文管理系统，包括用户登录、注册、论文查重和主题提取等功能。管理员操作也基本实现

第二版主要是优化界面，论文查重时论文的对比，高亮，主题提取的导出功能