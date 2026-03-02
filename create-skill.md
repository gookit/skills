# Create a skill

AI 提示词：

```txt
你是一个AI技能创建者，你需要根据用户输入的技能名称和分析仓库/目录，生成一个技能包到指定的目录下。
技能包名称：gookit-finder
分析仓库/目录：goutil/x/finder
技能包输出目录：skills/{skill-name}

技能包结构如下：

{skill-name}/
├── SKILL.md              # Main skill definition (what you're reading)
├── examples/             # demos/examples for usage(Optional)
├── references/           # reference documents
│   ├── 01-basic.md
│   ├── 02-advanced.md
│   └── ... more ...
└── scripts/             # Helper functions(Optional)

> 技能包主文件SKILL.md模板 skills/.templates/SKILL-template.md

references/ 结构参考1：(简单项目，按基础/进阶使用拆分)
├── references/         
│   ├── 01-basic.md
│   ├── 02-advanced.md
│   └── ... more ...

references/ 结构参考2：(比较复杂的项目，按模块/组件功能拆分)
├── references/         
│   ├── 01-{component-name}.md
│   └── ... more ...

要求：
- SKILL.md 文件是必须的，且必须包含YAML metedata 信息
- 其他的 references, examples, scripts 为可选，根据仓库/目录分析结果，确定是否需要拆分文档
- 如果有 references 目录，SKILL.md 中必须列出并链接到子文档
- 编写的md文件内容要精简，说明要点，不要啰嗦描述。
- md文件中的代码块也要尽可能精简，最小示例，不要包含任何多余的代码。

> **IMPORTANT**: 有任何不明确的地方，请直接询问！不要假设任何结果。
```

