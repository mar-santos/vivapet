document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('usuariosForm');
    const messageDiv = document.getElementById('message');
    const fotoInput = document.getElementById('foto_user');
    const avatarPreview = document.getElementById('avatarPreview');
    const defaultAvatar = "/static/src/assets/images/imagem_usuario.png";

    // Preview da imagem de perfil
    if (fotoInput && avatarPreview) {
        fotoInput.addEventListener('change', function () {
            const file = fotoInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    avatarPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            } else {
                avatarPreview.src = defaultAvatar;
            }
        });
    }

    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = new FormData(form);

            try {
                const resp = await fetch('http://localhost:5000/api/usuarios', {
                    method: 'POST',
                    body: formData
                });
                const data = await resp.json();
                if (resp.ok) {
                    messageDiv.style.color = "#0c8b45";
                    messageDiv.textContent = "Usuário cadastrado com sucesso!";
                    form.reset();

                    if (avatarPreview) {
                        avatarPreview.src = defaultAvatar;
                    }
                    if (fotoInput) {
                        fotoInput.value = "";
                    }
                } else {
                    messageDiv.style.color = "#ed2020";
                    messageDiv.textContent = 'Erro: ' + (data.errors ? Object.values(data.errors).join(', ') : data.message || "Erro ao cadastrar.");
                }
            } catch (err) {
                messageDiv.style.color = "#ed2020";
                messageDiv.textContent = "Erro de conexão. Tente novamente.";
            }
        });
    }
});