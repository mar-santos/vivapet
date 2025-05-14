document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.querySelector('.login-form');

    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const senha = document.getElementById('senha').value;

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, senha })
            });

            const data = await response.json();

            if (response.ok) {
                alert("Login realizado com sucesso!");
                // Verifique a estrutura correta da resposta
                localStorage.setItem('access_token', data.access_token);
                window.location.href = "/dashboard";
            } else {
                alert(`Erro: ${data.message}`);
                console.error('Erro:', data.message);
            }
        } catch (error) {
            alert('Erro ao tentar fazer login.');
            console.error('Erro:', error);
        }
    });
});