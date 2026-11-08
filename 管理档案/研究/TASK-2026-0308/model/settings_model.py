#!/usr/bin/env python3
"""Finite teaching model: serialized callbacks; no engine, geometry or frames."""
from dataclasses import dataclass, asdict
from itertools import permutations
import json
import platform
import sys

@dataclass(frozen=True)
class Request:
    generation: int
    request_id: int

@dataclass(frozen=True)
class LayoutInput:
    generation: int
    content_version: int
    scale_version: int

class Preview:
    def __init__(self):
        self.generation = 1
        self.open = True
        self.serial = 0
        self.current = None
        self.records = {}
        self.content = None
        self.committed_token = None
        self.content_version = 0
        self.scale = 1.0
        self.scale_version = 0
        self.layout_done = None
        self.status = 'idle'
        self.events = []

    def log(self, event, **data):
        self.events.append(dict(event=event, **data))

    def request(self, language, accept=True, start=None):
        if not accept or not self.open:
            self.log('rejected', language=language)
            return None  # Rejection does not supersede the last admitted request.
        self.serial += 1
        token = Request(self.generation, self.serial)
        self.records[token] = dict(language=language, settled=False)
        self.current = token
        self.status = 'pending'
        self.log('admitted', token=asdict(token), language=language)
        # Admission and identity MUST be visible before any synchronous callback.
        if start:
            start(token)
        return token

    def complete(self, token, error=None):
        record = self.records.get(token)
        if (not self.open or token != self.current or record is None
                or record['settled']):
            self.log('ignored_completion', token=asdict(token), error=error)
            return False
        record['settled'] = True
        if error is not None:
            self.status = 'failed'
            self.log('current_failure', token=asdict(token), error=error)
            return False
        self.content = record['language']
        self.committed_token = token
        self.content_version += 1
        self.layout_done = None
        self.status = 'content_ready'
        self.log('commit', token=asdict(token), language=self.content,
                 content_version=self.content_version)
        return True

    def cancel(self):
        self.current = None
        self.status = 'cancelled'
        self.log('cancel')

    def close(self):
        self.open = False
        self.generation += 1
        self.current = None
        self.layout_done = None
        self.status = 'closed'
        self.log('close', generation=self.generation)

    def reopen(self):
        self.open = True
        self.generation += 1
        self.status = 'idle'
        self.log('reopen', generation=self.generation)

    def set_scale(self, value):
        if self.scale != value:
            self.scale = value
            self.scale_version += 1
            self.layout_done = None
        self.log('scale', value=value, scale_version=self.scale_version)

    def layout_input(self):
        if not self.open or self.content is None:
            return None
        return LayoutInput(self.generation, self.content_version, self.scale_version)

    def operation_ready(self, token):
        # Logical readiness for THIS request, not proof that pixels were displayed.
        signature = self.layout_input()
        ready = (token is not None and self.open
                 and self.current == token == self.committed_token
                 and self.status == 'content_ready'
                 and signature is not None and self.layout_done == signature)
        self.log('operation_ready', token=asdict(token) if token else None,
                 committed_token=asdict(self.committed_token) if self.committed_token else None,
                 status=self.status, ready=ready)
        return ready

    def layout_receipt(self, captured_input):
        # Equality is provenance validation, NOT a geometry correctness check.
        if captured_input is None or captured_input != self.layout_input():
            self.log('ignored_layout', input=asdict(captured_input) if captured_input else None)
            return False
        self.layout_done = captured_input
        self.log('layout_receipt', input=asdict(captured_input))
        return True


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def run():
    cases = []
    def save(name, p, claim, boundary):
        cases.append(dict(name=name, passed=True, supports=claim,
                          not_tested=boundary, events=p.events))

    p = Preview(); a=p.request('ja'); b=p.request('fr')
    check(p.complete(b) and not p.complete(a) and p.content=='fr', 'out of order')
    save('delayed_out_of_order',p,'后受理 fr 先完成后，ja 的迟到结果不能提交。','真实线程竞争、加载器行为。')

    p=Preview(); a=p.request('ja'); b=p.request('fr'); c=p.request('ja')
    check(a!=c and not p.complete(a) and not p.complete(b) and p.complete(c), 'ABA')
    save('ja_fr_ja_same_value',p,'相同语言值不代表同一次请求；第一次 ja 不能冒充第三次 ja。','语言资源内容、字体。')

    p=Preview(); a=p.request('ja'); p.close(); p.reopen(); b=p.request('fr')
    check(a.generation!=b.generation and not p.complete(a) and p.complete(b),'generation')
    save('close_reopen',p,'关闭重开后的请求与旧视图请求分离。','Unity 生命周期及销毁回调。')

    p=Preview(); a=p.request('ja'); b=p.request('fr'); p.complete(a,error='old failure')
    check(p.status=='pending','stale failure altered status'); p.complete(b,error='current failure')
    check(p.status=='failed' and p.content is None,'current failure')
    check(not p.complete(b) and p.content is None,'failure terminal')
    save('current_and_stale_failure',p,'过期失败不改当前状态；当前失败终结请求，不伪造成功。','错误 UI、自动重试策略。')

    p=Preview(); a=p.request('ja'); p.cancel()
    check(not p.complete(a) and p.content is None,'cancel')
    save('cancel_then_late_completion',p,'取消后的迟到回调不能提交。','底层操作是否停止及资源释放。')

    p=Preview(); a=p.request('ja'); check(p.complete(a),'first'); v=p.content_version
    check(not p.complete(a) and p.content_version==v,'duplicate')
    save('duplicate_completion',p,'成功回调重复到达不重复提交或增加内容版本。','多线程原子性。')

    p=Preview(); a=p.request('ja'); check(p.request('fr',accept=False) is None,'reject')
    check(p.current==a and p.complete(a),'rejection superseded request')
    save('rejected_admission',p,'未受理请求不取代最后受理请求。','实际受理/限流条件。')

    p=Preview(); a=p.request('ja',start=lambda t:p.complete(t))
    check(p.content=='ja' and p.status=='content_ready' and p.records[a]['settled'],'sync cache')
    save('synchronous_cache_completion',p,'先保存受理记录再启动加载，允许启动函数内同步完成。','真实缓存 API 及其重入约定。')

    p=Preview(); p.complete(p.request('ja')); old=p.layout_input(); p.set_scale(1.5)
    check(not p.layout_receipt(old) and p.layout_done is None,'scale layout')
    fresh=p.layout_input(); check(p.layout_receipt(fresh),'fresh scale')
    p.complete(p.request('fr'))
    check(not p.layout_receipt(fresh) and p.layout_done is None,'content layout')
    check(p.layout_receipt(p.layout_input()),'latest layout')
    save('old_layout_receipts',p,'布局输入标记同时含内容版本与缩放版本，任一改变均使旧回执失效。','真实布局几何、换行、帧顺序。')

    p=Preview(); p.complete(p.request('ja')); old=p.layout_input(); p.close(); p.reopen()
    check(not p.layout_receipt(old),'old view layout')
    save('layout_across_reopen',p,'布局输入也带视图代际，旧视图回执不能确认新视图。','视图重建时真实组件状态。')

    p=Preview(); p.complete(p.request('ja')); b=p.request('fr'); p.complete(b,error='unavailable')
    check(p.content=='ja' and p.status=='failed' and p.current==b,'fallback semantics')
    save('failure_preserves_previous_content',p,'当前失败保留逻辑历史 content，但状态明确为失败；没有验证旧内容实际显示。','产品对旧内容展示或清空的选择。')

    p=Preview(); a=p.request('ja'); p.complete(a)
    check(not p.operation_ready(a), 'content alone is not operation readiness')
    old=p.layout_input(); p.layout_receipt(old)
    check(p.operation_ready(a), 'matching content and layout')
    b=p.request('fr'); check(p.layout_receipt(old), 'old content layout remains meaningful')
    check(not p.operation_ready(b) and not p.operation_ready(a), 'pending request cannot inherit old readiness')
    p.complete(b); check(not p.operation_ready(b), 'new content needs own receipt')
    check(not p.layout_receipt(old), 'previous content receipt is stale')
    p.layout_receipt(p.layout_input()); check(p.operation_ready(b), 'new operation ready')
    p.set_scale(1.5); check(not p.operation_ready(b), 'scale invalidates readiness')
    p.layout_receipt(p.layout_input()); check(p.operation_ready(b), 'new scale ready')
    c=p.request('de'); p.complete(c,error='unavailable')
    check(not p.operation_ready(c), 'failure is not readiness')
    p.close(); p.reopen(); check(not p.operation_ready(b), 'old generation cannot be ready')
    save('operation_readiness_requires_identity_and_layout',p,
         '本次请求就绪同时要求当前提交身份、content_ready 和匹配布局签名；旧内容回执不能确认新请求。',
         '实际占位/旧内容显示策略、像素上屏或引擎布局质量。')

    # Finite enumeration, not proof over all possible event histories.
    p=Preview(); enum=[]
    for order in permutations(range(3)):
        q=Preview(); tokens=[q.request(s) for s in ['ja','fr','ja']]
        for index in order: q.complete(tokens[index])
        commits=[e for e in q.events if e['event']=='commit']
        check(len(commits)==1 and commits[0]['token']==asdict(tokens[2]),'permutation')
        enum.append(dict(completion_order=order,commit_token=commits[0]['token']))
    p.log('six_orders',results=enum)
    save('all_three_completion_permutations',p,'三次请求全部先受理的六种完成排列均只提交第三次。','受理、取消、关闭与完成的所有交织；不是模型检查证明。')

    # Independent counterexample: L1(ja) -> L2(fr) -> C2 -> C1 -> S.
    # Deliberately broken callbacks ignore identity. S is an explicitly DEFINED
    # teaching-model rebuild from the current target, not an engine mechanism.
    target=None; logical_content=None; refresh_events=[]; old=Request(1,1); latest=Request(1,2)
    for label,token,language in [('L1',old,'ja'),('L2',latest,'fr')]:
        target=language
        refresh_events.append(dict(event=label,token=asdict(token),target=target))
    for label,token,payload in [('C2',latest,'fr'),('C1',old,'ja')]:
        logical_content=payload
        refresh_events.append(dict(event=label,token=asdict(token),
                                   logical_content=logical_content,illegal_commit=token!=latest))
    check(logical_content=='ja' and target=='fr', 'stale callback corrupts logical content')
    logical_content=target  # S: defined reconstruction from the latest target.
    refresh_events.append(dict(event='S',model_action='rebuild_from_current_target',
                               scale=1.5,target=target,logical_content=logical_content))
    illegal=sum(e.get('illegal_commit',False) for e in refresh_events)
    check(logical_content=='fr' and illegal==1, 'refresh masks stale commit')
    cases.append(dict(name='refresh_masks_stale_commit_counterexample',passed=True,
        supports='L1(ja)→L2(fr)→C2→C1→S：旧 ja 曾覆盖 fr，有限模型定义的 S 按当前目标重建后恢复 fr；最终正确不排除旧提交。',
        not_tested='S 不是 Unity 或布局系统机制，未验证实际缩放是否触发内容重建或错误是否上屏。',
        events=refresh_events,final_snapshot_passes=True,illegal_commit_count=illegal))

    # Deliberately broken implementation: retag old payload with current identity.
    current=Request(1,2)
    bad_events=[dict(event='admitted',token=asdict(Request(1,1)),language='ja'),
                dict(event='admitted',token=asdict(current),language='fr')]
    shown=None
    for original,payload in [(Request(1,1),'ja'),(current,'fr')]:
        relabelled=current  # BUG: completion-time substitution loses provenance.
        if relabelled==current:
            shown=payload
            bad_events.append(dict(event='bad_commit',original=asdict(original),
                                   checked=asdict(relabelled),language=shown))
    wrong_commits=[e for e in bad_events if e['event']=='bad_commit' and e['original']!=e['checked']]
    check(shown=='fr' and len(wrong_commits)==1,'masked counterexample')
    cases.append(dict(name='masked_stale_commit_counterexample',passed=True,
        supports='错误实现最终逻辑内容仍为 fr，但曾提交过期 ja；最终快照不能证明过程中没有旧提交。',
        not_tested='错误状态是否真的出现在屏幕上；模型没有渲染帧。',events=bad_events,
        final_snapshot_passes=True,illegal_commit_count=len(wrong_commits)))

    return dict(scope='有限 Python 教学模型；无 Unity，无真实布局、无帧时序或游戏验证。',
                environment=dict(python=sys.version,platform=platform.platform()),
                test_count=len(cases),passed=len(cases),cases=cases)

if __name__=='__main__':
    print(json.dumps(run(),ensure_ascii=False,indent=2))
