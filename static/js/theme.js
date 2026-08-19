/* =====================================================================
   theme.js — Bascule clair / sombre, persistance localStorage.
   Conforme RGAA : aucun visuel dépendant uniquement de JS.
   Pré-applique data-theme avant le rendu via script inline (voir base.html).
   ===================================================================== */
(function () {
  "use strict";

  var STORAGE_KEY = "bddpe-theme";

  function getStoredTheme() {
    try { return localStorage.getItem(STORAGE_KEY); }
    catch (e) { return null; }
  }

  function storeTheme(theme) {
    try { localStorage.setItem(STORAGE_KEY, theme); }
    catch (e) { /* mode privée : on ignore */ }
  }

  function systemTheme() {
    return window.matchMedia &&
           window.matchMedia("(prefers-color-scheme: dark)").matches
           ? "dark" : "light";
  }

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") || systemTheme();
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    syncToggleButtons(theme);
  }

  function syncToggleButtons(theme) {
    var buttons = document.querySelectorAll("[data-theme-toggle]");
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      var pressed = (theme === "dark");
      btn.setAttribute("aria-pressed", pressed ? "true" : "false");
      btn.setAttribute("aria-label",
        pressed ? "Activer le thème clair" : "Activer le thème sombre");
      btn.setAttribute("title",
        pressed ? "Thème sombre actif — basculer vers le thème clair"
                : "Thème clair actif — basculer vers le thème sombre");
    }
  }

  function toggleTheme() {
    var next = currentTheme() === "dark" ? "light" : "dark";
    applyTheme(next);
    storeTheme(next);
  }

  // Suivi des préférences système si l'utilisateur n'a rien forcé.
  function bindSystemListener() {
    if (!window.matchMedia) return;
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    var handler = function () {
      if (!getStoredTheme()) { applyTheme(systemTheme()); }
    };
    if (mq.addEventListener) mq.addEventListener("change", handler);
    else if (mq.addListener) mq.addListener(handler);
  }

  // Branchement des boutons toggle.
  function bindToggles() {
    var buttons = document.querySelectorAll("[data-theme-toggle]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener("click", toggleTheme);
    }
  }

  function init() {
    syncToggleButtons(currentTheme());
    bindToggles();
    bindSystemListener();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();