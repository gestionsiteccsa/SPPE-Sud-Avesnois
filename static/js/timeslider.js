/* TimeSlider - selecteur d'horaires d'ouverture (vanilla JS, sans dependance)
 *
 * Usage :
 *   const picker = new TimeSlider('#hours-picker', {
 *     value: { lundi: { closed: false, slots: [["09:00","12:30"]] }, ... },
 *     onChange: (value) => { ... }
 *   });
 *   picker.getValue()  /  picker.setValue(obj)  /  picker.destroy()
 *
 * Evenement 'change' emis sur l'element racine apres chaque modification.
 */

(function (global) {
  'use strict';

  var DAYS = [
    { key: 'lundi', label: 'Lundi' },
    { key: 'mardi', label: 'Mardi' },
    { key: 'mercredi', label: 'Mercredi' },
    { key: 'jeudi', label: 'Jeudi' },
    { key: 'vendredi', label: 'Vendredi' },
    { key: 'samedi', label: 'Samedi' },
    { key: 'dimanche', label: 'Dimanche' }
  ];

  var DAY_MIN = 1440;      /* minutes dans une journee */
  var MIN_SPAN = 45;       /* plage de vue minimale (zoom max) */
  var MIN_RANGE = 15;      /* duree minimale d'une plage */
  var CLICK_THRESHOLD = 4; /* px de mouvement avant de considerer un drag */

  var ICON_COPY = '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';

  function pad(n) { return n < 10 ? '0' + n : String(n); }
  function fmt(t) { return pad(Math.floor(t / 60)) + ':' + pad(t % 60); }
  function parse(s) {
    var m = /^(\d{1,2}):(\d{2})$/.exec(String(s).trim());
    if (!m) return null;
    var h = +m[1], mn = +m[2];
    if (h > 23 || mn > 59) return null;
    return h * 60 + mn;
  }
  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
  function snapStep(span) { return Math.max(15, Math.round(span / 48 / 15) * 15); }
  function labelStep(span) {
    var steps = [1440, 720, 360, 180, 120, 60, 30, 15];
    var target = span / 6;
    for (var i = 0; i < steps.length; i++) if (steps[i] <= target) return steps[i];
    return 15;
  }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function TimeSlider(root, options) {
    if (!(this instanceof TimeSlider)) return new TimeSlider(root, options);
    this.root = typeof root === 'string' ? document.querySelector(root) : root;
    if (!this.root) throw new Error('TimeSlider: element racine introuvable');
    this.opts = options || {};
    if (typeof this.opts.value === 'string') {
      try { this.opts.value = JSON.parse(this.opts.value); } catch (e) { this.opts.value = null; }
    }
    this.days = DAYS.map(function (d) {
      return {
        key: d.key,
        label: d.label,
        closed: false,
        slots: [],
        view: { span: DAY_MIN },
        selected: -1
      };
    });
    this._els = {};
    this.drag = null;
    this._onMove = null;
    this._onUp = null;
    this._onDocDown = null;
    this._build();
    this._bind();
    if (this.opts.value) this.setValue(this.opts.value);
    this.days.forEach(function (d) { this._renderDay(d); }, this);
  }

  /* ---------- construction DOM ---------- */

  TimeSlider.prototype._btn = function (label, title, cls, html) {
    var b = el('button', 'ts-btn ' + cls);
    b.type = 'button';
    if (html) { b.innerHTML = html; } else { b.textContent = label; }
    b.setAttribute('data-tooltip', title);
    return b;
  };

  TimeSlider.prototype._build = function () {
    var self = this;
    this.root.classList.add('ts-widget');
    this.root.innerHTML = '';
    var wrap = el('div', 'ts-days');
    this.root.appendChild(wrap);

    this.days.forEach(function (d) {
      var col = el('div', 'ts-day');
      col.dataset.day = d.key;

      var header = el('div', 'ts-day-header');
      var row = el('div', 'ts-day-head-row');
      row.appendChild(el('div', 'ts-day-name', d.label));
      var summary = el('div', 'ts-day-summary', '—');
      row.appendChild(summary);
      header.appendChild(row);

      var controls = el('div', 'ts-controls');
      var toggle = el('label', 'ts-toggle');
      var cb = document.createElement('input');
      cb.type = 'checkbox';
      toggle.setAttribute('data-tooltip', 'Journée fermée');
      toggle.appendChild(cb);
      toggle.appendChild(document.createTextNode('Fermé'));
      controls.appendChild(toggle);

      controls.appendChild(self._btn('', 'Copier ce jour vers d\'autres jours', 'ts-copy', ICON_COPY));
      header.appendChild(controls);
      col.appendChild(header);

      var track = el('div', 'ts-track');
      var canvas = el('div', 'ts-canvas');
      var preview = el('div', 'ts-preview');
      preview.style.display = 'none';
      preview.appendChild(el('span', 'ts-preview-label', ''));
      canvas.appendChild(preview);
      track.appendChild(canvas);
      col.appendChild(track);

      var popover = el('div', 'ts-popover');
      popover.style.display = 'none';
      popover.appendChild(el('h4', 'ts-popover-title', 'Copier vers…'));
      var list = el('div', 'ts-popover-list');
      popover.appendChild(list);
      var actions = el('div', 'ts-popover-actions');
      var btnAll = self._btn('Tous', 'Cocher / décocher tous les jours', 'ts-popover-all');
      var btnCancel = self._btn('Annuler', 'Fermer', 'ts-popover-cancel');
      var btnOk = self._btn('Copier', 'Appliquer la copie', 'ts-popover-ok ts-btn-primary');
      actions.appendChild(btnAll);
      actions.appendChild(btnCancel);
      actions.appendChild(btnOk);
      popover.appendChild(actions);
      col.appendChild(popover);

      wrap.appendChild(col);

      var btnCopy = header.querySelector('.ts-copy');

      self._els[d.key] = {
        col: col,
        header: header,
        summary: summary,
        closedInput: cb,
        track: track,
        canvas: canvas,
        preview: preview,
        popover: popover,
        list: list,
        btnCopy: btnCopy,
        btnAll: btnAll,
        btnOk: btnOk,
        btnCancel: btnCancel,
        grid: null,
        rangeEls: []
      };
    });
  };

  /* ---------- evenements ---------- */

  TimeSlider.prototype._bind = function () {
    var self = this;

    this.days.forEach(function (d) {
      var E = self._els[d.key];

      E.closedInput.addEventListener('change', function () {
        d.closed = E.closedInput.checked;
        self._renderDay(d);
        self._commit();
      });

      E.btnCopy.addEventListener('click', function (e) {
        e.stopPropagation();
        self._openPopover(d);
      });

      E.track.addEventListener('mousedown', function (e) {
        if (e.button !== 0 || d.closed) return;
        self._startCreate(d, e);
      });

      E.track.addEventListener('wheel', function (e) {
        if (d.closed) return;
        e.preventDefault();
        if (e.shiftKey) { /* pan vertical avec Shift+molette */
          E.track.scrollTop += e.deltaY > 0 ? 40 : -40;
          return;
        }
        var t = self._timeAt(d, e);
        var k = Math.min(1.6, Math.abs(e.deltaY) / 100 || 1);
        var factor = e.deltaY < 0 ? Math.pow(0.6, k) : Math.pow(1 / 0.6, k);
        var y = e.clientY - E.track.getBoundingClientRect().top;
        self.zoomDay(d, factor, t, y);
      }, { passive: false });

      E.btnAll.addEventListener('click', function () {
        var boxes = E.list.querySelectorAll('input[type=checkbox]');
        var allChecked = true;
        boxes.forEach(function (b) { if (!b.checked) allChecked = false; });
        boxes.forEach(function (b) { b.checked = !allChecked; });
      });

      E.btnOk.addEventListener('click', function () { self._applyCopy(d); });
      E.btnCancel.addEventListener('click', function () { self._closePopovers(); });
    });

    this._onMove = function (e) { self._dragMove(e); };
    this._onUp = function (e) { self._dragEnd(e); };
    this._onDocDown = function (e) {
      var t = e.target;
      while (t && t !== document) {
        if (t.classList && (t.classList.contains('ts-popover') || t.classList.contains('ts-copy'))) return;
        t = t.parentNode;
      }
      self._closePopovers();
    };
    document.addEventListener('mousemove', this._onMove);
    document.addEventListener('mouseup', this._onUp);
    document.addEventListener('mousedown', this._onDocDown);
  };

  /* ---------- coordonnees / zoom ---------- */

  TimeSlider.prototype._timeAt = function (d, e) {
    var E = this._els[d.key];
    var rect = E.track.getBoundingClientRect();
    var scale = E.track.clientHeight / d.view.span;
    return clamp((e.clientY - rect.top + E.track.scrollTop) / scale, 0, DAY_MIN);
  };

  TimeSlider.prototype.zoomDay = function (d, factor, anchorTime, anchorY) {
    var E = this._els[d.key];
    var oldScale = E.track.clientHeight / d.view.span;
    var t = anchorTime != null ? anchorTime : (E.track.scrollTop + E.track.clientHeight / 2) / oldScale;
    var y = anchorY != null ? anchorY : E.track.clientHeight / 2;
    var newSpan = clamp(d.view.span * factor, MIN_SPAN, DAY_MIN);
    if (newSpan === d.view.span) return;
    d.view.span = newSpan;
    this._renderDay(d); /* agrandit d'abord le canvas pour que le scroll ne soit pas clampe */
    var newScale = E.track.clientHeight / newSpan;
    var maxScroll = Math.max(0, DAY_MIN * newScale - E.track.clientHeight);
    E.track.scrollTop = clamp(t * newScale - y, 0, maxScroll);
  };

  /* ---------- creation / manipulation des plages ---------- */

  TimeSlider.prototype._startCreate = function (d, e) {
    e.preventDefault();
    var t = this._timeAt(d, e);
    this._clearSelection(d);
    this.drag = {
      day: d,
      mode: 'create',
      startT: t,
      lastT: t,
      startX: e.clientX,
      startY: e.clientY,
      moved: false,
      /* une seule plage par jour : l'existante est remplacee, on la grise pendant le trace */
      oldRangeEl: d.slots.length ? this._els[d.key].rangeEls[0] : null,
      preview: { start: t, end: t }
    };
    this._layoutPreview(d);
  };

  TimeSlider.prototype._startResize = function (d, i, mode, e) {
    e.preventDefault();
    e.stopPropagation();
    this.drag = {
      day: d,
      mode: mode,
      slotIndex: i,
      rangeEl: this._els[d.key].rangeEls[i],
      startX: e.clientX,
      startY: e.clientY,
      moved: false,
      preview: { start: d.slots[i].start, end: d.slots[i].end }
    };
  };

  TimeSlider.prototype._dragMove = function (e) {
    if (!this.drag) return;
    var d = this.drag.day;
    var t = this._timeAt(d, e);
    var dr = this.drag;

    if (!dr.moved) {
      var dx = e.clientX - dr.startX;
      var dy = e.clientY - dr.startY;
      if (Math.abs(dx) + Math.abs(dy) <= CLICK_THRESHOLD) return;
      dr.moved = true;
      if (dr.rangeEl) dr.rangeEl.classList.add('dragging');
      if (dr.oldRangeEl) dr.oldRangeEl.classList.add('ts-replacing');
    }

    /* creation = accroche large (30 min en vue 24h), deplacement/resize = 15 min */
    var step = (dr.mode === 'create') ? snapStep(d.view.span) : 15;
    var idx = dr.slotIndex;
    var slots = d.slots;

    if (dr.mode === 'create') {
      /* une seule plage par jour : toute la journee est libre, l'existante sera remplacee */
      var s = clamp(Math.round(Math.min(dr.startT, t) / step) * step, 0, DAY_MIN);
      var en = clamp(Math.round(Math.max(dr.startT, t) / step) * step, 0, DAY_MIN);
      dr.preview = { start: s, end: Math.max(s, en) };
    } else if (dr.mode === 'move') {
      /* le DEBUT de la plage suit le curseur : relacher a 7h place le debut a 7h */
      var dur = slots[idx].end - slots[idx].start;
      var prevE = idx > 0 ? slots[idx - 1].end : 0;
      var nextS = idx < slots.length - 1 ? slots[idx + 1].start : DAY_MIN;
      var ns = clamp(Math.round(t / step) * step, prevE, nextS - dur);
      dr.preview = { start: ns, end: ns + dur };
    } else {
      var sl = slots[idx];
      var pe = idx > 0 ? slots[idx - 1].end : 0;
      var nx = idx < slots.length - 1 ? slots[idx + 1].start : DAY_MIN;
      if (dr.mode === 'resize-top') {
        var ns2 = clamp(Math.round(t / step) * step, pe, sl.end - MIN_RANGE);
        dr.preview = { start: ns2, end: sl.end };
      } else {
        var ne2 = clamp(Math.round(t / step) * step, sl.start + MIN_RANGE, nx);
        dr.preview = { start: sl.start, end: ne2 };
      }
    }
    this._layoutPreview(d);
  };

  TimeSlider.prototype._layoutPreview = function (d) {
    var E = this._els[d.key];
    var scale = E.track.clientHeight / d.view.span;
    var p = this.drag.preview;
    var h = Math.max(2, (p.end - p.start) * scale);
    E.preview.style.display = 'block';
    E.preview.style.top = (p.start * scale) + 'px';
    E.preview.style.height = h + 'px';
    var label = E.preview.querySelector('.ts-preview-label');
    label.textContent = fmt(p.start) + ' – ' + fmt(p.end);
    label.style.display = h > 20 ? 'block' : 'none';
  };

  TimeSlider.prototype._dragEnd = function (e) {
    var dr = this.drag;
    if (!dr) return;
    this.drag = null;
    var d = dr.day;
    var E = this._els[d.key];
    E.preview.style.display = 'none';
    if (dr.rangeEl) dr.rangeEl.classList.remove('dragging');
    if (dr.oldRangeEl) dr.oldRangeEl.classList.remove('ts-replacing');

    if (!dr.moved) return; /* simple clic : selection deja gere par le clic */

    if (dr.mode === 'create') {
      var s = dr.preview.start, en = dr.preview.end;
      if (en - s >= MIN_RANGE) {
        /* une seule plage par jour : on remplace l'existante */
        d.slots = [{ start: s, end: en }];
        this._selectIndex(d, 0);
      }
    } else {
      var idx = dr.slotIndex;
      var sl = d.slots[idx];
      if (dr.mode === 'move') {
        sl.start = dr.preview.start;
        sl.end = dr.preview.end;
      } else if (dr.mode === 'resize-top') {
        sl.start = dr.preview.start;
      } else {
        sl.end = dr.preview.end;
      }
      this._selectIndex(d, idx);
    }
    this._syncRanges(d);
    this._renderDay(d);
    this._commit();
  };

  TimeSlider.prototype._bindRange = function (d, rg, i) {
    var self = this;

    rg.addEventListener('mousedown', function (e) {
      if (e.button !== 0 || self.drag || d.closed) return;
      e.preventDefault();
      e.stopPropagation();
      self.drag = {
        day: d,
        mode: 'move',
        slotIndex: i,
        rangeEl: rg,
        startX: e.clientX,
        startY: e.clientY,
        moved: false,
        preview: { start: d.slots[i].start, end: d.slots[i].end }
      };
    });

    rg.addEventListener('click', function (e) {
      if (e.target.classList.contains('ts-range-del')) return;
      self._selectIndex(d, i);
      self._renderDay(d);
    });

    rg.addEventListener('dblclick', function (e) {
      if (e.target.classList.contains('ts-range-del')) return;
      e.preventDefault();
      var sl = d.slots[i];
      var span = clamp((sl.end - sl.start) * 2.2, MIN_SPAN, DAY_MIN);
      var c = (sl.start + sl.end) / 2;
      var E = self._els[d.key];
      d.view.span = span;
      self._renderDay(d); /* agrandit le canvas avant de fixer le scroll */
      var maxScroll = Math.max(0, DAY_MIN * (E.track.clientHeight / span) - E.track.clientHeight);
      E.track.scrollTop = clamp(c * (E.track.clientHeight / span) - E.track.clientHeight / 2, 0, maxScroll);
    });

    rg.querySelector('.ts-handle-top').addEventListener('mousedown', function (e) {
      if (e.button !== 0 || d.closed) return;
      self._startResize(d, i, 'resize-top', e);
    });

    rg.querySelector('.ts-handle-bottom').addEventListener('mousedown', function (e) {
      if (e.button !== 0 || d.closed) return;
      self._startResize(d, i, 'resize-bottom', e);
    });

    rg.querySelector('.ts-range-del').addEventListener('mousedown', function (e) {
      e.stopPropagation(); /* ne pas demarrer un deplacement en cliquant sur la croix */
    });

    rg.querySelector('.ts-range-del').addEventListener('click', function (e) {
      e.stopPropagation();
      d.slots.splice(i, 1);
      self._selectIndex(d, -1);
      self._syncRanges(d);
      self._renderDay(d);
      self._commit();
    });
  };

  /* ---------- rendu ---------- */

  TimeSlider.prototype._syncRanges = function (d) {
    var E = this._els[d.key];
    while (E.rangeEls.length > d.slots.length) {
      E.rangeEls.pop().remove();
    }
    for (var i = 0; i < d.slots.length; i++) {
      var rg = E.rangeEls[i];
      if (!rg) {
        rg = el('div', 'ts-range');
        rg.title = 'Glisser pour déplacer · poignées pour allonger/raccourcir';
        rg.appendChild(el('div', 'ts-handle ts-handle-top'));
        rg.appendChild(el('span', 'ts-range-label', ''));
        rg.appendChild(el('div', 'ts-handle ts-handle-bottom'));
        rg.appendChild(el('button', 'ts-range-del', '×'));
        E.canvas.appendChild(rg);
        E.rangeEls[i] = rg;
        this._bindRange(d, rg, i);
      }
    }
  };

  TimeSlider.prototype._renderDay = function (d) {
    var E = this._els[d.key];
    var span = d.view.span;
    var scale = E.track.clientHeight / span;
    var lstep = labelStep(span);
    var minor = lstep / 2;

    E.col.classList.toggle('is-closed', d.closed);
    if (d.closed) {
      E.summary.textContent = 'Fermé';
    } else if (!d.slots.length) {
      E.summary.textContent = '—';
    } else {
      E.summary.textContent = d.slots.map(function (s) {
        return fmt(s.start) + '–' + fmt(s.end);
      }).join(' · ');
    }

    E.canvas.style.height = (DAY_MIN * scale) + 'px';

    var majorCount = Math.floor(DAY_MIN / lstep) + 1;
    var minorCount = Math.floor(DAY_MIN / minor) + 1;
    var g = E.grid;
    if (!g || g.major !== majorCount || g.minor !== minorCount || g.step !== lstep) {
      if (g) g.all.forEach(function (n) { n.remove(); });
      g = { major: majorCount, minor: minorCount, step: lstep, all: [], majors: [], labels: [] };
      var frag = document.createDocumentFragment();
      for (var m = 0; m <= DAY_MIN; m += minor) {
        var line = el('div', 'ts-gridline ' + (m % lstep === 0 ? 'major' : 'minor'));
        frag.appendChild(line);
        g.all.push(line);
        if (m % lstep === 0) g.majors.push(line);
      }
      for (var h = 0; h <= DAY_MIN; h += lstep) {
        var lb = el('div', 'ts-timelabel', fmt(h));
        frag.appendChild(lb);
        g.all.push(lb);
        g.labels.push({ el: lb, t: h });
      }
      E.canvas.appendChild(frag);
      E.grid = g;
    }
    g.majors.forEach(function (line, i) { line.style.top = (i * lstep * scale) + 'px'; });
    g.labels.forEach(function (lb) { lb.el.style.top = (lb.t * scale) + 'px'; });

    d.slots.forEach(function (sl, i) {
      var rg = E.rangeEls[i];
      if (!rg) return;
      var top = sl.start * scale;
      var h = Math.max(4, (sl.end - sl.start) * scale);
      rg.style.top = top + 'px';
      rg.style.height = h + 'px';
      rg.classList.toggle('selected', d.selected === i);
      var lab = rg.querySelector('.ts-range-label');
      lab.style.display = h > 26 ? 'block' : 'none';
      lab.textContent = fmt(sl.start) + ' – ' + fmt(sl.end);
    });
  };

  TimeSlider.prototype._selectIndex = function (d, i) {
    d.selected = i;
  };

  TimeSlider.prototype._clearSelection = function (d) {
    d.selected = -1;
  };

  /* ---------- copie entre jours ---------- */

  TimeSlider.prototype._openPopover = function (d) {
    this._closePopovers();
    var E = this._els[d.key];
    E.list.innerHTML = '';
    this.days.forEach(function (other) {
      if (other.key === d.key) return;
      var lab = el('label', 'ts-popover-item');
      var cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.value = other.key;
      lab.appendChild(cb);
      lab.appendChild(document.createTextNode(other.label));
      E.list.appendChild(lab);
    });
    var popover = E.popover;
    popover.style.display = 'block';
    var r = E.btnCopy.getBoundingClientRect();
    var width = popover.offsetWidth;
    var left = r.left;
    if (left + width > window.innerWidth - 8) left = window.innerWidth - width - 8;
    popover.style.position = 'fixed';
    popover.style.top = (r.bottom + 4) + 'px';
    popover.style.left = Math.max(8, left) + 'px';
    popover.style.right = 'auto';
    popover.style.zIndex = '9999';
    var self = this;
    var onViewport = function () { self._closePopovers(); };
    this._popoverCleanup = onViewport;
    window.addEventListener('scroll', onViewport, true);
    window.addEventListener('resize', onViewport);
  };

  TimeSlider.prototype._closePopovers = function () {
    var self = this;
    this.days.forEach(function (d) { self._els[d.key].popover.style.display = 'none'; });
    if (this._popoverCleanup) {
      window.removeEventListener('scroll', this._popoverCleanup, true);
      window.removeEventListener('resize', this._popoverCleanup);
      this._popoverCleanup = null;
    }
  };

  TimeSlider.prototype._applyCopy = function (src) {
    var E = this._els[src.key];
    var dests = [];
    E.list.querySelectorAll('input:checked').forEach(function (b) {
      var dd = null;
      this.days.forEach(function (x) { if (x.key === b.value) dd = x; });
      if (dd) dests.push(dd);
    }, this);
    if (!dests.length) {
      this._closePopovers();
      return;
    }
    var cloned = src.slots.map(function (s) { return { start: s.start, end: s.end }; });
    var closed = src.closed;
    var self = this;
    dests.forEach(function (dd) {
      dd.closed = closed;
      dd.slots = cloned.map(function (s) { return { start: s.start, end: s.end }; });
      dd.selected = -1;
      self._els[dd.key].closedInput.checked = closed;
      self._syncRanges(dd);
      self._renderDay(dd);
    });
    this._closePopovers();
    this._commit();
  };

  /* ---------- API publique ---------- */

  TimeSlider.prototype.getValue = function () {
    var out = {};
    this.days.forEach(function (d) {
      out[d.key] = {
        closed: d.closed,
        slots: d.slots.map(function (s) { return [fmt(s.start), fmt(s.end)]; })
      };
    });
    return out;
  };

  TimeSlider.prototype.setValue = function (v) {
    var self = this;
    this.days.forEach(function (d) {
      var item = v && v[d.key] ? v[d.key] : { closed: false, slots: [] };
      d.closed = !!item.closed;
      d.slots = (item.slots || []).map(function (pair) {
        var s = parse(pair[0]);
        var e = parse(pair[1]);
        if (s == null || e == null || e <= s) return null;
        return {
          start: clamp(s, 0, DAY_MIN - MIN_RANGE),
          end: clamp(e, MIN_RANGE, DAY_MIN)
        };
      }).filter(Boolean).sort(function (a, b) { return a.start - b.start; });
      /* une seule plage par jour : on garde la premiere */
      if (d.slots.length > 1) d.slots = d.slots.slice(0, 1);
      d.selected = -1;
      self._els[d.key].closedInput.checked = d.closed;
      self._syncRanges(d);
      self._renderDay(d);
    });
  };

  TimeSlider.prototype._commit = function () {
    var v = this.getValue();
    this.root.dispatchEvent(new CustomEvent('change', { detail: v }));
    if (typeof this.opts.onChange === 'function') this.opts.onChange(v);
  };

  TimeSlider.prototype.destroy = function () {
    if (this._onMove) document.removeEventListener('mousemove', this._onMove);
    if (this._onUp) document.removeEventListener('mouseup', this._onUp);
    if (this._onDocDown) document.removeEventListener('mousedown', this._onDocDown);
    this.root.classList.remove('ts-widget');
    this.root.innerHTML = '';
  };

  global.TimeSlider = TimeSlider;
})(typeof window !== 'undefined' ? window : this);
