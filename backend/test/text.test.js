import test from 'node:test';
import assert from 'node:assert/strict';
import { summarizeText, toDraft } from '../src/utils/text.js';

test('summarizeText returns short summary', () => {
  const input = '첫 문장입니다. 두 번째 문장입니다. 세 번째 문장입니다.';
  assert.equal(summarizeText(input, 'short'), '첫 문장입니다.');
});

test('toDraft formats output', () => {
  const draft = toDraft({ sourceType: 'news', title: '테스트', summary: '요약' });
  assert.ok(draft.includes('[NEWS]'));
});
