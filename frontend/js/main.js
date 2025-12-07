/**
 * SalesQuest - Frontend JavaScript
 */

// API no VPS (produção) ou local (desenvolvimento)
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5200/api'
    : 'http://212.85.23.66:5200/api';

// ================================
// UTILITÁRIOS
// ================================

async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Erro na API:', error);
        return null;
    }
}

function formatarNumero(numero) {
    return new Intl.NumberFormat('pt-BR').format(numero);
}

function formatarDinheiro(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// ================================
// CARREGAR STATS GERAIS
// ================================

async function carregarStatsGerais() {
    const data = await fetchAPI('/stats/geral');

    if (!data) return;

    document.getElementById('total-vendedores').textContent = data.total_vendedores;
    document.getElementById('total-leads').textContent = formatarNumero(data.hoje.leads);
    document.getElementById('total-entrevistas').textContent = formatarNumero(data.hoje.entrevistas);
    document.getElementById('total-vendas').textContent = formatarNumero(data.hoje.vendas);
}

// ================================
// CARREGAR RANKING
// ================================

async function carregarRanking(periodo = 'dia') {
    const data = await fetchAPI(`/ranking?periodo=${periodo}`);

    if (!data || !data.ranking) return;

    const ranking = data.ranking;

    // Atualiza pódio (top 3)
    for (let i = 1; i <= 3; i++) {
        const podioEl = document.getElementById(`podio-${i}`);
        if (ranking[i - 1]) {
            const vendedor = ranking[i - 1];
            podioEl.querySelector('.podio-avatar').textContent = vendedor.avatar;
            podioEl.querySelector('.podio-nome').textContent = vendedor.nome;
            podioEl.querySelector('.podio-pontos').textContent = `${formatarNumero(vendedor.pontos_periodo)} XP`;
        } else {
            podioEl.querySelector('.podio-avatar').textContent = '❓';
            podioEl.querySelector('.podio-nome').textContent = '-';
            podioEl.querySelector('.podio-pontos').textContent = '0 XP';
        }
    }

    // Atualiza ranking completo (a partir do 4º)
    const rankingList = document.getElementById('ranking-list');
    rankingList.innerHTML = '';

    if (ranking.length > 3) {
        for (let i = 3; i < ranking.length; i++) {
            const vendedor = ranking[i];
            const item = criarItemRanking(vendedor);
            rankingList.appendChild(item);
        }
    } else {
        rankingList.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">Nenhum vendedor além do top 3</p>';
    }
}

function criarItemRanking(vendedor) {
    const div = document.createElement('div');
    div.className = 'ranking-item fade-in';
    div.innerHTML = `
        <div class="ranking-posicao">#${vendedor.posicao}</div>
        <div class="ranking-avatar">${vendedor.avatar}</div>
        <div class="ranking-info">
            <div class="ranking-nome">${vendedor.nome}</div>
            <div class="ranking-nivel">Nível ${vendedor.nivel} · ${formatarNumero(vendedor.xp_total)} XP total</div>
        </div>
        <div class="ranking-pontos">${formatarNumero(vendedor.pontos_periodo)} XP</div>
    `;
    return div;
}

// ================================
// TABS DE PERÍODO
// ================================

function configurarTabs() {
    const tabs = document.querySelectorAll('.periodo-tab');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active de todos
            tabs.forEach(t => t.classList.remove('active'));

            // Adiciona active no clicado
            tab.classList.add('active');

            // Carrega ranking do período
            const periodo = tab.dataset.periodo;
            carregarRanking(periodo);
        });
    });
}

// ================================
// INICIALIZAÇÃO
// ================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎮 SalesQuest carregado!');

    // Carrega dados iniciais
    await carregarStatsGerais();
    await carregarRanking('dia');

    // Configura tabs
    configurarTabs();

    // Atualiza a cada 30 segundos
    setInterval(() => {
        carregarStatsGerais();

        // Pega período ativo
        const periodoAtivo = document.querySelector('.periodo-tab.active').dataset.periodo;
        carregarRanking(periodoAtivo);
    }, 30000);
});
