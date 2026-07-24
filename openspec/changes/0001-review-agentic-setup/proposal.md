# Change: Review and refine agentic setup

## Status
Archived (completed)

## Why
Exercise 4 の "hello, world" タスクとして、コーディングエージェント用の
設定一式(`AGENTS.md`、スキル選定、OpenSpecディレクトリ構成)が実際に
機能するかをレビューし、不足を補う。

## What changes
- `AGENTS.md` に、テストを書かずに完了報告しないこと・コミットメッセージ
  にIssueクローズキーワードを含めることを明記。
- `openspec/project.md` にプロジェクト仕様(データモデル・主要機能・
  技術スタック)を集約し、以後の feature 提案から参照できるようにする。
- CI(`.github/workflows/ci.yml`)を追加し、lint・test・coverageを
  push/PRごとに自動実行するようにする(Exercise 5 note の
  「自動化されたコードレビュー/チェック」の一環)。

## Impact
- Affected specs: `project.md`(新規)
- Affected code: `AGENTS.md`, `.github/workflows/ci.yml`
- 破壊的変更なし
