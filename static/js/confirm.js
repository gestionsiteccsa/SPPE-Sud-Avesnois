/* =====================================================================
   confirm.js — Confirmation avant soumission des formulaires marqués
   data-confirm="message". Respecte l'accessibilité : focus après
   annulation et attribution aria sur le bouton.
   ===================================================================== */
(function () {
  "use strict";

  function init() {
    var forms = document.querySelectorAll("form[data-confirm]");
    for (var i = 0; i < forms.length; i++) {
      (function (form) {
        var message = form.getAttribute("data-confirm");
        form.addEventListener("submit", function (event) {
          if (!window.confirm(message)) {
            event.preventDefault();
            var button = form.querySelector("button[type='submit']");
            if (button) button.focus();
          }
        });
      })(forms[i]);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
