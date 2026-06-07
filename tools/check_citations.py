#!/usr/bin/env python3
# 引用完整性校验脚本 — 检查报告中每条参考文献是否都有可点击超链接
# 用法: python check_citations.py <报告文件.md>

import sys, re

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # 1. 提取参考文献区域
    ref_match = re.search(r'## 参考文献.*?(?=\n## |\n---\n|\Z)', content, re.DOTALL)
    if not ref_match:
        # 有些报告用"出处表"或其他标题
        ref_match = re.search(r'## (参考文献|出处表|数据来源).*?(?=\n## |\n---\n|\Z)', content, re.DOTALL)

    if not ref_match:
        errors.append("[ERR] 未找到「参考文献」或「出处表」章节")
        return errors

    ref_section = ref_match.group(0)

    # 2. 提取每条参考文献
    refs = re.findall(r'\[(\d+)\]', ref_section)
    cited_nums = set(refs)

    if not cited_nums:
        errors.append("[ERR] 参考文献表为空")
        return errors

    # 3. 检查每条是否有 [文档名](URL) 格式的超链接
    for num in sorted(cited_nums, key=int):
        # 找到该编号的行
        pattern = rf'\[{num}\].*?\n'
        line_match = re.search(pattern, ref_section)
        if line_match:
            line = line_match.group(0)
            if not re.search(r'\[.+?\]\(https?://.+?\)', line):
                errors.append(f"[ERR] 参考文献 [{num}] 缺少可点击超链接")
        else:
            errors.append(f"[ERR] 参考文献 [{num}] 条目不存在")

    # 4. 检查正文中引用的编号是否都在参考文献中存在
    body = content[:ref_match.start()]
    body_refs = set(re.findall(r'\[(\d+)\]', body))

    missing_in_refs = body_refs - cited_nums
    for num in sorted(missing_in_refs, key=int):
        errors.append(f"[WARN] 正文引用了 [{num}]，但参考文献表中不存在")

    # 5. 检查是否有参考文献编号未被正文引用
    unused_refs = cited_nums - body_refs
    for num in sorted(unused_refs, key=int):
        errors.append(f"[INFO] 参考文献 [{num}] 未被正文引用")

    if not errors:
        print(f"[OK] {filepath} — 引用校验通过 ({len(cited_nums)}条参考文献, 正文引用{len(body_refs)}个编号)")
    else:
        print(f"\n===== {filepath} 引用校验发现问题 =====")
        for e in errors:
            print(f"  {e}")
        print(f"\n  参考文献: {len(cited_nums)}条 | 正文引用: {len(body_refs)}个编号")

    return errors

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python check_citations.py <报告文件.md>")
        sys.exit(1)
    errors = check_file(sys.argv[1])
    sys.exit(1 if errors else 0)
