[中文](../README.md)

# WeekFlow

WeekFlow is a local desktop app for writing structured weekly reports. Open a file from `data`, fill in each page, and export a Markdown report.

## Download

Download [`WeekFlow-V26.07.04.zip`](https://github.com/cimorn/WeekFlow/releases/download/latest/WeekFlow-V26.07.04.zip).

Extract the whole archive and run `WeekFlow-V26.07.04.exe` from that folder. Do not move the exe out by itself; it needs the nearby `resources`, `locales`, dll files, and `data`.

## 1. Open Or Create A Report

The start page opens first. Choose an existing report from `data`, or create a new one.

<p>
  <img src="https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/01-home.png" alt="Home page for opening or creating a report" width="900">
</p>

Creating a report also creates its folder:

```text
data/
  demo-community/
    demo-community.json
    demo-community.md
    figs/
```

`json` is the editable data, `md` is the exported report, and `figs` stores project images.

## 2. Fill In Basic Info

Use Basic Info for the title and summary. AI is optional; fill in `Base URL`, `API Key`, and `Model / Endpoint`, then test the connection.

<p>
  <img src="https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/04-basic-ai.png" alt="Basic info and AI setup" width="900">
</p>

Common Alibaba Cloud Model Studio OpenAI-compatible endpoint:

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

For workspace-specific endpoints, replace `{WorkspaceId}` with the real workspace ID.

## 3. Write Results And Feelings

Results and feelings are on one page: results on the left, feelings on the right. AI polishing is only used for feelings.

<p>
  <img src="https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/02-results.png" alt="Results and feelings page" width="900">
</p>

## 4. Manage Project Progress

Choose a project first, then switch between View Project, Write Progress, Record Result, and Timeline. Project images are saved in the report's `figs` folder.

<p>
  <img src="https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/03-projects.png" alt="Project progress page" width="900">
</p>

## 5. Preview The Report

Preview shows Markdown on the left and the rendered report on the right. Use Independent Preview to open it in a separate window.

<p>
  <img src="https://raw.githubusercontent.com/cimorn/WeekFlow/main/docs/screenshots/05-preview.png" alt="Markdown and rendered preview" width="900">
</p>

## 6. Save And Back Up

- Save updates both `json` and `md`.
- Export Backup packages the current `data` folder.
- Only one main window can run at a time. Starting the exe again focuses the existing window.

## License

[MIT License](../LICENSE)
