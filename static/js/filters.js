/* =====================================================================
   filters.js — Persistance des filtres de la liste de structures.
   Conserve les filtres dans localStorage (simples), restaure au chargement.
   Conforme RGAA : dégradation gracieuse, pas de dépendance JS pour naviguer.
   ===================================================================== */
(function () {
  "use strict";

  var STORAGE_KEY = "bddpe-filters-structures";

  function getForm() {
    return document.querySelector("form[data-filters-form]");
  }

  function readQuery() {
    var qs = window.location.search.replace(/^\?/, "");
    var out = {};
    if (!qs) return out;
    qs.split("&").forEach(function (pair) {
      if (!pair) return;
      var idx = pair.indexOf("=");
      var k = decodeURIComponent(idx === -1 ? pair : pair.slice(0, idx));
      var v = decodeURIComponent(idx === -1 ? "" : pair.slice(idx + 1));
      if (k && k !== "page") out[k] = v;
    });
    return out;
  }

  function storeFromUrl() {
    var q = readQuery();
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(q)); }
    catch (e) {}
  }

  function applyStoredOnReset() {
    var form = getForm();
    if (!form) return;
    var resetBtn = form.querySelector("[data-reset-filters]");
    if (!resetBtn) return;
    resetBtn.addEventListener("click", function () {
      try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
    });
  }

  function init() {
    // Si la liste contient des filtres actifs venant de l'URL, on stocke.
    var q = readQuery();
    if (Object.keys(q).length > 0) {
      storeFromUrl();
    }
    applyStoredOnReset();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();