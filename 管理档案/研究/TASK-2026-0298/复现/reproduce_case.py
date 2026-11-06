#!/usr/bin/env python3
"""Exact enumeration of the article's finite teaching inputs; Python standard library only.

Reads one JSON file. Writes results.json and two original SVGs into a NEW output
directory. Refuses an existing output directory; no network, randomness or other
file writes. This is an arithmetic reproduction, not an independent review.
"""
import argparse
import copy
from collections import defaultdict
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path


def scalar(value):
    return {"exact": str(value), "decimal": float(value)}


def distribution(model):
    domains = [[(Q(t), Q(p)) for t, p in model[k]]
               for k in ("A", "B", "common_delay")]
    for domain in domains:
        if any(p < 0 or t < 0 for t, p in domain) or sum(p for t, p in domain) != 1:
            raise ValueError("Invalid domain")
    tail = Q(model["tail"])
    if tail < 0:
        raise ValueError("Negative tail")
    rows, pmf = [], defaultdict(Q)
    ea, eb = Q(0), Q(0)
    for (a, pa), (b, pb), (z, pz) in itertools.product(*domains):
        p = pa * pb * pz
        ta, tb = a + z, b + z
        finish = max(ta, tb) + tail
        rows.append({"X_A": str(a), "X_B": str(b), "Z": str(z),
                     "T_A": str(ta), "T_B": str(tb), "F": str(finish), "p": scalar(p)})
        pmf[finish] += p
        ea += p * ta
        eb += p * tb
    assert sum(pmf.values()) == 1
    return rows, dict(sorted(pmf.items())), ea, eb


def cumulative(pmf, d):
    return sum((p for t, p in pmf.items() if t <= d), Q(0))


def quantile(pmf, alpha):
    if not 0 < alpha <= 1:
        raise ValueError("Quantile level must be in (0,1]")
    for t in sorted(pmf):
        if cumulative(pmf, t) >= alpha:
            return t
    raise AssertionError("Total probability is not one")


def summarise(model, queries):
    rows, pmf, ea, eb = distribution(model)
    mean = sum((t * p for t, p in pmf.items()), Q(0))
    assert mean >= max(ea, eb) + Q(model["tail"])
    return {"scenarios": rows,
            "finish_distribution": [{"F": str(t), "p": scalar(p), "cdf": scalar(cumulative(pmf, t))} for t, p in pmf.items()],
            "mean_T_A": scalar(ea), "mean_T_B": scalar(eb),
            "mean_F": scalar(mean), "merge_of_means_plus_tail": scalar(max(ea, eb) + Q(model["tail"])),
            "deadline_probabilities": {d: scalar(cumulative(pmf, Q(d))) for d in queries["deadlines"]},
            "left_quantiles": {a: str(quantile(pmf, Q(a))) for a in queries["quantiles"]}}


def svg_start(width, height, title, desc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<title>{title}</title><desc>{desc}</desc>
<style>text{{font-family:'Noto Sans CJK SC','Noto Sans CJK JP',sans-serif;fill:#173042}} .small{{font-size:17px}} .body{{font-size:20px}} .title{{font-size:27px;font-weight:700}} .grid{{stroke:#d8e2e9;stroke-width:1}} .line{{stroke:#24465c;stroke-width:2;fill:none}} .risk{{stroke:#b15d16;stroke-width:3;fill:none}}</style>
<rect width="100%" height="100%" fill="#ffffff"/>
'''


def mechanism_svg():
    s = svg_start(1100, 575, "共同事件只取一次，再计算两路汇合", "共同接口修订延迟Z同时进入T_A和T_B；先对每个情境取max，再加一工作日确定尾段。")
    s += '''<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="#24465c"/></marker><marker id="orange" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="#b15d16"/></marker></defs>
<text x="40" y="48" class="title">共同事件只取一次，再计算两路汇合</text>
<text x="40" y="80" class="small">原创教学模型｜工作日边界｜不同人员与设备，容量已预留</text>
<rect x="355" y="113" width="350" height="78" rx="12" fill="#fff0da" stroke="#b15d16"/>
<text x="530" y="145" text-anchor="middle" class="body">同一次接口修订 Z</text>
<text x="530" y="173" text-anchor="middle" class="small">不发生 0 天（80%）／发生 +3 天（20%）</text>
<rect x="40" y="247" width="230" height="80" rx="12" fill="#eef5f8" stroke="#6c94aa"/>
<text x="155" y="279" text-anchor="middle" class="body">动画导出 X_A</text>
<text x="155" y="307" text-anchor="middle" class="small">2 天 80%／4 天 20%</text>
<rect x="40" y="377" width="230" height="80" rx="12" fill="#eef5f8" stroke="#6c94aa"/>
<text x="155" y="409" text-anchor="middle" class="body">事件映射 X_B</text>
<text x="155" y="437" text-anchor="middle" class="small">2 天 80%／4 天 20%</text>
<rect x="355" y="252" width="240" height="70" rx="12" fill="#f0f8f7" stroke="#4c8a81"/>
<text x="475" y="294" text-anchor="middle" class="body">T_A = X_A + Z</text>
<rect x="355" y="382" width="240" height="70" rx="12" fill="#f0f8f7" stroke="#4c8a81"/>
<text x="475" y="424" text-anchor="middle" class="body">T_B = X_B + Z</text>
<path d="M270,287 H349 M270,417 H349" class="line" marker-end="url(#arrow)"/>
<path d="M475,191 V246" class="risk" marker-end="url(#orange)"/>
<path d="M620,191 V350 H475 V376" class="risk" marker-end="url(#orange)"/>
<path d="M595,287 H715 V322" stroke="white" stroke-width="7" fill="none"/>
<path d="M595,287 H715 V322 M595,417 H715 V383" class="line" marker-end="url(#arrow)"/>
<rect x="645" y="328" width="145" height="50" rx="10" fill="#e6effb" stroke="#4876a6"/>
<text x="717" y="360" text-anchor="middle" class="body">M = max</text>
<path d="M790,353 H827" class="line" marker-end="url(#arrow)"/>
<rect x="833" y="310" width="225" height="85" rx="12" fill="#eef5f8" stroke="#6c94aa"/>
<text x="945" y="344" text-anchor="middle" class="body">F = M + 1</text>
<text x="945" y="373" text-anchor="middle" class="small">整合准备完成</text>
<text x="40" y="510" class="body">X_A、X_B、Z 在本模型中相互独立；T_A、T_B 因共享 Z 而共同变化。</text>
<text x="40" y="543" class="small">箭头表示计算输入，不是共享审核人的资源顺序；尾段不代表 QA 通过或正式发布。</text>
</svg>'''
    return s


def cdf_svg(pmf):
    s = svg_start(1100, 670, "从累计概率查询期限与分位", "主例F在3、5、6、8工作日的累计概率分别为0.512、0.8、0.928、1。实心点包含跳点，空心点不包含。")
    x = lambda t: 110 + float(t) * 100
    y = lambda p: 535 - float(p) * 380
    s += '<text x="40" y="48" class="title">固定期限向上读概率，目标概率向右找最早日期</text>\n'
    s += '<text x="40" y="82" class="small">G(t) = P(F ≤ t)｜原创教学模型｜包含恰好在截止时完成的情境</text>\n'
    for p in (0, Q(1, 5), Q(2, 5), Q(3, 5), Q(4, 5), 1):
        s += f'<path d="M110,{y(p)} H1010" class="grid"/><text x="92" y="{y(p)+6}" text-anchor="end" class="small">{float(p):.1f}</text>\n'
    s += '<path d="M110,140 V535 H1030" class="line"/>\n'
    for t in range(10):
        s += f'<path d="M{x(t)},535 V543" class="line"/><text x="{x(t)}" y="567" text-anchor="middle" class="small">{t}</text>\n'
    s += '<text x="535" y="605" class="body">终点 F 的工作日边界 t</text><text x="40" y="127" class="small">累计概率</text>\n'
    for a, t, label in [(Q(4,5),5,"P80 = 5"),(Q(9,10),6,"P90 = 6"),(Q(19,20),8,"P95 = 8")]:
        s += f'<path d="M110,{y(a)} H{x(t)} V535" stroke="#b15d16" stroke-width="1.5" stroke-dasharray="5 5" fill="none"/>\n'
    cum, last = Q(0), Q(0)
    for t, p in pmf.items():
        s += f'<path d="M{x(last)},{y(cum)} H{x(t)}" stroke="#246a94" stroke-width="4"/>\n'
        s += f'<circle cx="{x(t)}" cy="{y(cum)}" r="5.5" fill="white" stroke="#246a94" stroke-width="2"/>\n'
        old = cum
        cum += p
        s += f'<path d="M{x(t)},{y(old)} V{y(cum)}" stroke="#246a94" stroke-width="1.5" stroke-dasharray="3 4"/>\n'
        s += f'<circle cx="{x(t)}" cy="{y(cum)}" r="6" fill="#246a94"/>\n'
        label = f'{float(cum):.3f}'
        s += f'<text x="{x(t)+12}" y="{y(cum)-12}" class="small">{label}</text>\n'
        last = t
    s += f'<path d="M{x(last)},{y(cum)} H1010" stroke="#246a94" stroke-width="4"/>\n'
    s += '<text x="375" y="129" class="small">P80 = 5</text><text x="555" y="129" class="small">P90 = 6</text><text x="755" y="129" class="small">P95 = 8</text>\n'
    s += '<text x="110" y="645" class="small">期限 5：80%；期限 6：92.8%。P90 跳到 6，不晚于 6 完成的概率为 92.8%。</text></svg>'
    return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    base = data["base"]
    result = {"description": data["description"], "base": summarise(base, data["queries"]), "alternatives": {}}
    for name, changes in data["alternatives"].items():
        model = copy.deepcopy(base)
        model.update(changes)
        result["alternatives"][name] = summarise(model, data["queries"])
    marginal = data["marginal_only"]
    p = Q(marginal["fast_probability"])
    low, high = max(Q(0), 2*p-1), p
    result["marginal_bounds"] = {"lower": scalar(low), "upper": scalar(high), "couplings": []}
    for q_text in marginal["q_examples"]:
        q = Q(q_text)
        weights = [q, p-q, p-q, 1-2*p+q]
        assert all(w >= 0 for w in weights) and sum(weights) == 1
        assert weights[0]+weights[1] == p and weights[0]+weights[2] == p
        times = [(Q(marginal["fast"]), Q(marginal["fast"])),
                 (Q(marginal["fast"]), Q(marginal["slow"])),
                 (Q(marginal["slow"]), Q(marginal["fast"])),
                 (Q(marginal["slow"]), Q(marginal["slow"]))]
        prob = sum((w for (a,b),w in zip(times,weights) if max(a,b)+Q(marginal["tail"]) <= Q(marginal["deadline"])), Q(0))
        result["marginal_bounds"]["couplings"].append({"q":q_text,"weights_fast_fast_fast_slow_slow_fast_slow_slow":[scalar(w) for w in weights],"P_deadline":scalar(prob)})
    ranges = []
    for r_text in data["common_risk_range"]:
        r = Q(r_text)
        model = copy.deepcopy(base)
        model["common_delay"] = [["0",str(1-r)],["3",str(r)]]
        _, pmf, _, _ = distribution(model)
        actual = cumulative(pmf,Q(6))
        assert actual == 1-Q(9,25)*r
        ranges.append({"r":r_text,"P_F_le_6":scalar(actual)})
    result["risk_range_endpoints"] = ranges
    result["risk_rate_threshold_for_P90_by_6"] = scalar(Q(5,18))
    old = data["legacy_example"]
    f, slow, p = Q(old["fast"]), Q(old["slow"]), Q(old["fast_probability"])
    result["legacy_example"] = {"branch_mean":scalar(p*f+(1-p)*slow),"independent_merge_mean":scalar(p*p*f+(1-p*p)*slow),"synchronous_merge_mean":scalar(p*f+(1-p)*slow)}
    sample = data["small_sample_counterexample"]
    result["six_successes_probability_if_p_0_7"] = scalar(Q(sample["hypothetical_success_probability"])**sample["n"])
    assert result["base"]["deadline_probabilities"]["5"]["exact"] == "4/5"
    assert result["base"]["deadline_probabilities"]["6"]["exact"] == "116/125"
    assert result["base"]["left_quantiles"] == {"0.8":"5","0.9":"6","0.95":"8"}
    # All validation precedes creation. Never replace earlier output.
    args.out_dir.mkdir(parents=True, exist_ok=False)
    (args.out_dir/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (args.out_dir/"common-event-merge.svg").write_text(mechanism_svg(),encoding="utf-8")
    _, pmf, _, _ = distribution(base)
    (args.out_dir/"finish-cdf.svg").write_text(cdf_svg(pmf),encoding="utf-8")
    print("Validated finite inputs; wrote results.json and two original SVGs to:",args.out_dir)
    print("No random sampling, no scheduling product, no production observations.")


if __name__ == "__main__":
    main()
