/**
 * SalesQuest - Frontend JavaScript
 * Sistema de gamificação comercial completo
 */

// API via HTTPS (Traefik)
const API_URL = 'https://salesquest-api.agenciacafeonline.com.br/api';

// Estado global
let vendedoresCache = [];

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

function esconderLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        setTimeout(() => {
            loading.style.opacity = '0';
            setTimeout(() => {
                loading.style.display = 'none';
            }, 300);
        }, 500);
    }
}

// ================================
// NAVEGAÇÃO ENTRE PÁGINAS
// ================================

function configurarNavegacao() {
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            // Remove active de todos os links
            navLinks.forEach(l => l.classList.remove('active'));

            // Adiciona active no link clicado
            link.classList.add('active');

            // Esconde todas as páginas
            pages.forEach(p => p.classList.remove('active'));

            // Mostra página correspondente
            const pageName = link.dataset.page;
            const targetPage = document.getElementById(`page-${pageName}`);

            if (targetPage) {
                targetPage.classList.add('active');

                // Carrega dados específicos da página
                if (pageName === 'vendedores' && vendedoresCache.length === 0) {
                    carregarVendedores();
                } else if (pageName === 'missoes') {
                    carregarMissoes();
                } else if (pageName === 'coach') {
                    preencherSelectVendedores();
                } else if (pageName === 'analise') {
                    preencherSelectAnalise();
                }
            }
        });
    });
}

// ================================
// CARREGAR STATS GERAIS
// ================================

async function carregarStatsGerais() {
    const data = await fetchAPI('/stats/geral');

    if (!data) return;

    // Anima contadores
    animarContador('total-vendedores', data.total_vendedores);
    animarContador('total-leads', data.hoje.leads);
    animarContador('total-entrevistas', data.hoje.entrevistas);
    animarContador('total-vendas', data.hoje.vendas);
}

function animarContador(elementId, valorFinal) {
    const elemento = document.getElementById(elementId);
    if (!elemento) return;

    const valorAtual = parseInt(elemento.textContent) || 0;
    const diferenca = valorFinal - valorAtual;
    const duracao = 1000; // ms
    const passos = 20;
    const incremento = diferenca / passos;
    let contador = 0;

    const interval = setInterval(() => {
        contador++;
        const novoValor = Math.round(valorAtual + (incremento * contador));
        elemento.textContent = formatarNumero(novoValor);

        if (contador >= passos) {
            elemento.textContent = formatarNumero(valorFinal);
            clearInterval(interval);
        }
    }, duracao / passos);
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
        if (!podioEl) continue;

        if (ranking[i - 1]) {
            const vendedor = ranking[i - 1];
            const avatarEl = podioEl.querySelector('.podio-avatar');
            const nomeEl = podioEl.querySelector('.podio-nome');
            const nivelEl = podioEl.querySelector('.podio-nivel');
            const pontosValorEl = podioEl.querySelector('.pontos-valor');

            if (avatarEl) avatarEl.textContent = vendedor.avatar;
            if (nomeEl) nomeEl.textContent = vendedor.nome;
            if (nivelEl) nivelEl.textContent = `Nível ${vendedor.nivel}`;
            if (pontosValorEl) pontosValorEl.textContent = formatarNumero(vendedor.pontos_periodo);
        } else {
            const avatarEl = podioEl.querySelector('.podio-avatar');
            const nomeEl = podioEl.querySelector('.podio-nome');
            const pontosValorEl = podioEl.querySelector('.pontos-valor');

            if (avatarEl) avatarEl.textContent = '❓';
            if (nomeEl) nomeEl.textContent = '-';
            if (pontosValorEl) pontosValorEl.textContent = '0';
        }
    }

    // Atualiza ranking completo (a partir do 4º)
    const rankingList = document.getElementById('ranking-list');
    if (rankingList) {
        rankingList.innerHTML = '';

        if (ranking.length > 3) {
            for (let i = 3; i < ranking.length; i++) {
                const vendedor = ranking[i];
                const item = criarItemRanking(vendedor);
                rankingList.appendChild(item);
            }
        } else {
            rankingList.innerHTML = '<p style="text-align: center; color: #64748b; padding: 40px;">Nenhum vendedor além do top 3</p>';
        }
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
// CARREGAR VENDEDORES
// ================================

async function carregarVendedores() {
    const data = await fetchAPI('/vendedores');

    if (!data || !data.vendedores) return;

    vendedoresCache = data.vendedores;

    const grid = document.getElementById('vendedores-grid');
    if (!grid) return;

    grid.innerHTML = '';

    data.vendedores.forEach(vendedor => {
        const card = criarCardVendedor(vendedor);
        grid.appendChild(card);
    });
}

function criarCardVendedor(vendedor) {
    const div = document.createElement('div');
    div.className = 'vendedor-card fade-in';

    const badgesHTML = vendedor.badges && vendedor.badges.length > 0
        ? vendedor.badges.map(badge => `<span class="badge-mini" title="${badge}">${badge}</span>`).join('')
        : '<span style="color: #64748b; font-size: 12px;">Nenhuma conquista ainda</span>';

    div.innerHTML = `
        <div class="vendedor-header">
            <div class="vendedor-avatar-large">${vendedor.avatar}</div>
            <div class="vendedor-info">
                <div class="vendedor-nome">${vendedor.nome}</div>
                <div class="vendedor-nivel">Nível ${vendedor.nivel} - ${vendedor.nivel_nome}</div>
            </div>
        </div>
        <div class="vendedor-stats">
            <div class="stat-item">
                <div class="stat-value">${formatarNumero(vendedor.xp_total)}</div>
                <div class="stat-label">XP Total</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${vendedor.badges ? vendedor.badges.length : 0}</div>
                <div class="stat-label">Badges</div>
            </div>
        </div>
        <div class="vendedor-badges">
            ${badgesHTML}
        </div>
        <button class="btn btn-secondary btn-block" onclick="verDetalhesVendedor(${vendedor.id})">
            Ver Perfil Completo
        </button>
    `;

    return div;
}

function verDetalhesVendedor(id) {
    alert(`Funcionalidade de perfil detalhado será implementada em breve! (ID: ${id})`);
}

// ================================
// CARREGAR MISSÕES
// ================================

async function carregarMissoes() {
    const container = document.getElementById('missoes-container');
    if (!container) return;

    // Missões mockadas (depois virá da API)
    const missoes = [
        {
            id: 1,
            titulo: '🔥 Streak de 5 Dias',
            descricao: 'Bata sua meta diária por 5 dias consecutivos',
            recompensa: '100 XP',
            progresso: 3,
            total: 5,
            tipo: 'diaria'
        },
        {
            id: 2,
            titulo: '🎯 Triplo Hat Trick',
            descricao: 'Feche 3 vendas em um único dia',
            recompensa: '150 XP + Badge "Hat Trick"',
            progresso: 1,
            total: 3,
            tipo: 'desafio'
        },
        {
            id: 3,
            titulo: '📞 Maratonista de Leads',
            descricao: 'Alcance 200 leads em uma semana',
            recompensa: '200 XP',
            progresso: 87,
            total: 200,
            tipo: 'semanal'
        },
        {
            id: 4,
            titulo: '💎 Mestre das Entrevistas',
            descricao: 'Realize 50 entrevistas com taxa de conversão > 30%',
            recompensa: '300 XP + Badge "Interview Master"',
            progresso: 23,
            total: 50,
            tipo: 'desafio'
        }
    ];

    container.innerHTML = '';

    missoes.forEach(missao => {
        const card = criarCardMissao(missao);
        container.appendChild(card);
    });
}

function criarCardMissao(missao) {
    const div = document.createElement('div');
    div.className = `missao-card missao-${missao.tipo} fade-in`;

    const percentual = Math.round((missao.progresso / missao.total) * 100);

    div.innerHTML = `
        <div class="missao-header">
            <div class="missao-titulo">${missao.titulo}</div>
            <div class="missao-tipo">${missao.tipo}</div>
        </div>
        <div class="missao-descricao">${missao.descricao}</div>
        <div class="missao-progresso">
            <div class="progresso-info">
                <span>${missao.progresso} / ${missao.total}</span>
                <span>${percentual}%</span>
            </div>
            <div class="progresso-bar">
                <div class="progresso-fill" style="width: ${percentual}%"></div>
            </div>
        </div>
        <div class="missao-recompensa">
            <span class="recompensa-icon">🎁</span>
            <span>${missao.recompensa}</span>
        </div>
    `;

    return div;
}

// ================================
// COACH IA
// ================================

function preencherSelectVendedores() {
    const select = document.getElementById('coach-vendedor');
    if (!select || vendedoresCache.length === 0) return;

    // Remove opções existentes exceto a primeira
    select.innerHTML = '<option value="">Escolha...</option>';

    vendedoresCache.forEach(vendedor => {
        const option = document.createElement('option');
        option.value = vendedor.id;
        option.textContent = `${vendedor.nome} - Nível ${vendedor.nivel}`;
        select.appendChild(option);
    });
}

async function gerarMotivacao() {
    const select = document.getElementById('coach-vendedor');
    const vendedorId = select.value;

    if (!vendedorId) {
        alert('Por favor, selecione um vendedor primeiro!');
        return;
    }

    const resultDiv = document.getElementById('coach-result');
    resultDiv.innerHTML = '<p class="loading-text">⏳ Gerando mensagem motivacional...</p>';

    const data = await fetchAPI(`/coach/motivacao/${vendedorId}`);

    if (data && data.mensagem) {
        resultDiv.innerHTML = `
            <div class="mensagem-coach fade-in">
                <div class="mensagem-header">
                    <span class="mensagem-icon">☀️</span>
                    <span class="mensagem-tipo">Mensagem Matinal</span>
                </div>
                <div class="mensagem-conteudo">${data.mensagem.replace(/\n/g, '<br>')}</div>
            </div>
        `;
    } else {
        resultDiv.innerHTML = '<p class="error-text">❌ Erro ao gerar mensagem. Tente novamente.</p>';
    }
}

async function gerarAlerta() {
    const select = document.getElementById('coach-vendedor');
    const vendedorId = select.value;

    if (!vendedorId) {
        alert('Por favor, selecione um vendedor primeiro!');
        return;
    }

    const resultDiv = document.getElementById('coach-result');
    resultDiv.innerHTML = '<p class="loading-text">⏳ Gerando alerta de performance...</p>';

    const data = await fetchAPI(`/coach/alerta/${vendedorId}`);

    if (data && data.mensagem) {
        resultDiv.innerHTML = `
            <div class="mensagem-coach alerta fade-in">
                <div class="mensagem-header">
                    <span class="mensagem-icon">⚠️</span>
                    <span class="mensagem-tipo">Alerta de Performance</span>
                </div>
                <div class="mensagem-conteudo">${data.mensagem.replace(/\n/g, '<br>')}</div>
            </div>
        `;
    } else {
        resultDiv.innerHTML = '<p class="error-text">❌ Erro ao gerar mensagem. Tente novamente.</p>';
    }
}

async function gerarProvocacao() {
    const select = document.getElementById('coach-vendedor');
    const vendedorId = select.value;

    if (!vendedorId) {
        alert('Por favor, selecione um vendedor primeiro!');
        return;
    }

    const resultDiv = document.getElementById('coach-result');
    resultDiv.innerHTML = '<p class="loading-text">⏳ Gerando provocação...</p>';

    const data = await fetchAPI(`/coach/provocacao/${vendedorId}`);

    if (data && data.mensagem) {
        resultDiv.innerHTML = `
            <div class="mensagem-coach provocacao fade-in">
                <div class="mensagem-header">
                    <span class="mensagem-icon">🔥</span>
                    <span class="mensagem-tipo">Provocação</span>
                </div>
                <div class="mensagem-conteudo">${data.mensagem.replace(/\n/g, '<br>')}</div>
            </div>
        `;
    } else {
        resultDiv.innerHTML = '<p class="error-text">❌ Erro ao gerar mensagem. Tente novamente.</p>';
    }
}

async function gerarRelatorio() {
    const select = document.getElementById('coach-vendedor');
    const vendedorId = select.value;

    if (!vendedorId) {
        alert('Por favor, selecione um vendedor primeiro!');
        return;
    }

    const resultDiv = document.getElementById('coach-result');
    resultDiv.innerHTML = '<p class="loading-text">⏳ Gerando relatório noturno...</p>';

    const data = await fetchAPI(`/coach/relatorio/${vendedorId}`);

    if (data && data.mensagem) {
        resultDiv.innerHTML = `
            <div class="mensagem-coach relatorio fade-in">
                <div class="mensagem-header">
                    <span class="mensagem-icon">📊</span>
                    <span class="mensagem-tipo">Relatório Noturno</span>
                </div>
                <div class="mensagem-conteudo">${data.mensagem.replace(/\n/g, '<br>')}</div>
            </div>
        `;
    } else {
        resultDiv.innerHTML = '<p class="error-text">❌ Erro ao gerar mensagem. Tente novamente.</p>';
    }
}

// ================================
// ANÁLISE DE CONVERSAS
// ================================

async function preencherSelectAnalise() {
    const select = document.getElementById('analise-vendedor');

    if (vendedoresCache.length === 0) {
        vendedoresCache = await fetchAPI('/vendedores');
    }

    if (!vendedoresCache) return;

    select.innerHTML = '<option value="">Escolha...</option>';

    vendedoresCache.forEach(v => {
        const option = document.createElement('option');
        option.value = v.id;
        option.textContent = `${v.avatar} ${v.nome}`;
        select.appendChild(option);
    });

    // Listener para quando selecionar vendedor
    select.addEventListener('change', () => {
        const vendedorId = select.value;
        if (vendedorId) {
            carregarAnaliseVendedor(vendedorId);
        } else {
            document.getElementById('analise-container').innerHTML = '<p class="empty-state">Selecione um vendedor para ver a análise de qualidade.</p>';
        }
    });
}

async function carregarAnaliseVendedor(vendedorId) {
    const container = document.getElementById('analise-container');

    // Loading state
    container.innerHTML = '<p class="empty-state">⏳ Carregando análise...</p>';

    const data = await fetchAPI(`/analise/vendedor/${vendedorId}`);

    if (!data) {
        container.innerHTML = '<p class="empty-state">❌ Erro ao carregar análise. Tente novamente.</p>';
        return;
    }

    // Renderizar análise completa
    container.innerHTML = renderizarAnaliseCompleta(data);
}

function renderizarAnaliseCompleta(data) {
    const { vendedor, nota_media_conversas, total_conversas_analisadas, performance, conversas_recentes } = data;

    // Nota geral card
    const notaCard = `
        <div class="nota-card">
            <div class="nota-card-title">📊 Nota Média de Conversas</div>
            <div class="nota-valor">${nota_media_conversas.toFixed(1)}</div>
            <div class="nota-label">de 10.0</div>
            <div class="nota-detalhes">
                <div class="nota-item">
                    <div class="nota-item-label">Conversas</div>
                    <div class="nota-item-valor">${total_conversas_analisadas}</div>
                </div>
                <div class="nota-item">
                    <div class="nota-item-label">Vendedor</div>
                    <div class="nota-item-valor">${vendedor.avatar} ${vendedor.nome}</div>
                </div>
                <div class="nota-item">
                    <div class="nota-item-label">Nível</div>
                    <div class="nota-item-valor">${vendedor.nivel}</div>
                </div>
            </div>
        </div>
    `;

    // Performance cards
    let performanceCards = '';

    if (performance && Object.keys(performance).length > 0) {
        performanceCards = `
            <div class="performance-grid">
                ${renderizarPerformanceCard('📞 Leads', performance.leads)}
                ${renderizarPerformanceCard('🎯 Entrevistas', performance.entrevistas)}
                ${renderizarPerformanceCard('🔄 Conversões', performance.conversoes)}
                ${renderizarPerformanceCard('💰 Vendas', performance.vendas)}
            </div>
        `;
    }

    // Conversas recentes
    let conversasSection = '';

    if (conversas_recentes && conversas_recentes.length > 0) {
        const conversasList = conversas_recentes.map(conversa => renderizarConversaItem(conversa)).join('');

        conversasSection = `
            <div class="conversas-section">
                <div class="conversas-titulo">💬 Últimas Conversas Analisadas</div>
                <div class="conversas-list">
                    ${conversasList}
                </div>
            </div>
        `;
    } else {
        conversasSection = `
            <div class="conversas-section">
                <p class="empty-state">Nenhuma conversa analisada ainda.</p>
            </div>
        `;
    }

    return notaCard + performanceCards + conversasSection;
}

function renderizarPerformanceCard(titulo, data) {
    if (!data) return '';

    const { meta, atual, percentual } = data;

    // Determinar cor do percentual
    let classePercentual = 'red';
    if (percentual >= 100) classePercentual = 'green';
    else if (percentual >= 70) classePercentual = 'yellow';

    const progresso = Math.min(percentual, 100); // Cap em 100% visualmente

    return `
        <div class="performance-card">
            <div class="performance-header">
                <div class="performance-titulo">${titulo}</div>
                <div class="performance-percentual ${classePercentual}">${percentual}%</div>
            </div>
            <div class="performance-valores">
                <div class="performance-atual">${formatarNumero(atual)}</div>
                <div class="performance-meta">Meta: ${formatarNumero(meta)}</div>
            </div>
            <div class="performance-bar">
                <div class="performance-bar-fill" style="width: ${progresso}%"></div>
            </div>
        </div>
    `;
}

function renderizarConversaItem(conversa) {
    const { cliente_nome, tipo_conversa, nota_geral, resultado, data_conversa, duracao_segundos } = conversa;

    // Classificar nota
    let scoreClass = 'poor';
    if (nota_geral >= 8.5) scoreClass = 'excellent';
    else if (nota_geral >= 7.0) scoreClass = 'good';
    else if (nota_geral >= 5.5) scoreClass = 'average';

    // Classificar resultado
    const resultadoMap = {
        'venda_fechada': '💰 Venda Fechada',
        'agendamento': '📅 Agendamento',
        'interesse': '🤔 Interesse',
        'sem_interesse': '❌ Sem Interesse',
        'perdido': '❌ Perdido'
    };

    const resultadoTexto = resultadoMap[resultado] || resultado;

    // Formatar data
    const dataObj = new Date(data_conversa);
    const dataFormatada = dataObj.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });

    // Ícone tipo conversa
    const tipoIcon = tipo_conversa === 'whatsapp' ? '💬' : '📞';

    // Duração (se houver)
    let duracaoTexto = '';
    if (duracao_segundos) {
        const minutos = Math.floor(duracao_segundos / 60);
        const segundos = duracao_segundos % 60;
        duracaoTexto = `⏱️ ${minutos}:${segundos.toString().padStart(2, '0')}`;
    }

    return `
        <div class="conversa-item">
            <div class="conversa-header">
                <div class="conversa-cliente">${cliente_nome}</div>
                <div class="conversa-score ${scoreClass}">${nota_geral.toFixed(1)}/10</div>
            </div>
            <div class="conversa-info">
                <div class="conversa-tipo">${tipoIcon} ${tipo_conversa}</div>
                <div class="conversa-data">📅 ${dataFormatada}</div>
                ${duracaoTexto ? `<div class="conversa-duracao">${duracaoTexto}</div>` : ''}
                <div class="conversa-resultado ${resultado}">${resultadoTexto}</div>
            </div>
        </div>
    `;
}

// ================================
// INICIALIZAÇÃO
// ================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎮 SalesQuest carregando...');

    // Carrega dados iniciais
    await Promise.all([
        carregarStatsGerais(),
        carregarRanking('dia'),
        carregarVendedores()
    ]);

    // Configura navegação e tabs
    configurarNavegacao();
    configurarTabs();

    // Esconde loading screen
    esconderLoading();

    console.log('✅ SalesQuest pronto!');

    // Atualiza a cada 30 segundos
    setInterval(() => {
        carregarStatsGerais();

        // Pega período ativo e recarrega ranking
        const periodoTab = document.querySelector('.periodo-tab.active');
        if (periodoTab) {
            const periodoAtivo = periodoTab.dataset.periodo;
            carregarRanking(periodoAtivo);
        }
    }, 30000);
});
