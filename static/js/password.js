/* =====================================================================
   password.js — Bascule de visibilité des champs mot de passe.
   Conforme RGAA : aria-pressed sur bouton, état reflété sur l'input
   (type password/text) ET sur la label accessible.
   ===================================================================== */
(function () {
  "use strict";

  function setupToggle(btn) {
    var group = btn.parentElement;
    var input = group ? group.querySelector("input") : null;
    if (!input || !btn) return;

    var icons = btn.querySelectorAll("svg");
    var iconOn = icons.length > 0 ? icons[0] : null;
    var iconOff = icons.length > 1 ? icons[1] : null;
    var labelOn = btn.getAttribute("data-label-show") || "Afficher le mot de passe";
    var labelOff = btn.getAttribute("data-label-hide") || "Masquer le mot de passe";

    btn.setAttribute("aria-pressed", "false");
    btn.setAttribute("aria-label", labelOn);

    btn.addEventListener("click", function () {
      var reveal = btn.getAttribute("aria-pressed") !== "true";
      input.type = reveal ? "text" : "password";
      btn.setAttribute("aria-pressed", reveal ? "true" : "false");
      btn.setAttribute("aria-label", reveal ? labelOff : labelOn);
      if (iconOn && iconOff) {
        iconOn.classList.toggle("hidden", reveal);
        iconOff.classList.toggle("hidden", !reveal);
      }
      // Replacer le curseur dans le champ pour reprendre immédiatement la saisie.
      try { var len = input.value.length; input.focus(); input.setSelectionRange(len, len); } catch (e) {}
    });
  }

  function init() {
    var buttons = document.querySelectorAll("[data-password-toggle]");
    for (var i = 0; i < buttons.length; i++) setupToggle(buttons[i]);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
