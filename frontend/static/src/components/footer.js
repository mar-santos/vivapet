// src/components/footer.js

function renderFooter() {
    const year = new Date().getFullYear();
    
    return `
    <footer class="bg-light py-4 mt-5 border-top">
        <div class="container">
            <div class="row">
                <div class="col-md-4 mb-3 mb-md-0">
                    <h5>PetSystem</h5>
                    <p class="text-muted">Cuidados com amor e profissionalismo para seu melhor amigo.</p>
                </div>
                <div class="col-md-4 mb-3 mb-md-0">
                    <h5>Links Rápidos</h5>
                    <ul class="list-unstyled">
                        <li><a href="/servicos">Nossos Serviços</a></li>
                        <li><a href="/agendamentos">Agende uma Consulta</a></li>
                        <li><a href="/contato">Contato</a></li>
                    </ul>
                </div>
                <div class="col-md-4">
                    <h5>Contato</h5>
                    <ul class="list-unstyled">
                        <li><i class="fas fa-map-marker-alt me-2"></i> Rua dos Animais, 123</li>
                        <li><i class="fas fa-phone me-2"></i> (11) 99999-9999</li>
                        <li><i class="fas fa-envelope me-2"></i> contato@petsystem.com</li>
                    </ul>
                    <div class="mt-3">
                        <a href="#" class="text-decoration-none me-2"><i class="fab fa-facebook-f"></i></a>
                        <a href="#" class="text-decoration-none me-2"><i class="fab fa-instagram"></i></a>
                        <a href="#" class="text-decoration-none me-2"><i class="fab fa-twitter"></i></a>
                    </div>
                </div>
            </div>
            <hr>
            <div class="text-center">
                <p class="mb-0 text-muted">© ${year} PetSystem. Todos os direitos reservados.</p>
            </div>
        </div>
    </footer>
    `;
}