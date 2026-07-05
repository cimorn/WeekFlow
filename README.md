[English](docs/README.en.md)

# WeekFlow

WeekFlow 是一个本地桌面周报工具。打开软件，选择 `data` 里的文件，按页面填写，最后得到一份 Markdown 周报。

## 下载安装

下载：[`WeekFlow-V26.07.04.zip`](https://github.com/cimorn/WeekFlow/releases/download/latest/WeekFlow-V26.07.04.zip)

解压后运行文件夹里的 `WeekFlow-V26.07.04.exe`。不要把 exe 单独拖出来运行，它需要同目录的 `resources`、`locales`、dll 和 `data`。

## 1. 打开或新建周报

启动后先进入文件页。可以打开 `data` 里的已有周报，也可以新建一份。

<p>
  <img src="https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/01-home.png" alt="首页：选择 data 文件或新建周报" width="900">
</p>

新建后会自动生成同名文件夹：

```text
data/
  demo-community/
    demo-community.json
    demo-community.md
    figs/
```

`json` 是可继续编辑的数据，`md` 是导出的周报，`figs` 放项目图片。

## 2. 填写基本信息

在“基本信息”里填写标题和总结。AI 是可选的；需要时填 `Base URL`、`API Key`、`Model / Endpoint`，再点“测试 AI”。

<p>
  <img src="https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/04-basic-ai.png" alt="基本信息与 AI 接入" width="900">
</p>

阿里百炼常用 OpenAI 兼容地址：

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

如果用业务空间专属地址，把 `{WorkspaceId}` 换成真实业务空间 ID。

## 3. 写本周成果和感受

“成果感受”分成左右两块：左边写本周成果，右边写本周感受。AI 润色只放在感受这里。

<p>
  <img src="https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/02-results.png" alt="成果感受页面" width="900">
</p>

## 4. 管理项目进展

先在左侧选择项目，再切换“查看项目 / 填写进展 / 记录结果 / 时间流水”。结果图片会保存到该周报文件夹的 `figs` 里。

<p>
  <img src="https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/03-projects.png" alt="项目进展页面" width="900">
</p>

## 5. 预览周报

“预览”里左边是 Markdown，右边是渲染效果。也可以点顶部“独立预览”打开单独窗口。

<p>
  <img src="https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/05-preview.png" alt="Markdown 与渲染预览" width="900">
</p>

## 6. 保存和备份

- 点顶部“保存”会同时更新 `json` 和 `md`。
- 首页的“导出备份”会打包当前 `data` 数据。
- 软件只允许打开一个主窗口；重复打开 exe 会回到已打开的窗口。

## 许可

[MIT License](LICENSE)
