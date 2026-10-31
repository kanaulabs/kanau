/* 日本語と中国語を文節(語)で折る —— どのブラウザでも同じ所で(2026-10-31)。韓国語は最後の短い語だけを前に付ける。
   Chrome の word-break: auto-phrase は Safari・Firefox に無く、Safari では本文が「確かめる方/法」と語の途中で割れていた。
   ここでは語の切れ目(Intl.Segmenter。3 つのブラウザとも持つ)から文節を組み、文節の間にだけ <wbr> を置いて、
   html に .jb を付ける(CSS が word-break: keep-all にする)。スクリプトが走らなければ、今までどおり字の間で折れる。
   文節の組み方:
     - ひらがなだけの語(助詞・送り仮名・「いる」「する」)は前に付ける。ただし前が句読点・空白・行頭なら付けない
     - 句読点・閉じ括弧・長音・小さい字は前に付ける。開き括弧と「お」「ご」は後ろに付ける
     - 英字の後の空白に助詞が続くとき(「Monitor の」)、その空白は折らない空白(U+00A0)にする
     - 最後の文節が 3 字以下なら前に付ける(「寄る」だけが次の行に落ちない)
   見張りは docs/site-check/改行チェック.swift(Safari の WebKit)と 改行チェック.js(Chrome)。 */
(function () {
  var root = document.documentElement;
  var lang = (root.lang || '').toLowerCase();
  // 空白で折る言語(韓国語・英語・ほか)は、表の升や見出しの最後の 1〜3 字の語(「오른쪽 | 위」「per | sé」「anfitrião | faz」)だけを前に付ける
  if (!/^(ja|zh)/.test(lang)) { glueLastWord(); return; }
  var ZH = /^zh/.test(lang);
  if (!(ZH || /^ja/.test(lang)) || !window.Intl || !Intl.Segmenter) return;
  var seg = new Intl.Segmenter(ZH ? lang : 'ja', { granularity: 'word' });
  var HIRA = /^[ぁ-ゟ]+$/;
  var TAIL = /^[，；：？！“”‘’、。，．・：；！？!?,.:;」』）\)\]】〉》ー〜…ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ％%]+$/;
  var HEAD = /[「『（\(\[【〈《]$|^[おご]$/;
  var CJK = /[\u3000-\u30ff\u3400-\u9fff\uff00-\uffef]/;   // 句読点(、。)と全角の記号も —— 「CANDLE、BONFIRE」だけの文を落とさない
  var KATA = /^[゠-ヿー]+$/;
  var KANJI = /^[㐀-鿿々]+$/;
  var SKIP = { SCRIPT: 1, STYLE: 1, CODE: 1, PRE: 1, SELECT: 1, OPTION: 1, TEXTAREA: 1, INPUT: 1, svg: 1, SVG: 1 };

  function width(s) { var n = 0; for (var i = 0; i < s.length; i++) n += s.charCodeAt(i) < 0x2e80 ? 0.55 : 1; return n; }

  // before = 前の印の最後の字(文の頭の空白を扱うため)。fine = 表の升の中 —— 列が縮めるよう、ひらがなの語(「される」「こと」)を
  // 前に付けず、1 字の助詞はいつも、2 字の語尾(「から」「ます」)は 6 字までだけ付ける。付けすぎると 3 列の表がスマホで画面の 1.4 倍に広がった
  function phrases(text, before, fine) {
    var out = [], prev = null;
    var it = seg.segment(text)[Symbol.iterator](), x;
    var parts = [];
    while (!(x = it.next()).done) {
      // 辞書が割りすぎる語を戻す: つないで 8 字までのカタカナ(「ブラック|アウト」「ファイア|ウォール」「ルー|ター」。
      // 「プライバシー|ポリシー」「マルチキャスト|アドレス」のような長い複合語は割ってよい)、
      // 1 字の漢字と漢字(「灯|体」「各|接続」)
      var s0 = x.value.segment, q = parts[parts.length - 1];
      if (q !== undefined && ((KATA.test(q) && KATA.test(s0) && (q + s0).length <= 8) ||
          (!ZH && KANJI.test(q) && KANJI.test(s0) && (q.length === 1 || s0.length === 1)) ||
          (!ZH && q.length === 1 && KANJI.test(q) && KANJI.test(s0[0])))) parts[parts.length - 1] = q + s0;   // 「外|付け」
      else parts.push(s0);
    }
    for (var i = 0; i < parts.length; i++) {
      var s = parts[i], cur = out[out.length - 1];
      if (/^\s+$/.test(s)) {
        var nx = parts[i + 1] || '';
        // 英字・記号の後の空白に助詞が続く(「Monitor の」「50% が」「✕ を」)、数字の後に 1 字が続く(「13 章」)なら、
        // 折らない空白(U+00A0)にして後ろに付ける。文の頭の空白(前が別の印 <code> のとき)も同じ
        var back = cur === undefined ? (before || '') : cur.slice(-1);
        if ((HIRA.test(nx) && back && !/\s/.test(back) && !CJK.test(back)) ||
            (nx.length === 1 && CJK.test(nx) && /[0-9]$/.test(back)) ||
            (nx.length === 1 && !/[A-Za-z0-9\u3040-\u30ff\u3400-\u9fff]/.test(nx) && i === parts.length - 2)) {   // 最後の記号 1 つ(「或 ⏻」)
          if (cur === undefined) out.push(' '); else out[out.length - 1] = cur + ' ';
          prev = 'glue'; continue;
        }
        out.push(s); prev = 'space'; continue;
      }
      if (prev === 'glue') { out[out.length - 1] += s; prev = 'word'; continue; }
      var attach = cur !== undefined && prev !== 'space' && (
        TAIL.test(s) ||
        (HIRA.test(s) && (!fine || s.length === 1 || /^(ます|です|した|して|する|ない|ので|から|まで|より|など|こと)$/.test(s) || (s.length === 2 && width(cur + s) <= 6)) && !/[、。！？\s]$/.test(cur)) ||
        (ZH && s.length === 1 && KANJI.test(s) && KANJI.test(cur.slice(-1)) && width(cur) < 6) ||
        HEAD.test(cur));
      // 閉じ括弧の後の助詞(「機種)の」「」の」)は、Chrome が括弧の後で折るので語をつなぐ字(U+2060)を挟む
      if (attach) out[out.length - 1] = cur + (/[)）」』\]]$/.test(cur) && HIRA.test(s) ? '\u2060' : '') + s; else out.push(s);
      prev = 'word';
    }
    // 最後の短い文節を 1 行に残さない
    var k = out.length - 1;
    while (k > 0 && /^\s+$/.test(out[k])) k--;
    if (k > 0 && width(out[k].replace(/[、。！？」』）\s]/g, '')) <= 3 && !/^\s+$/.test(out[k - 1])) {
      out.splice(k - 1, 2, out[k - 1] + out[k]);
    }
    return out;
  }

  function walk(node) {
    var tw = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        for (var p = n.parentNode; p && p !== node.parentNode; p = p.parentNode) if (SKIP[p.nodeName]) return NodeFilter.FILTER_REJECT;
        // 日本語の無い「255.255.255.255(Art-Net)」も、括弧の前で折れるように拾う
        return CJK.test(n.data) || /\S[(（]/.test(n.data) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
      }
    });
    var list = [], n;
    while ((n = tw.nextNode())) list.push(n);
    list.forEach(function (n) {
      var pv = n.previousSibling, pt = pv ? pv.textContent : '';
      var ps = phrases(n.data, pt.slice(-1), !!(n.parentNode.closest && n.parentNode.closest('td,th')));
      // 句読点で終わり、次に印(<code>CANDLE</code>、<code>BONFIRE</code>)が続くときも、句読点の後で折れるようにする ——
      // keep-all の下では「、」と英字の間で折れず、効果の名前を並べた表が画面の 2.5 倍に広がった
      var after = /[、。，／・]$/.test(n.data) && n.nextSibling;
      if (ps.length < 2 && !after && ps.join('') === n.data) return;
      var f = document.createDocumentFragment();
      ps.forEach(function (p, i) {
        // 英字どうしの間には置かない(「B.|O.」「1|/|10」)。英字は空白でだけ折る。開き括弧に日本語が続くなら括弧の前で折ってよい(「UPDATE|(明るく点滅)」)
        if (i && !/^\s/.test(p) && !/\s$/.test(ps[i - 1]) && (/^[(（]/.test(p) || CJK.test(p.replace(/^[(（\[「『【]/, '')[0]) || CJK.test(ps[i - 1].slice(-1))))
          f.appendChild(document.createElement('wbr'));
        f.appendChild(document.createTextNode(p));
      });
      if (after) f.appendChild(document.createElement('wbr'));
      // 印の直後の「 と」「 は」(<code>＋ Fixtures</code> と)は、印ごと 1 つの塊にする ——
      // 折らない空白でも、Safari は white-space: nowrap の印の後ろで折ってしまい、行の頭が「と」になった
      var prevEl = n.previousSibling;
      if (/^\u00a0/.test(ps[0]) && prevEl && prevEl.nodeType === 1 && !/^(BR|WBR)$/.test(prevEl.nodeName) &&
          prevEl.textContent.length <= 16 && getComputedStyle(prevEl).display === 'inline') {
        var box = document.createElement('span');
        box.style.whiteSpace = 'nowrap';
        n.parentNode.insertBefore(box, prevEl);
        box.appendChild(prevEl);
        box.appendChild(f.firstChild);
        n.parentNode.insertBefore(box, n);
      }
      n.parentNode.replaceChild(f, n);
    });
  }

  function glueLastWord() {
    var els = document.querySelectorAll('td,th,h1,h2,h3,.chap b,.chap .d,.door b,.door span,.sub,li');
    // タイ語は語の間に空白が無い。短い升(「เครื่องเกสต์」)は 1 行に保つ —— 辞書に無い外来語が途中で割れた
    if (/^th/.test(lang)) Array.prototype.forEach.call(document.querySelectorAll('td,th'), function (c) {
      if (c.textContent.trim().length <= 14 && !/\s/.test(c.textContent.trim())) c.style.whiteSpace = 'nowrap';
    });
    Array.prototype.forEach.call(els, function (el) {
      var t = el.lastChild;
      while (t && t.nodeType !== 3) t = t.lastChild;
      if (!t) return;
      var m = t.data.match(/^([\s\S]*\S) ([^\s]{1,3}[.,)）]?\s*)$/);
      if (m) t.data = m[1] + '\u00a0' + m[2];
    });
  }

  walk(document.body);
  root.classList.add('jb');
})();
