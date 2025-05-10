// src/components/navbar.js

function renderNavbar() {
    return `
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/src/assets/images/logo.png" alt="PetSystem Logo" height="40">
                PetSystem
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarMain" aria-controls="navbarMain" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarMain">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Início</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/servicos">Serviços</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/agendamentos">Agendamentos</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/pets">Meus Pets</a>
                    </li>
                </ul>
                <div class="d-flex">
                    <a href="/login" class="btn btn-outline-primary me-2">Login</a>
                    <a href="/usuarios/novo" class="btn btn-primary">Cadastre-se</a>
                </div>
            </div>
        </div>
    </nav>
    `;
}