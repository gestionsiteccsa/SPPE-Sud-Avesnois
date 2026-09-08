/* =====================================================================
   opening-days.js — Modale des structures ouvertes par jour (dashboard).
   Vanilla JS (même pattern que feedback.js), compatible CSP nonce via
   le bundle. Progressive enhancement : sans JS, les compteurs par jour
   restent lisibles dans le <details> ; la liste détaillée demande JS.
   ===================================================================== */
(function () {
  "use strict";

  var MAX_SHOWN = 200;

  function showStatus(box, text) {
    if (!box) return;
    if (!text) {
      box.hidden = true;
      box.textContent = "";
      return;
    }
    box.hidden = false;
    box.textContent = text;
  }

  function clearList(list) {
    while (list.firstChild) {
      list.removeChild(list.firstChild);
    }
  }

  function buildRow(item) {
    var li = document.createElement("li");
    li.className = "py-3 first:pt-0 last:pb-0";

    var link = document.createElement("a");
    link.className =
      "font-semibold text-[var(--color-text)] no-underline hover:text-[var(--color-primary-hover)] hover:underline";
    link.textContent = item.nom || "Structure sans nom";
    // URL construite côté serveur (reverse), jamais depuis une donnée utilisateur.
    link.setAttribute("href", item.url);

    var meta = document.createElement("p");
    meta.className = "text-[length:var(--fs-xs)] text-[var(--color-text-muted)] mt-1 mb-0";
    var details = [];
    if (item.type) details.push(item.type);
    if (item.commune) details.push(item.commune);
    if (item.horaires) details.push(item.horaires);
    meta.textContent = details.join(" · ") || "Informations non renseignées";

    var wrapper = document.createElement("div");
    wrapper.className = "min-w-0";
    wrapper.appendChild(link);
    wrapper.appendChild(meta);

    var row = document.createElement("div");
    row.className = "flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2";
    row.appendChild(wrapper);

    if (item.masquee) {
      var badge = document.createElement("span");
      badge.className =
        "inline-flex self-start sm:self-center px-2 py-0.5 rounded-[var(--radius-sm)] bg-[var(--color-warning-soft)] text-[var(--color-warning)] text-[length:var(--fs-xs)] font-semibold";
      badge.textContent = "Masquée";
      row.appendChild(badge);
    }

    li.appendChild(row);
    return li;
  }

  function init() {
    var dialog = document.getElementById("opening-day-dialog");
    if (!dialog) return;
    var buttons = document.querySelectorAll("[data-opening-day]");
    if (!buttons.length) return;

    // Navigateur très ancien sans <dialog> : on reste sur les compteurs,
    // en renvoyant vers la liste des structures plutôt qu'un JSON brut.
    if (typeof dialog.showModal !== "function") {
      return;
    }

    var title = dialog.querySelector("#opening-day-title");
    var list = dialog.querySelector("[data-opening-list]");
    var statusBox = dialog.querySelector("[data-opening-status]");
    var moreBox = dialog.querySelector("[data-opening-more]");
    if (!list) return;

    var lastFocus = null;
    var currentRequest = null;
    var requestSeq = 0;

    function close(restoreFocus) {
      if (currentRequest && typeof currentRequest.abort === "function") {
        currentRequest.abort();
        currentRequest = null;
      }
      if (dialog.open) dialog.close();
      if (restoreFocus !== false && lastFocus && typeof lastFocus.focus === "function") {
        lastFocus.focus();
      }
    }

    function open(button) {
      var label = button.getAttribute("data-opening-label") || "le jour sélectionné";
      var url = button.getAttribute("data-opening-url");
      if (!url) return;
      lastFocus = document.activeElement;
      requestSeq += 1;
      var seq = requestSeq;

      if (title) title.textContent = "Structures ouvertes le " + label.toLowerCase();
      clearList(list);
      if (moreBox) moreBox.hidden = true;
      showStatus(statusBox, "Chargement de la liste…");
      if (!dialog.open) dialog.showModal();
      if (title && typeof title.focus === "function") title.focus();

      if (typeof window.fetch !== "function") {
        showStatus(statusBox, "Votre navigateur ne permet pas de charger cette liste.");
        return;
      }

      if (currentRequest && typeof currentRequest.abort === "function") {
        currentRequest.abort();
      }
      var controller = null;
      if (typeof window.AbortController === "function") {
        controller = new AbortController();
        currentRequest = controller;
      }

      fetch(url, {
        method: "GET",
        headers: { "X-Requested-With": "XMLHttpRequest", Accept: "application/json" },
        credentials: "same-origin",
        signal: controller ? controller.signal : undefined,
      })
        .then(function (response) {
          if (response.status === 403) throw new Error("session-expired");
          if (response.status === 404) throw new Error("unknown-day");
          if (!response.ok) throw new Error("http-error");
          return response.json();
        })
        .then(function (payload) {
          // Ignore une réponse arrivée après une demande plus récente.
          if (seq !== requestSeq) return;
          currentRequest = null;
          var results = (payload && payload.results) || [];
          var total = payload && typeof payload.total === "number" ? payload.total : results.length;
          if (!results.length) {
            showStatus(statusBox, "Aucune structure ouverte " + label.toLowerCase() + ".");
            return;
          }
          showStatus(statusBox, null);
          var shown = 0;
          results.slice(0, MAX_SHOWN).forEach(function (item) {
            if (!item || !item.url) return;
            list.appendChild(buildRow(item));
            shown += 1;
          });
          if ((payload && payload.truncated) || total > shown) {
            if (moreBox) {
              moreBox.hidden = false;
              moreBox.textContent =
                "Affichage des " + shown + " premières sur " + total + " structures.";
            }
          }
        })
        .catch(function (err) {
          if (err && err.name === "AbortError") return;
          if (seq !== requestSeq) return;
          currentRequest = null;
          if (err && err.message === "session-expired") {
            showStatus(statusBox, "Votre session a expiré. Reconnectez-vous puis réessayez.");
          } else if (err && err.message === "unknown-day") {
            showStatus(statusBox, "Ce jour est inconnu. Fermez puis réessayez.");
          } else {
            showStatus(statusBox, "Chargement impossible. Vérifiez votre connexion puis réessayez.");
          }
        });
    }

    Array.prototype.forEach.call(buttons, function (button) {
      button.addEventListener("click", function () {
        open(button);
      });
    });

    dialog.addEventListener("click", function (event) {
      // Clic sur le backdrop natif : event.target est le <dialog> lui-même.
      if (event.target === dialog) close(true);
    });
    dialog.addEventListener("close", function () {
      if (currentRequest && typeof currentRequest.abort === "function") {
        currentRequest.abort();
        currentRequest = null;
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
