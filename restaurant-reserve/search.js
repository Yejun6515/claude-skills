// 핫페퍼 그루메 서치 API (스킬 self-contained). 키는 같은 폴더 config.json.
// 사용: node search.js "<키워드>" [--count N] [--party N] [--freefood] [--freedrink] [--budget 코드]
//   예) node search.js "難波 居酒屋" --freedrink --budget B002 --count 8
//   예산 코드(실제): B009=~500, B010=501-1000, B011=1001-1500, B001=1501-2000,
//     B002=2001-3000, B003=3001-4000, B008=4001-5000, B015=5001-6000 ... (밤 평균예산)
//   "3000엔 이하" = B002 (필요시 B001 등 콤마로 여러개). budget은 평균값이라 요일특가는 못 거름.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const dir = dirname(fileURLToPath(import.meta.url));
const KEY = JSON.parse(readFileSync(join(dir, 'config.json'), 'utf8')).hotpepper_key;

const argv = process.argv.slice(2);
let keyword = '';
const opt = {};
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--count') opt.count = argv[++i];
  else if (a === '--party') opt.party = argv[++i];
  else if (a === '--budget') opt.budget = argv[++i];
  else if (a === '--freefood') opt.freefood = 1;
  else if (a === '--freedrink') opt.freedrink = 1;
  else if (!keyword) keyword = a;
}
keyword = keyword || '難波 居酒屋';

const p = new URLSearchParams({ key: KEY, keyword, count: String(opt.count || 8), format: 'json', order: '4' });
if (opt.party) p.set('party_capacity', opt.party);
if (opt.budget) p.set('budget', opt.budget);
if (opt.freefood) p.set('free_food', '1');    // 食べ放題あり
if (opt.freedrink) p.set('free_drink', '1');  // 飲み放題あり

const res = await fetch(`https://webservice.recruit.co.jp/hotpepper/gourmet/v1/?${p}`);
const data = await res.json();
if (data.results.error) { console.error('API 오류:', JSON.stringify(data.results.error)); process.exit(1); }
const shops = (data.results.shop || []).map((s) => ({
  name: s.name, genre: s.genre?.name, budget: s.budget?.name, capacity: s.capacity,
  access: s.mobile_access || s.access, address: s.address, tel: s.tel || null,
  free_food: s.free_food, free_drink: s.free_drink,
  net_reserve: s.urls?.pc || null, coupon: s.coupon_urls?.pc || null, open: s.open,
}));
console.log(JSON.stringify({ available: data.results.results_available, filters: { ...opt, keyword }, shops }, null, 2));
