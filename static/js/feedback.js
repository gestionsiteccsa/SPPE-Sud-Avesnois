/* =====================================================================
   feedback.js — Bouton fixe + <dialog> de signalement.
   Vanilla JS (même pattern que nav.js/confirm.js), compatible CSP nonce
   via le bundle. Progressive enhancement : sans JS, le formulaire POST
   classique vers feedback:submit reste fonctionnel.
   ===================================================================== */
(function () {
  "use strict";

  function currentPath() {
    try {
      var path = window.location.pathname || "/";
      var search = window.location.search || "";
      var full = path + search;
      return full.slice(0, 500);
    } catch (e) {
      return "/";
    }
  }

  function showStatus(box, kind, text) {
    if (!box) return;
    box.hidden = false;
    box.textContent = text;
    box.setAttribute("data-kind", kind || "info");
  }

  function init() {
    var openBtn = document.querySelector("[data-feedback-open]");
    var dialog = document.getElementById("feedback-dialog");
    if (!openBtn || !dialog) return;
    if (typeof dialog.showModal !== "function") {
      // Navigateur très ancien sans <dialog> : le formulaire reste
      // accessible via la page dédiée.
      openBtn.addEventListener("click", function () {
        window.location.href = "/feedback/signaler/";
      });
      return;
    }

    var form = dialog.querySelector("[data-feedback-form]");
    var pageInput = dialog.querySelector("[data-feedback-page]");
    var contextInput = dialog.querySelector("[data-feedback-context]");
    var nextInput = dialog.querySelector("[data-feedback-next]");
    var statusBox = dialog.querySelector("[data-feedback-status]");
    var submitBtn = dialog.querySelector("[data-feedback-submit]");
    var cancelBtn = dialog.querySelector("[data-feedback-cancel]");
    var lastFocus = null;

    function prefill() {
      var here = currentPath();
      if (contextInput) contextInput.value = here;
      if (nextInput && !nextInput.value) nextInput.value = here;
      // Pré-remplit seulement si vide ou encore à la valeur précédente,
      // pour ne pas écraser un choix manuel en cas de réouverture.
      if (pageInput && !pageInput.value) pageInput.value = here;
    }

    function open() {
      lastFocus = document.activeElement;
      prefill();
      if (statusBox) {
        statusBox.hidden = true;
        statusBox.textContent = "";
      }
      dialog.showModal();
      var target = dialog.querySelector("#feedback-message") || pageInput;
      if (target && typeof target.focus === "function") target.focus();
    }

    function close(restoreFocus) {
      if (dialog.open) dialog.close();
      if (restoreFocus !== false && lastFocus && typeof lastFocus.focus === "function") {
        lastFocus.focus();
      }
    }

    openBtn.addEventListener("click", open);
    if (cancelBtn) cancelBtn.addEventListener("click", function () { close(true); });
    dialog.addEventListener("click", function (event) {
      // Clic sur le backdrop natif : event.target est le <dialog> lui-même.
      if (event.target === dialog) close(true);
    });

    if (!form) return;
    form.addEventListener("submit", function (event) {
      // Si fetch indisponible, laisse le POST classique faire son travail.
      if (typeof window.fetch !== "function" || typeof window.FormData !== "function") {
        return;
      }
      event.preventDefault();
      if (statusBox) {
        statusBox.hidden = true;
        statusBox.textContent = "";
      }
      if (submitBtn) submitBtn.disabled = true;

      var data = new FormData(form);
      // Garantit le contexte courant même si le champ caché est vide.
      if (contextInput && !contextInput.value) contextInput.value = currentPath();
      data.set("page_contexte", contextInput ? contextInput.value : currentPath());

      fetch(form.action, {
        method: "POST",
        body: data,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          Accept: "application/json",
        },
        credentials: "same-origin",
      }).then(function (response) {
        if (response.status === 403) {
          throw new Error("session-expired");
        }
        return response.json().then(function (payload) {
          return { status: response.status, payload: payload };
        });
      }).then(function (result) {
        if (result.status === 201 && result.payload && result.payload.ok) {
          showStatus(statusBox, "success", "Merci ! Votre signalement a bien été envoyé.");
          form.reset();
          window.setTimeout(function () { close(true); }, 900);
        } else if (result.payload && result.payload.errors) {
          var parts = [];
          Object.keys(result.payload.errors).forEach(function (key) {
            var list = result.payload.errors[key] || [];
            list.forEach(function (item) {
              var text = item && item.message ? item.message : String(item);
              parts.push(text);
            });
          });
          showStatus(
            statusBox,
            "error",
            parts.length ? parts.join(" ") : "Le formulaire contient des erreurs."
          );
          var firstInvalid = form.querySelector("[name='message'], [name='page_declaree']");
          if (firstInvalid && typeof firstInvalid.focus === "function") firstInvalid.focus();
        } else {
          showStatus(statusBox, "error", "Envoi impossible. Réessayez dans un instant.");
        }
      }).catch(function (err) {
        if (err && err.message === "session-expired") {
          showStatus(
            statusBox,
            "error",
            "Votre session a expiré. Reconnectez-vous, votre texte est conservé."
          );
        } else {
          showStatus(statusBox, "error", "Envoi impossible. Vérifiez votre connexion.");
        }
      }).then(function () {
        if (submitBtn) submitBtn.disabled = false;
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
