# ハーネスエンジニアリング極地構成における営業管理ダッシュボード完全自律運用ベストプラクティス

## 0. ゴール定義（「人の手を入れない」を分解）

「完全自律」は1つではなく、以下をすべて機械化することを指す。

1. **構築自動化**: 要件→設計→実装→テスト→デプロイが自動。
2. **運用自動化**: 監視→異常検知→復旧→報告が自動。
3. **保守自動化**: 依存更新・脆弱性修正・データ品質改善が自動。
4. **拡張自動化**: 新KPI・新画面・新連携を仕様駆動で自動追加。
5. **統制自動化**: 監査証跡・権限・コンプライアンス判定が自動。

このため、単なるCI/CDではなく、**「仕様を唯一の真実源（SoT）にする宣言的プラットフォーム」**が前提。

---

## 1. 参照アーキテクチャ（4層 + 制御プレーン）

### 1.1 データ層（Data Plane）
- CRM（Salesforce/HubSpot等）、SFA、MA、会計、CSツールからCDCで収集。
- Lakehouse（Delta/Iceberg）へRaw→Staging→Martの3層。
- `dbt` でKPI定義・次元管理（顧客、案件、担当、商材、期間）をコード化。
- データ契約（Data Contract）でスキーマ変更を事前検知。

### 1.2 アプリ層（App Plane）
- ダッシュボードは**メタデータ駆動UI**（例: JSON Schema + component registry）。
- KPIカード・ファネル・予実比較・案件ヒートマップを部品化。
- 権限はRBAC + ABAC（組織、役職、担当範囲）をOPAで一元判定。

### 1.3 実行層（Execution Plane）
- ワークフローはArgo Workflows / TemporalでDAG化。
- IaC（Terraform） + GitOps（Argo CD/Flux）で環境差分を廃止。
- すべてのジョブは冪等・再実行可能・タイムアウト/リトライ標準化。

### 1.4 品質層（Quality Plane）
- テストピラミッド:
  - データ: `dbt test` + Great Expectations
  - API: 契約テスト（OpenAPI + schemathesis）
  - UI: Playwright E2E（主要業務シナリオ）
- SLO: 可用性、データ鮮度、クエリレイテンシ、誤集計率。

### 1.5 制御プレーン（Control Plane）
- **Policy as Code**: OPA/Regoで「デプロイ可否」「PII列公開可否」「権限逸脱」を自動判定。
- **Observability as Code**: OpenTelemetry + Prometheus + Grafana + Alertmanager。
- **Runbook as Code**: 異常時手順を機械実行（auto-remediation）可能な形式で保持。

---

## 2. ハーネスエンジニアリングの“極地”設計原則

1. **Everything-as-Code**
   - Infra / Data model / KPI定義 / 権限 / 監視 / Runbook / ドキュメントすべてGit管理。
2. **Spec-first + Codegen**
   - 要件はDSL（YAML/JSON）で定義し、API・UI・テストを自動生成。
3. **Golden Path**
   - 例外を減らす標準雛形（新KPI追加テンプレート、新データソース連携テンプレート）を提供。
4. **Progressive Delivery**
   - Feature flag、canary、shadow trafficで安全に段階展開。
5. **Autonomous Guardrails**
   - 「自由な開発」ではなく「逸脱不可の自動ガード」で無人運用を成立させる。

---

## 3. 構築フェーズ完全自動化（Build Autonomy）

### 3.1 要件入力を機械可読化
- `sales_dashboard_spec.yaml` に以下を宣言:
  - KPI定義（計算式、粒度、更新頻度、責任者）
  - 画面構成（ウィジェット、フィルタ、ドリルダウン）
  - 権限制御（誰が何を見られるか）
  - 非機能要件（SLO、RTO/RPO、監査要件）

### 3.2 パイプライン自動生成
- Spec変更を契機にCIが以下を生成:
  1. dbtモデル雛形
  2. APIスキーマとサーバスタブ
  3. UIコンポーネント設定
  4. 単体/統合/E2Eテストケース
  5. 監視ルールとダッシュボード

### 3.3 品質ゲート（マージ不可ルール）
- すべてのゲート通過を必須化:
  - セキュリティ（SAST/DAST/依存脆弱性）
  - データ品質（Null率・重複率・整合性）
  - 性能（主要クエリP95閾値）
  - コスト（クエリ単価・日次予算上限）

### 3.3.1 レビュー完全自動化（AI + ルールエンジン）
- PRレビューを以下の3段で自動化し、**人間レビューを必須要件から外す**:
  1. 静的レビュー（Lint/型/規約/秘密情報混入検知）
  2. 意味レビュー（変更差分とSpec整合、KPI定義逸脱、権限逸脱）
  3. リスクレビュー（本番影響度、ロールバック容易性、監査要件）
- AIレビューは提案のみ許可し、**最終判定はPolicy as Code**で機械決定。
- 「レビュー承認 = すべてのゲート署名が揃った状態」と定義し、承認操作を廃止。

### 3.4 デプロイ戦略
- 本番前にephemeral環境で実データ縮小サンプルにより自動検証。
- Green/Blue + Canaryで段階配信。
- 異常検知時は自動ロールバック + インシデント記録自動作成。

---

## 4. 保守フェーズ完全自動化（Operate & Maintain Autonomy）

### 4.1 自動監視
- 監視対象:
  - ETL遅延
  - KPI異常（統計的異常検知）
  - ダッシュボード遅延
  - 権限逸脱アクセス
- すべてSLOベースのアラートしきい値をコード管理。

### 4.2 自動復旧（Self-healing）
- 典型的な復旧アクションをRunbook化:
  - 失敗ジョブ再実行
  - キュー詰まり解消
  - キャッシュ再構築
  - スケールアウト
- 実行結果を監査ログに自動保存。

### 4.3 自動更新
- Dependabot/Renovateで依存更新PRを自動作成。
- 互換性テスト・性能リグレッションを通過したもののみ自動マージ。
- 重大CVEは優先パイプラインで即時パッチ適用。

### 4.4 コスト最適化自動化
- クエリプラン監視と高コストSQLの自動提案（or自動修正PR）。
- 利用頻度の低いマートは自動で更新頻度を落とす。
- 予算逸脱予兆で自動スロットリング。

---

## 5. 機能拡張フェーズ自動化（Evolve Autonomy）

### 5.1 拡張を「プラグイン化」
- 新機能は以下の最小単位で追加:
  - `kpi_plugin`
  - `widget_plugin`
  - `datasource_plugin`
- 各プラグインは契約（interface）に準拠させ、CIで互換性判定。

### 5.2 生成AIを組み込む場合の安全策
- LLMは**提案役**、最終適用はPolicyエンジン承認後に限定。
- Prompt/Outputを監査ログ化。
- KPI計算ロジックなど高リスク領域はLLM直書きを禁止し、テンプレート生成のみに制約。

### 5.3 A/Bと効果測定の自動化
- 新画面・新指標はFeature Flag配下でリリース。
- 採用判定指標（利用率、滞在時間、意思決定速度）を自動集計。
- 閾値未達は自動で停止・撤回。

---

## 6. 体制設計（無人化に必要な最小の人間関与）

完全無人に近づけるには、日常運用ではなく**ルール設計**に人を寄せる。

- 人が担うべき最小タスク:
  1. 事業ルール更新（四半期）
  2. ポリシー変更承認（法令/監査対応）
  3. 重大障害後のポストモーテム承認
- それ以外（実装・検証・展開・復旧）は自動化対象。

---

## 7. 導入ロードマップ（90日）

### Phase 1（Day 1-30）基盤化
- 現行KPIとデータフロー棚卸し。
- Specフォーマット策定。
- IaC + GitOps + 観測基盤の最小構成導入。

### Phase 2（Day 31-60）自動化強化
- Spec→生成パイプライン構築。
- 品質ゲート（セキュリティ/性能/データ品質）実装。
- 自動復旧Runbookの上位10シナリオ実装。

### Phase 3（Day 61-90）自律化完成
- 依存更新自動マージ条件整備。
- 拡張プラグイン方式導入。
- SLO運用とコスト最適化の自動制御を有効化。

---

## 8. 失敗しやすいポイントと回避策

1. **最初からAIに任せすぎる**
   - 回避: 先にSpec/Policy/契約テストを固める。
2. **データ定義が曖昧**
   - 回避: KPI辞書・データ契約を先に整備。
3. **例外運用が増える**
   - 回避: Golden Path外の変更を原則禁止、必要なら先に標準化。
4. **監視がアラート過多**
   - 回避: SLO連動・ノイズ削減ルールを実装。

---

## 9. 実装テンプレート（最小）

- リポジトリ構成例:
  - `spec/`（KPI, UI, Policy仕様）
  - `data/`（dbt models/tests）
  - `app/`（API/UI generated + custom plugins）
  - `ops/`（Terraform, ArgoCD, monitoring, runbooks）
  - `.github/workflows/`（quality gates + deploy）

- ブランチ戦略:
  - `main` 保護
  - すべてPR経由
  - 自動生成コミットはBot署名

- KPI変更フロー:
  1. `spec/kpi/*.yaml`更新
  2. CIがモデル/API/UI/テストを再生成
  3. ゲート通過後に自動リリース

---

## 10. 結論（実務での最適解）

営業管理ダッシュボードを「構築〜保守〜拡張」まで無人に近づける最適解は、
**人がアプリを直接作る運用をやめ、仕様・ポリシー・ガードレールを作る運用へ転換すること**。

その中核は以下の3点:
- **Spec-first（要件の機械可読化）**
- **Policy as Code（逸脱不可の自動統制）**
- **Self-healing + GitOps（運用の自律化）**

加えて、レビュー工程まで無人化するために、**Review as Code（レビュー基準と承認判定のコード化）**を標準化する。

この3点を揃えることで、ハーネスエンジニアリングの極地構成として、
「人が触らなくても壊れず進化し続ける営業管理ダッシュボード」に現実的に到達できる。

---

## 11. PR運用テンプレート（日本語標準）

自律運用でも監査可能性を担保するため、PR本文は日本語で以下の固定構成を推奨する。

1. 背景（なぜ変更が必要か）
2. 変更内容（何をどう変えたか）
3. 影響範囲（データ、API、UI、運用）
4. 検証結果（実行コマンドと結果）
5. ロールバック手順（失敗時の戻し方）

このテンプレートをリポジトリのPRチェックで必須化し、未充足の場合は自動でマージ不可にする。

---

## 12. 転用ガイド：Spring Boot + Thymeleaf + Oracle + GitLab 版ベスト構成

「このプロジェクトのハーネス思想」を Java/Spring 系へ移植する場合は、技術スタックを置換しつつ、
**Spec-first / Policy as Code / GitOps 的運用**をそのまま残すのが最適。

### 12.1 推奨リポジトリ構成（モノレポ）

- `spec/`
  - `kpi/`（KPI定義 YAML）
  - `ui/`（画面定義 YAML: ウィジェット、フィルタ、権限）
  - `policy/`（アクセス制御・公開可否ルール）
- `app/`
  - `backend/`（Spring Boot）
  - `frontend/`（Thymeleafテンプレート + Alpine.js等の最小JS）
- `data/`
  - `flyway/`（DDL・初期データ）
  - `sql/`（参照SQL、Materialized View管理）
- `ops/`
  - `gitlab-ci/`（CIテンプレ）
  - `runbooks/`（自動復旧手順）
  - `monitoring/`（Prometheus/Grafana定義）

### 12.2 アプリ設計（Spring Boot / Thymeleaf）

- Spring Bootは **Hexagonal Architecture** を推奨。
  - `domain`: KPI計算・業務ルール
  - `application`: ユースケース
  - `infrastructure`: Oracleアクセス（MyBatis/JOOQ/JPAいずれか）
  - `presentation`: Controller + Thymeleaf
- Thymeleafは「画面ロジック最小化」を徹底。
  - 表示条件は `policy` 判定結果をViewModelに反映
  - 大きな動的UIが必要な箇所のみJS強化（全面SPA化は避ける）
- DTOとEntityを分離し、レポート用途の読み取りモデルを別定義（CQRS-lite）する。

### 12.3 Oracle参照の実装原則

- OracleはOLTP直参照ではなく、**参照専用スキーマ**またはViewを介して読む。
- KPI用SQLは `data/sql/kpi_*.sql` として管理し、SQL単体テストをCIに組み込む。
- パフォーマンス基準:
  - 主要集計SQLに対し `EXPLAIN PLAN` を定期取得
  - P95しきい値超過でマージ不可
- 接続安全性:
  - HikariCP + `READ ONLY` トランザクション
  - SecretはGitLab CI Variables/Vault連携で注入

### 12.4 GitLab運用（ハーネス適用ポイント）

- `main` 保護 + `CODEOWNERS` + 必須パイプライン成功。
- `gitlab-ci.yml` を以下の段階に分離:
  1. `spec-lint`（YAMLスキーマ検証）
  2. `generate`（Specからコード/設定生成）
  3. `build-test`（unit/integration）
  4. `oracle-sql-test`（SQL検証、実行計画チェック）
  5. `security`（SAST/Dependency/Secret Detection）
  6. `deploy`（stg→canary→prod）
- Approvalは「人手承認」より **ポリシー承認（機械ゲート）**を優先。
- 失敗時は自動ロールバックJobとインシデントIssue自動起票を連動。

### 12.5 監視・自動復旧（最低限）

- 監視KPI:
  - Oracle参照遅延（query latency）
  - バッチ遅延
  - 画面応答時間（server-side render時間）
  - 権限拒否率の異常増加
- 自動復旧:
  - 接続プール枯渇時の段階的再起動
  - 失敗バッチ再実行
  - キャッシュ再構築

### 12.6 導入順（現実的な60日プラン）

- Day 1-15: 現行画面/KPI/SQLを `spec/` へ棚卸し
- Day 16-30: Spring Boot層をHexagonalへ整理、Oracle参照をRead Model化
- Day 31-45: GitLab CIに品質ゲート（SQL/性能/セキュリティ）導入
- Day 46-60: Canary配信 + 自動ロールバック + 運用Runbook自動化

### 12.7 この転用で守るべき非交渉項目

1. KPI定義をJavaコードに直書きしない（必ず `spec/` 起点）
2. Oracle本番表への直接更新権限をアプリに与えない
3. GitLabの必須ゲートを「警告」運用にしない（失敗時は確実に止める）
4. 例外運用は先に標準テンプレート化してから許可する

この4点を守ると、Spring Boot + Thymeleaf + Oracle + GitLab でも、
本ドキュメントのハーネス思想（宣言的・自動統制・自律運用）を高い再現性で移植できる。
