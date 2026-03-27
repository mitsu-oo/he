#!/usr/bin/env python3
"""PR本文が必須テンプレート項目を満たしているかチェックする。"""

from __future__ import annotations

import os
import sys

REQUIRED_SECTIONS = [
    "## 背景",
    "## 変更内容",
    "## 影響範囲",
    "## 検証結果",
    "## ロールバック手順",
]


def main() -> int:
    body = os.getenv("PR_BODY", "")
    if not body.strip():
        print("PR_BODY が空です。PR本文を取得できているか確認してください。")
        return 1

    missing = [section for section in REQUIRED_SECTIONS if section not in body]
    if missing:
        print("PR本文に必須セクションが不足しています:")
        for section in missing:
            print(f"- {section}")
        return 1

    print("PR本文テンプレートチェックに合格しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
