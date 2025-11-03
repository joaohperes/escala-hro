document.addEventListener('DOMContentLoaded', () => {
    const now = new Date();
    const formatted = now.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    document.getElementById('ultima-atualizacao').textContent = `Última atualização: ${formatted}`;
});

// Refresh a cada 30 minutos
setInterval(() => {
    location.reload();
}, 1800000);
