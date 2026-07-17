document.addEventListener("click", function (evento) {
    const botaoAbrir = evento.target.closest("[data-open-modal]");
    if (botaoAbrir) {
        const modal = document.getElementById(botaoAbrir.dataset.openModal);
        if (modal) abrirModal(modal);
    }

    const botaoFechar = evento.target.closest("[data-close-modal]");
    if (botaoFechar) {
        const modal = botaoFechar.closest(".modal-overlay");
        if (modal) fecharModal(modal);
    }

    if (evento.target.classList.contains("modal-overlay")) {
        fecharModal(evento.target);
    }
});

document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape") {
        const modalAberto = document.querySelector(".modal-overlay.ativo");
        if (modalAberto) fecharModal(modalAberto);
    }
});

function abrirModal(modal) {
    modal.classList.add("ativo");
    document.body.classList.add("modal-aberto");
}

function fecharModal(modal) {
    modal.classList.remove("ativo");
    document.body.classList.remove("modal-aberto");
}
